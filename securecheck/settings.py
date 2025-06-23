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
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Detectar si estamos en producción
PRODUCTION = os.environ.get('PRODUCTION', 'False') == 'True'

# === CONFIGURACIÓN DE SEGURIDAD ===

# Protección XSS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Protección Clickjacking
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security) 
# Configuración que elimina advertencias W004, W005, W021
SECURE_HSTS_SECONDS = 31536000 if PRODUCTION else 60  # 1 año en producción, 1 minuto en desarrollo
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Siempre True para eliminar W005
SECURE_HSTS_PRELOAD = True             # Siempre True para eliminar W021

# SSL/HTTPS - Para eliminar warning W008
SECURE_SSL_REDIRECT = PRODUCTION  # Solo redirigir a HTTPS en producción

# Cookies seguras - Para eliminar warnings W012 y W016
SESSION_COOKIE_SECURE = PRODUCTION  # Solo HTTPS en producción  
CSRF_COOKIE_SECURE = PRODUCTION     # Solo HTTPS en producción
SESSION_COOKIE_HTTPONLY = True      # Previene acceso JS a cookies de sesión
CSRF_COOKIE_HTTPONLY = True         # Previene acceso JS a cookies CSRF

# Configuración adicional de cookies
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Protección adicional
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if PRODUCTION else None

# === CONFIGURACIÓN DE HOSTS ===
if PRODUCTION:
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.0.16', '0.0.0.0']

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

# === CONFIGURACIÓN DE BASE DE DATOS ===
if PRODUCTION:
    # PostgreSQL para producción
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'securecheck'),
            'USER': os.environ.get('POSTGRES_USER', 'securecheck'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    # Permitir elección entre SQLite y PostgreSQL en desarrollo
    if os.environ.get('USE_POSTGRES', 'False') == 'True':
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('POSTGRES_DB', 'securecheck'),
                'USER': os.environ.get('POSTGRES_USER', 'securecheck'),
                'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'securecheck'),
                'HOST': os.environ.get('DB_HOST', 'db'),
                'PORT': os.environ.get('DB_PORT', '5432'),
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

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

# === CONFIGURACIÓN DE LOGGING ===
# Crear directorio de logs si no existe
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

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
if PRODUCTION:
    # Configuración real para producción
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
else:
    # Console backend para desarrollo
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yoursecurescan.com')

# Configuración de API Keys
HIBP_API_KEY = os.environ.get("HIBP_API_KEY", "")

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# === CONFIGURACIÓN DE RATE LIMITING ===
RATELIMIT_KEY = 'ip'  # Limita por dirección IP del usuario.
RATELIMIT_RATE = '5/m' # 5 peticiones por minuto. Puedes ajustarlo a '10/h' (10 por hora), etc.
RATELIMIT_BLOCK = True # Si se supera el límite, bloquea la petición (genera un error).
RATELIMIT_METHOD = 'all' # Aplica el límite a todos los métodos (GET, POST, etc.)

# Configuración del sitio para sitemaps
SITE_ID = 1

# === CONFIGURACIÓN ESPECÍFICA PARA DESARROLLO ===
if DEBUG:
    # Herramientas de desarrollo adicionales
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Mostrar errores SQL en desarrollo
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
    }