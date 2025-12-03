
import os
from pathlib import Path
import dj_database_url

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Seguridad / Entorno ===
# Define estos en Render (Environment → Add Environment Variable)
SECRET_KEY = os.getenv('SECRET_KEY', 'inseguro-solo-dev')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Acepta una lista separada por comas
ALLOWED_HOSTS = [h.strip() for h in os.getenv(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,resemin-backend.onrender.com'
).split(',') if h.strip()]

# === Apps ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'consulta',              # app principal
    # 'corsheaders',         # si expones API pública y necesitas CORS, descomenta y config abajo
]

# === Middleware ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # estáticos en producción
    # 'corsheaders.middleware.CorsMiddleware',      # habilitar si usas corsheaders
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'plataforma.urls'

# === Templates ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # p.ej. BASE_DIR/templates/panel/dashboard.html
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'plataforma.wsgi.application'

# === Base de datos ===
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv(
            'DATABASE_URL',
            'postgres://usuario:password@localhost:5432/db_local'
        ),
        conn_max_age=600,
        ssl_require=not DEBUG,   # En Render debe ser True (producción)
    )
}

# === Archivos estáticos ===
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Si tienes carpeta local de estáticos:
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# === Archivos media (si los usas) ===
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# === CSRF / Hosts confiables ===
CSRF_TRUSTED_ORIGINS = [
    'https://resemin-backend.onrender.com',
]

# === Localización ===
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# === Claves primarias por defecto ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === Seguridad adicional (producción) ===
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Render behind proxy
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG  # si Render fuerza HTTPS, puedes dejarlo True en prod

# === CORS (opcional) ===
# Si expones endpoints a un frontend en Netlify:
# CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOWED_ORIGINS = [
#     'https://tu-frontend.netlify.app',
# ]
# CORS_ALLOW_CREDENTIALS = True

# === Logging para ver tracebacks con DEBUG=TRUE ===

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO' if not DEBUG else 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

