from django.core.management.base import BaseCommand
from app_pinguin.models import Gaz, Electricite, Naf2, Iris, Chaleur
from app_pinguin.management.commands.traitement import Processor


class Command(BaseCommand):
    help = "Insère des données depuis un fichier .zip contenant les DataFrames"

    def add_arguments(self, parser):
        parser.add_argument(
            "zip_path",
            type=str,
            help="Chemin du fichier .zip contenant les fichiers de données",
        )

    def handle(self, *args, **kwargs):
        zip_path = kwargs["zip_path"]
        processor = Processor(zip_path)
        processor.process()
        processor.naf2["CODE"] = processor.naf2["CODE"].astype(str).str.strip()
        processor.iris["CODE_IRIS"] = processor.iris["CODE_IRIS"].astype(str).str.strip()
        processor.electricite["IRIS_CODE"] = processor.electricite["IRIS_CODE"].astype(str).str.strip()
        processor.electricite["CODE_SECTEUR_NAF2"] = processor.electricite["CODE_SECTEUR_NAF2"].astype(str).str.strip()


        # === NAF2 ===
        self.stdout.write("Insertion des données NAF2...")
        Naf2.objects.bulk_create(
            [
                Naf2(CODE=row["CODE"], LIBELLE=row["LIBELLE"])
                for _, row in processor.naf2.iterrows()
            ],
            ignore_conflicts=True,
        )
        self.stdout.write("finish")

        # === IRIS ===
        self.stdout.write("Insertion des données IRIS...")
        Iris.objects.bulk_create(
            [
                Iris(
                    CODE_IRIS=row["CODE_IRIS"],
                    LIB_IRIS=row["LIB_IRIS"],
                    TYP_IRIS=row["TYP_IRIS"],
                    GRD_QUART=row["GRD_QUART"],
                    DEPCOM=row["DEPCOM"],
                    LIBCOM=row["LIBCOM"],
                    UU2020=row["UU2020"],
                    REG=row["REG"],
                    DEP=row["DEP"],
                )
                for _, row in processor.iris.iterrows()
            ],
            ignore_conflicts=True,
        )
        self.stdout.write("finish")

        self.stdout.write("Insertion des données ELECTRICITE...")
        # Préparer dictionnaires pour les FK (plus rapide)
        iris_map = {
            iris.CODE_IRIS: iris for iris in Iris.objects.all()
        }
        naf2_map = {
            naf.CODE: naf for naf in Naf2.objects.all()
        }

        # Précharger les ForeignKey en dictionnaires
        iris_map = {obj.CODE_IRIS: obj for obj in Iris.objects.all()}
        naf_map = {obj.CODE: obj for obj in Naf2.objects.all()}

        # --------------------------
        # Insertions des ELECTRICITE
        # --------------------------
        electricites = []
        missing_iris, missing_naf = 0, 0

        for _, row in processor.electricite.iterrows():
            iris = iris_map.get(row["IRIS_CODE"])
            naf = naf_map.get(row["CODE_SECTEUR_NAF2"])

            if not iris:
                missing_iris += 1
                continue
            if not naf:
                missing_naf += 1
                continue

            electricites.append(Electricite(
                OPERATEUR=row["OPERATEUR"],
                ANNEE=row["ANNEE"],
                FILIERE=row["FILIERE"],
                IRIS_CODE=iris,
                CODE_CATEGORIE_CONSOMMATION=row["CODE_CATEGORIE_CONSOMMATION"],
                CODE_SECTEUR_NAF2=naf,
                CODE_GRAND_SECTEUR=row["CODE_GRAND_SECTEUR"],
                CONSO=row["CONSO"],
                PDL=row["PDL"],
                INDQUAL=row["INDQUAL"]
            ))

        Electricite.objects.bulk_create(electricites)
        self.stdout.write(f"Electricité : {len(electricites)} lignes insérées.")
        self.stdout.write(f"Electricité : {missing_iris} lignes ignorées (IRIS manquant), {missing_naf} (NAF2 manquant).")
        self.stdout.write("finish")
        
        
        
        # --------------------------
        # Insertions des GAZ
        # --------------------------
        self.stdout.write("Insertion des données GAZ...")
        gazs = []
        missing_iris, missing_naf = 0, 0

        for _, row in processor.gaz.iterrows():
            iris = iris_map.get(row["IRIS_CODE"])
            naf = naf_map.get(row["CODE_SECTEUR_NAF2"])

            if not iris:
                missing_iris += 1
                continue
            if not naf:
                missing_naf += 1
                continue

            gazs.append(Gaz(
                OPERATEUR=row["OPERATEUR"],
                ANNEE=row["ANNEE"],
                FILIERE=row["FILIERE"],
                IRIS_CODE=iris,
                CODE_CATEGORIE_CONSOMMATION=row["CODE_CATEGORIE_CONSOMMATION"],
                CODE_SECTEUR_NAF2=naf,
                CONSO=row["CONSO"],
                PDL=row["PDL"],
                INDQUAL=row["INDQUAL"]
            ))
        self.stdout.write("finish")
        Gaz.objects.bulk_create(gazs)
        self.stdout.write(f"Gaz : {len(gazs)} lignes insérées.")
        self.stdout.write(f"Gaz : {missing_iris} lignes ignorées (IRIS manquant), {missing_naf} (NAF2 manquant).")
        
        
        # === CHALEUR ===
        self.stdout.write("Insertion des données CHALEUR...")
        Chaleur.objects.bulk_create(
            [
                Chaleur(
                    OPERATEUR=row["OPERATEUR"],
                    ANNEE=row["ANNEE"],
                    FILIERE=row["FILIERE"],
                    IRIS_CODE=iris_map.get(row["IRIS_CODE"]),
                    CONSO=row["CONSO"],
                    PDL=row["PDL"],
                )
                for _, row in processor.chaleur.iterrows()
                if row["IRIS_CODE"] in iris_map
            ]
        )
        self.stdout.write("finish")
        self.stdout.write(self.style.SUCCESS("✅ Données insérées avec succès."))
