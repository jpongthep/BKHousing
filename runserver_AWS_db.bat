@echo off
echo ========================================
echo Run Server With AWS DB + LAN Network
echo ========================================
call env/Scripts/Activate.bat
python manage.py runserver 0.0.0.0:8000 --settings=Housing.production