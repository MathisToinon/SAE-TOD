import zipfile
import os
import tempfile
import chardet
import pandas as pd
import requests
from io import BytesIO
import io

class Processor:
    def __init__(self, zip_path):
        self.zip_path = zip_path
        self.extracted_path = None
        self.gaz = "pas encore crée - lancer la methode process"
        self.electricite = "pas encore crée - lancer la methode process"
        self.chaleur = "pas encore crée - lancer la methode process"
        self.naf2 = self.init_naf_2()
        self.iris = self.init_iris()

    def _detect_encoding(self, filepath, n_bytes=10000):
        with open(filepath, "rb") as f:
            raw = f.read(n_bytes)
            result = chardet.detect(raw)
            return result['encoding']

    def _load_csv(self, filepath):
        encoding = self._detect_encoding(filepath)
        filename = os.path.basename(filepath)
        try:
            df = pd.read_csv(
                filepath,
                encoding=encoding,
                skiprows=1,
                sep=';',
                decimal='.',
                na_values=['nd', 'secret']
            )
            print(f"✅ Lecture réussie — {filename}")
            return  df,filename
        except Exception as e:
            print(f"❌ Erreur de lecture de {filename} : {e}")

    def traitement_unique(self, df, nom):
        if "chaleur" in nom :
            self.traitement_chaleur(df, nom)
        if "electricite" in nom :
            self.traitement_elec(df, nom)
        if "gaz-naturel" in nom : 
            self.traitement_gaz(df, nom)

    def traitement_elec(self, df, nom ) : 
        df.drop(columns=["CORRECTION_CODE_IRIS","NOM_COMMUNE","CODE_EIC","THERMOR", "PART","IRIS_LIBELLE","CODE_IRIS_LIBELLE","CODE_SECTEUR_NAF2_LIBELLE"], inplace=True, errors='ignore')
        if "CODE_SECTEUR_NAF2_CODE" in df.columns:
            df.rename(columns={"CODE_SECTEUR_NAF2_CODE": "CODE_SECTEUR_NAF2"}, inplace=True)
        if "CODE_IRIS" in df.columns:
            df.rename(columns={"CODE_IRIS": "IRIS_CODE"}, inplace=True)
        if "IRIS" in df.columns:
            df.rename(columns={"IRIS": "IRIS_CODE"}, inplace=True)
        if "CODE_IRIS_CODE" in df.columns:
            df.rename(columns={"CODE_IRIS_CODE": "IRIS_CODE"}, inplace=True)

        df['CODE_SECTEUR_NAF2'] = df['CODE_SECTEUR_NAF2'].astype('Int64')  
        df["CODE_SECTEUR_NAF2"] = df["CODE_SECTEUR_NAF2"].astype('string')
     

        if type(self.electricite) is not str : 
            self.electricite = pd.concat([self.electricite,df], ignore_index=True)
        else : self.electricite = df


    def traitement_gaz(self, df, nom ) : 
        df.drop(columns=["CODE_EIC","CODE_SECTEUR_NAF2_LIBELLE","IRIS_LIBELLE","CODE_IRIS_LIBELLE","CORRECTION_CODE_IRIS","THERMOR","PART","NOM_COMMUNE"], inplace=True, errors='ignore')
        if "CODE_SECTEUR_NAF2_CODE" in df.columns:
            df.rename(columns={"CODE_SECTEUR_NAF2_CODE": "CODE_SECTEUR_NAF2"}, inplace=True)
        if "CODE_IRIS" in df.columns:
            df.rename(columns={"CODE_IRIS": "IRIS_CODE"}, inplace=True)
        if "CODE_IRIS_CODE" in df.columns:
            df.rename(columns={"CODE_IRIS_CODE": "IRIS_CODE"}, inplace=True)

        df['CODE_SECTEUR_NAF2'] = df['CODE_SECTEUR_NAF2'].astype('Int64') 
        df["CODE_SECTEUR_NAF2"] = df["CODE_SECTEUR_NAF2"].astype("string")


        if type(self.gaz) is not str : 
            self.gaz = pd.concat([self.gaz,df], ignore_index=True)
        else : self.gaz = df

    def traitement_chaleur(self, df, nom ) : 
        df.drop(columns=["ID",'IRIS_LIBELLE'], inplace=True, errors='ignore')
        if "IRIS" in df.columns:
            df.rename(columns={"IRIS": "IRIS_CODE"}, inplace=True)
        if type(self.chaleur) is not str : 
            self.chaleur = pd.concat([self.chaleur,df], ignore_index=True)
        else : self.chaleur = df


    def init_naf_2(self):
        url = "https://www.insee.fr/fr/statistiques/fichier/2120875/int_courts_naf_rev_2.xls"

        response = requests.get(url)
        xls_data = BytesIO(response.content)

        df = pd.read_excel(xls_data, engine="xlrd")
        df = df.iloc[:, [1, 2]]
        df.columns = ["CODE","LIBELLE"]

        df_filtered = df[df['CODE'].astype(str).str.match(r'^[0-9]{2}$')]

        df_filtered['CODE'] = df_filtered['CODE'].astype('Int64') 

        nouvelle_ligne = pd.DataFrame([{"CODE": pd.NA, "LIBELLE": "Non renseigné"}])

        # Ajout de la ligne
        df_filtered = pd.concat([df_filtered, nouvelle_ligne], ignore_index=True)  
        df_filtered["CODE"] = df_filtered["CODE"].astype("string")


        return df_filtered

    def init_iris(self):
        url = "https://www.insee.fr/fr/statistiques/fichier/7708995/reference_IRIS_geo2024.zip"

        response = requests.get(url)
        zip_bytes = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_bytes) as z:
            excel_file_name = z.namelist()[0]  
            with z.open(excel_file_name) as f:
                df = pd.read_excel(f, skiprows=5)
        
        return df 
        
        


    def process(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.extracted_path = tmpdirname

            # Extraction des fichiers
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)
                print(f"✅ ZIP extrait dans : {tmpdirname}")

            # Parcours des fichiers CSV extraits
            for root, _, files in os.walk(tmpdirname):
                for name in files:
                    if name.lower().endswith(".csv"):
                        csv_path = os.path.join(root, name)
                        res_df, res_nom = self._load_csv(csv_path)
                        self.traitement_unique(res_df,res_nom)


if __name__ == "__main__":
    zip_path = "donnees.zip"
    processor = Processor(zip_path)
    processor.process()
    print(len(processor.electricite))
    print(processor.naf2["CODE"])
