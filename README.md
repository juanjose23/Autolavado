
# Lavacar ASOCATIE

El proyecto Lavacar ASOCATIE es una completa solución de gestión administrativa diseñada para empresas de lavado de autos. Está destinado a simplificar y optimizar las operaciones diarias, desde la gestión de clientes y colaboradores hasta el seguimiento de servicios, precios y ventas. La integración de datos del negocio proporciona una visión holística, permitiendo tomar decisiones informadas y mejorar la eficiencia operativa.

Características Principales:

Gestión de Clientes:

Agregar, editar y eliminar información de clientes.
Registro histórico de servicios solicitados por cada cliente.
Gestión de Colaboradores:

Administrar perfiles de colaboradores.
Seguimiento de horarios, desempeño y asignación de tareas.
Servicios y Precios:

Mantener un catálogo actualizado de servicios ofrecidos.
Historial de cambios en los precios de los servicios.
Ventas y Facturación:

Registro de transacciones y ventas.
Facturación automática y generación de informes financieros.
Historial de Precios:

Seguimiento detallado de la evolución de los precios.
Registro de fechas efectivas de cambios en los precios.
Gestión de Horarios:

Programación y seguimiento de horarios de trabajo.
Integración con la disponibilidad de colaboradores.
Integración de Datos del Negocio:

Consolidación de datos para informes holísticos.
Análisis de rendimiento y toma de decisiones basada en datos.
## Descargas necesarias para el proyecto

 - [Descargar el gestor de base de datos postgresql](https://awesomeopensource.com/project/elangosundar/awesome-README-templates)
 - [Descargar python version 3.10](https://github.com/matiassingers/awesome-readme)
 - [Descarga wkhtmltopdf](https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project)

## Configuración con Variables de Entorno

Para ejecutar este proyecto, necesitarás configurar algunas variables de entorno en tu entorno de desarrollo. Estas variables son cruciales para el funcionamiento adecuado del sistema y contienen información sensible o específica del entorno. A continuación, se describe cada variable de entorno necesaria y su propósito:

## `DATABASE_URL`

- **Descripción:** Esta variable de entorno especifica la URL de conexión a la base de datos PostgreSQL.
- **Ejemplo:**
  ```bash
  export DATABASE_URL="postgresql://postgres:123456@localhost:5432/Autolavado"
## `SERVER_EMAIL`
- **Descripción:** Indica la dirección del servidor de correo electrónico utilizado para enviar mensajes desde la aplicación.
- **Ejemplo:**
    ```bash
    export SERVER_EMAIL="smtp.gmail.com"

## `port`
- **Descripción:**  Especifica el puerto que utilizará el servidor de correo electrónico para la conexión.
- **Ejemplo:**
     ```bash
        export port="587"
 ## `correo`
- **Descripción:**  Esta variable almacena la dirección de correo electrónico que se utilizará para enviar mensajes desde la aplicación.
- **Ejemplo:**
     ```bash
        export correo="ejemplo@gmail.com"

## `clave`
- **Descripción:** Contiene la contraseña asociada a la cuenta de correo electrónico utilizada para enviar mensajes desde la aplicación.
- **Ejemplo:**
     ```bash
        export clave="12345678"
## `FLASK_APP`
- **Descripción:** Especifica el archivo principal de la aplicación Flask que se debe ejecutar.
- **Ejemplo:**
     ```bash
        export FLASK_APP=app.py
## `FLASK_DEBUG`
- **Descripción:** Activa el modo de depuración en Flask para facilitar el desarrollo.
- **Ejemplo:**
     ```bash
        export FLASK_DEBUG=1
Este fragmento de README explica cada variable de entorno y proporciona ejemplos para que los usuarios puedan configurarlas correctamente antes de ejecutar la aplicación.

## Ejecutar Localmente

1. Clonar el Proyecto:

```bash
 https://github.com/juanjose23/Autolavado.git
```

2. Ir al Directorio del Proyecto:



```bash
  cd Autolavado
```

3. Instalar Dependencias:

```bash
  pip install -r requirements.txt

```

4. Configurar Variables de Entorno:

Asegúrate de configurar las variables de entorno antes de iniciar la aplicación.

5. Iniciar el Servidor:
```bash
 flask run
```
6. Acceder a la Aplicación:

Visita http://localhost:5000 en tu navegador para explorar la aplicación.

¡Listo! Ahora el proyecto de Autolavado debería estar funcionando localmente. 