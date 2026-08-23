@echo off
echo Запуск локального сервера для обхода защиты CORS...
start http://localhost:8000/configurator_work.html
python -m http.server 8000
pause
