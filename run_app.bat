@echo off

rem Cambiar al directorio de tu aplicación Flask (ajusta la ruta según tu estructura)
cd C:\Users\jrios\OneDrive\Escritorio\Autolavado

rem Activar el entorno virtual
call env\Scripts\activate

rem Ejecutar Flask
flask run

rem Desactivar el entorno virtual al finalizar
deactivate
