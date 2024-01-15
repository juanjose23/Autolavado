@echo off

rem Cambiar al directorio de tu aplicación Flask (ajusta la ruta según tu estructura)
cd C:\Users\jrios\OneDrive\Escritorio\Autolavado

rem Activar el entorno virtual
call env\Scripts\activate
rem Instalar los requisitos
pip install -r requirements.txt
rem Ejecutar Flask
flask run --host=0.0.0.0 --port=5000

rem Desactivar el entorno virtual al finalizar
deactivate
