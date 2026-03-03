@echo off
cd /d "c:\Users\IDEP\Desktop\TESTE_SUAP_IDEP2"
powershell.exe -NoExit -NoProfile -ExecutionPolicy Bypass -Command "python manage.py runserver 0.0.0.0:8010 --noreload"
