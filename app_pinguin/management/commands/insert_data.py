# FICHIER : app_pinguin/management/commands/insert_data.py

from django.core.management.base import BaseCommand
from app_pinguin.models import Gaz, Electricite, Naf2, Iris, Chaleur
from app_pinguin.management.commands.traitement import Processor
from django.db import connection
from tqdm import tqdm

BATCH_SIZE = 5000

class Command(BaseCommand):
    help = "Insère des données depuis un fichier .zip contenant les DataFrames traités"

    def add_arguments(self, parser):
        parser.add_argument("zip_path", type=str, help="Chemin vers le fichier .zip")

    def handle(self, *args, **kwargs):
        zip_path = kwargs["zip_path"]
        processor = Processor(zip_path)
        processor.process()

        # Nettoyage des clés
        processor.naf2["CODE"] = processor.naf2["CODE"].astype(str).str.strip()
        processor.iris["CODE_IRIS"] = processor.iris["CODE_IRIS"].astype(str).str.strip()
        processor.electricite["IRIS_CODE"] = processor.electricite["IRIS_CODE"].astype(str).str.strip()
        processor.electricite["CODE_SECTEUR_NAF2"] = processor.electricite["CODE_SECTEUR_NAF2"].astype(str).str.strip()

        self.disable_constraints()

        try:
            # Insertion Naf2 et Iris
            self.stdout.write("🔄 Insertion Naf2...")
            Naf2.objects.bulk_create([
                Naf2(CODE=row["CODE"], LIBELLE=row["LIBELLE"])
                for _, row in processor.naf2.iterrows()
            ], ignore_conflicts=True, batch_size=BATCH_SIZE)

            self.stdout.write("🔄 Insertion Iris...")
            Iris.objects.bulk_create([
                Iris(**row.to_dict())
                for _, row in processor.iris.iterrows()
            ], ignore_conflicts=True, batch_size=BATCH_SIZE)

            iris_map = {obj.CODE_IRIS: obj for obj in Iris.objects.all()}
            naf_map = {obj.CODE: obj for obj in Naf2.objects.all()}

            self.bulk_insert_energy(processor.electricite, Electricite, iris_map, naf_map)

            self.bulk_insert_energy(processor.gaz, Gaz, iris_map, naf_map)

            self.stdout.write("🔄 Insertion Chaleur...")
            chaleurs = [
                Chaleur(
                    OPERATEUR=row["OPERATEUR"],
                    ANNEE=row["ANNEE"],
                    FILIERE=row["FILIERE"],
                    IRIS_CODE=iris_map.get(row["IRIS_CODE"]),
                    CONSO=row["CONSO"],
                    PDL=row["PDL"]
                )
                for _, row in tqdm(processor.chaleur.iterrows(), total=len(processor.chaleur), desc="Chaleur")
                if row["IRIS_CODE"] in iris_map
            ]
            Chaleur.objects.bulk_create(chaleurs, batch_size=BATCH_SIZE)
            self.stdout.write(f"✅ Chaleur : {len(chaleurs)} lignes insérées.")

        finally:
            self.enable_constraints()
            self.stdout.write(self.style.SUCCESS("✅ Import terminé avec succès."))

    def bulk_insert_energy(self, df, model, iris_map, naf_map):
        buffer = []
        total_inserted, missing_iris, missing_naf = 0, 0, 0

        self.stdout.write(f"📆 Insertion {model.__name__} avec barre de progression...")

        for _, row in tqdm(df.iterrows(), total=len(df), desc=model.__name__):
            iris = iris_map.get(row["IRIS_CODE"])
            naf = naf_map.get(row.get("CODE_SECTEUR_NAF2")) if "CODE_SECTEUR_NAF2" in row else None

            if not iris:
                missing_iris += 1
            if "CODE_SECTEUR_NAF2" in row and not naf:
                missing_naf += 1

            obj_kwargs = {
                "OPERATEUR": row["OPERATEUR"],
                "ANNEE": row["ANNEE"],
                "FILIERE": row["FILIERE"],
                "IRIS_CODE": iris,
                "CONSO": row["CONSO"],
                "PDL": row["PDL"]
            }
            if "INDQUAL" in df.columns:
                obj_kwargs["INDQUAL"] = row["INDQUAL"]
            if "CODE_CATEGORIE_CONSOMMATION" in df.columns:
                obj_kwargs["CODE_CATEGORIE_CONSOMMATION"] = row["CODE_CATEGORIE_CONSOMMATION"]
            if "CODE_GRAND_SECTEUR" in df.columns and hasattr(model, "CODE_GRAND_SECTEUR"):
                obj_kwargs["CODE_GRAND_SECTEUR"] = row["CODE_GRAND_SECTEUR"]
            if "CODE_SECTEUR_NAF2" in df.columns and hasattr(model, "CODE_SECTEUR_NAF2"):
                obj_kwargs["CODE_SECTEUR_NAF2"] = naf

            buffer.append(model(**obj_kwargs))

            if len(buffer) >= BATCH_SIZE:
                model.objects.bulk_create(buffer, batch_size=BATCH_SIZE)
                total_inserted += len(buffer)
                buffer = []

        if buffer:
            model.objects.bulk_create(buffer, batch_size=BATCH_SIZE)
            total_inserted += len(buffer)

        self.stdout.write(f"✅ {model.__name__} : {total_inserted} lignes insérées.")
        self.stdout.write(f"ℹ️ {model.__name__} : {missing_iris} IRIS manquants, {missing_naf} NAF2 manquants.")

    def verifier_coherence_fk(self, df, model):
        self.stdout.write(f"🔍 Vérification des FK pour {model.__name__}...")

        iris_valid = set(Iris.objects.values_list("CODE_IRIS", flat=True))
        naf_valid = set(Naf2.objects.values_list("CODE", flat=True))

        df_iris = set(df["IRIS_CODE"].dropna().astype(str).str.strip())
        df_naf = set(df["CODE_SECTEUR_NAF2"].dropna().astype(str).str.strip()) if "CODE_SECTEUR_NAF2" in df.columns else set()

        iris_missing = df_iris - iris_valid
        naf_missing = df_naf - naf_valid

        if iris_missing:
            self.stdout.write(self.style.WARNING(f"⚠️ {len(iris_missing)} IRIS_CODE non trouvés :"))
            for code in list(iris_missing)[:5]:
                self.stdout.write(f"  - {code}")
            if len(iris_missing) > 5:
                self.stdout.write("  ...")

        if naf_missing:
            self.stdout.write(self.style.WARNING(f"⚠️ {len(naf_missing)} CODE_SECTEUR_NAF2 non trouvés :"))
            for code in list(naf_missing)[:5]:
                self.stdout.write(f"  - {code}")
            if len(naf_missing) > 5:
                self.stdout.write("  ...")

        if not iris_missing and not naf_missing:
            self.stdout.write(self.style.SUCCESS("✅ Toutes les FK sont valides."))

        return len(iris_missing) == 0 and len(naf_missing) == 0

    def disable_constraints(self):
        with connection.cursor() as cursor:
            for table in ["app_pinguin_electricite", "app_pinguin_gaz", "app_pinguin_chaleur"]:
                cursor.execute(f"ALTER TABLE {table} DISABLE TRIGGER USER;")
            self.stdout.write("🚫 Triggers utilisateur désactivés.")

    def enable_constraints(self):
        with connection.cursor() as cursor:
            for table in ["app_pinguin_electricite", "app_pinguin_gaz", "app_pinguin_chaleur"]:
                cursor.execute(f"ALTER TABLE {table} ENABLE TRIGGER USER;")
            self.stdout.write("✅ Triggers utilisateur réactivés.")
