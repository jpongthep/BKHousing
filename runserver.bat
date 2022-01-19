@echo off
echo ========================================
echo Activate Virtual Environment env 
echo ========================================
call env/Scripts/Activate.bat
python manage.py runserver 0.0.0.0:8000