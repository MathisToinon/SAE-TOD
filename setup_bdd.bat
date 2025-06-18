@echo off
REM Lire les variables depuis le fichier .env
for /f "tokens=1,* delims==" %%A in (.env) do (
    set %%A=%%B
)

:: Demander le chemin vers psql.exe
::set /p PSQL_PATH="Entrez le chemin complet vers psql.exe (ex: C:\Program Files\PostgreSQL\15\bin\psql.exe) : "
set PSQL_PATH="C:\Program Files\PostgreSQL\17\bin\psql.exe"
:: Vérifier que le fichier existe
@REM if not exist "!PSQL_PATH!" (
@REM     echo Le fichier !PSQL_PATH! est introuvable.
@REM     pause
@REM     exit /b
@REM )

echo 🔧 Création de la base de données PostgreSQL...
echo  %USER%
%PSQL_PATH% -U postgres -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';"
%PSQL_PATH% -U postgres -c "CREATE DATABASE %DB_NAME% OWNER %DB_USER%;"
%PSQL_PATH% -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"

echo ✅ Base et utilisateur PostgreSQL créés.

REM Activer l’environnement virtuel si besoin
REM call venv\Scripts\activate

echo ⚙️ Lancement des migrations Django...
python manage.py makemigrations
python manage.py migrate

echo 📦 Insertion des données via la commande Django personnalisée...
python manage.py insert_data ..\donnees.zip

echo verification des insertions
python .\verif_setup.py

echo ✅ Script d'installation terminé.
pause
