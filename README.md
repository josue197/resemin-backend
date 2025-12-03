
# Plataforma de Consulta (Django + PostgreSQL)

Este proyecto permite:

1. **Subir un archivo Excel** desde el panel de administración.
2. **Detectar automáticamente todas las columnas** y cargarlas como registros JSON.
3. **Elegir en el admin** qué columna es **DNI** y cuál es **Fecha de ingreso**, y **qué columnas serán visibles** para las consultas públicas.
4. **API** que recibe `dni` y `fecha` y devuelve **solo las columnas visibles**.

## Requisitos
- Python 3.10+
- PostgreSQL 13+ (pgAdmin 4 para administración)

## Instalación (Windows)
1. **Descomprime** el ZIP en `C:\plataforma`.
2. Abre `CMD` o `PowerShell` en `C:\plataforma`.
3. Crea y activa entorno virtual:
   ```bat
   python -m venv venv
   venv\Scriptsctivate
   ```
4. Instala dependencias:
   ```bat
   pip install -r requirements.txt
   ```
5. Configura tu base de datos en `plataforma/settings.py` (sección `DATABASES`).
6. Aplica migraciones y crea superusuario:
   ```bat
   python manage.py makemigrations consulta
   python manage.py migrate
   python manage.py createsuperuser
   ```
7. Ejecuta el servidor:
   ```bat
   python manage.py runserver
   ```
8. Entra al **admin**: `http://127.0.0.1:8000/admin/`
   - **Sube el Excel** (`ArchivoExcel`).
   - En el detalle del archivo, marca **una columna** como `es_dni` y **una columna** como `es_fecha_ingreso`.
   - Marca/desmarca `visible` en cada columna.
   - Deja `activo=True` en el Excel que quieres usar.

## Endpoints
- `GET /api/consulta/?dni=12345678&fecha=01/01/2020`
- `GET /api/columnas/` → útil para tu frontend: devuelve columnas visibles, todas, y los campos configurados de DNI/fecha.

## Notas
- El import convierte todos los valores a **texto** para simplificar coincidencias.
- La fecha aceptada por la API puede venir como `dd/mm/yyyy` o `yyyy-mm-dd`.
- Si subes un nuevo Excel y lo marcas **activo**, los anteriores quedan **inactivos** automáticamente.

## CORS
Si tu frontend está en Netlify (por ejemplo `https://resemin.netlify.app`), ya está en `CORS_ALLOWED_ORIGINS`. Cambia/añade dominios si es necesario.
