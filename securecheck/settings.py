import os
from pathlib import Path
from dotenv import load_dotenv

# securecheck/settings.py
# Cargar variables de entorno desde .env
load_dotenv()

# Intentar obtener la clave secreta desde las variables de entorno
try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    # Este error se lanzará si la variable no existe en el entorno
    raise ValueError("Error: La variable de entorno SECRET_KEY no está definida. Por favor, añádela a tu archivo .env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Configuración de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000  # 1 año en producción
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = False  # Cambia a True en producción si usas HTTPS
SESSION_COOKIE_SECURE = not DEBUG  # True en producción
CSRF_COOKIE_SECURE = not DEBUG     # True en producción
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,192.168.0.16').split(',')

# Configuración de URL del sitio para diferentes entornos
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', '127.0.0.1:8000')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',  # Añadido para sitemaps
    
    # Apps de terceros
    'django_htmx',
    
    # Apps propias
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'securecheck.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',  # Nuevo context processor
            ],
        },
    },
]

WSGI_APPLICATION = 'securecheck.wsgi.application'

# Reemplaza solo la sección DATABASES en tu settings.py

# Database - SQLite TEMPORAL (para recuperar datos)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Database - PostgreSQL para Docker
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('POSTGRES_DB', 'securecheck'),
#         'USER': os.environ.get('POSTGRES_USER', 'securecheck'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'securecheck'),
#         'HOST': os.environ.get('DB_HOST', 'db'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de caché (opcional, para producción usar Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Configuración de correo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desarrollo
DEFAULT_FROM_EMAIL = 'noreply@yoursecurescan.com'

# Configuración de API Keys
HIBP_API_KEY = os.environ.get("HIBP_API_KEY", "")

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# --- CONFIGURACIÓN DE DJANGO-RATELIMIT ---
RATELIMIT_KEY = 'ip'  # Limita por dirección IP del usuario.
RATELIMIT_RATE = '5/m' # 5 peticiones por minuto. Puedes ajustarlo a '10/h' (10 por hora), etc.
RATELIMIT_BLOCK = True # Si se supera el límite, bloquea la petición (genera un error).
RATELIMIT_METHOD = 'all' # Aplica el límite a todos los métodos (GET, POST, etc.)

# Configuración del sitio para sitemaps
SITE_ID = 1