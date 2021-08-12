@echo off
echo ========================================
echo Activate Virtual Environment env 
echo ========================================
d:/xampp/xampp_start
pause 
call env/Scripts/Activate.bat
python manage.py runserver