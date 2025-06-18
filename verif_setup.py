# verif_donnees.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet_pinguin.settings")
django.setup()

from app_pinguin.models import Naf2, Iris, Electricite, Gaz, Chaleur

print("=== Vérification des données ===")

print(f"🧾 NAF2 : {Naf2.objects.count()} lignes")
print(f"📍 IRIS : {Iris.objects.count()} lignes")
print(f"⚡ Electricité : {Electricite.objects.count()} lignes")
print(f"🔥 Gaz : {Gaz.objects.count()} lignes")
print(f"🌡️ Chaleur : {Chaleur.objects.count()} lignes")

# Relations vérifiées
nb_elecs_invalides = Electricite.objects.filter(IRIS_CODE__isnull=True).count()
nb_gaz_invalides = Gaz.objects.filter(IRIS_CODE__isnull=True).count()
nb_chaleur_invalides = Chaleur.objects.filter(IRIS_CODE__isnull=True).count()

print(f"⚠️ Electricité sans IRIS lié : {nb_elecs_invalides}")
print(f"⚠️ Gaz sans IRIS lié : {nb_gaz_invalides}")
print(f"⚠️ Chaleur sans IRIS lié : {nb_chaleur_invalides}")

nb_naf2_invalides = Electricite.objects.filter(CODE_SECTEUR_NAF2__isnull=True).count()
print(f"⚠️ Electricité sans NAF2 lié : {nb_naf2_invalides}")

print("✅ Vérification terminée.")
