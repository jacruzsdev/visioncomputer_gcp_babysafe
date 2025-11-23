# safety_project/settings.py
from pathlib import Path
import os
# La importación de dj_database_url es opcional si solo usas SQLite. 
# Si la dejas, recuerda que DEBE estar en requirements.txt
# import dj_database_url 

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-unsafereservekey-only-for-local-use-only')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
# Utilizamos la base de datos para la sesión (aunque sea SQLite temporalmente)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Si quieres que la sesión expire al cerrar el navegador (seguro para historial)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 2. CONFIGURACIÓN DE HOSTS (necesario para Cloud Run)
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1'] 
# Permite el acceso seguro desde la URL de Cloud Run
CSRF_TRUSTED_ORIGINS = ['https://*.run.app'] 

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'safety_detector', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'safety_project.urls'
WSGI_APPLICATION = 'safety_project.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# Configuración de Base de Datos (Usando SQLite por defecto para simplicidad)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    # ... validadores estándar
]

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Configuración de Archivos Estáticos (Crucial para Cloud Run) ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'