@echo off
REM Aller dans le dossier du projet (modifie ce chemin si nécessaire)
cd /d "C:\chemin\vers\ton\projet"

REM Activer l'environnement virtuel nommé .venv
call venv\Scripts\activate.bat

REM Lancer le serveur Django dans une nouvelle fenêtre de commande
start cmd /k "python manage.py runserver"

REM Attendre quelques secondes pour le démarrage du serveur
timeout /t 3 > nul

REM Ouvrir le navigateur sur l'URL locale
start http://127.0.0.1:8000/
