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

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 0 # Cambia a True en producción a => 31536000 if not DEBUG else 0    --1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = False # Cambia a True en producción si usas HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
#DEBUG = True  # <-- Forzamos el modo DEBUG para poder depurar
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1, 192.168.0.16').split(',')

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
    'csp',  # Content Security Policy
    
    # Apps propias
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',  # CSP debe ir temprano en el middleware stack
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

# Database - TEMPORAL: Volver a SQLite hasta resolver PostgreSQL mañana
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL configuration (preparado para mañana)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('POSTGRES_DB', 'privacytool'),
#         'USER': os.environ.get('POSTGRES_USER', 'privacyuser'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'secure_password_2024'),
#         'HOST': os.environ.get('POSTGRES_HOST', 'db'),
#         'PORT': os.environ.get('POSTGRES_PORT', '5432'),
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

# Añade estas líneas al final del archivo
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

# ===== CONTENT SECURITY POLICY (CSP) - NUEVO FORMATO =====
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com", "https://unpkg.com"),
        'style-src': ("'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com", "https://fonts.googleapis.com"),
        'font-src': ("'self'", "https://fonts.gstatic.com"),
        'img-src': ("'self'", "data:", "https:"),
        'connect-src': ("'self'",),
        'frame-src': ("'none'",),
        'object-src': ("'none'",),
        'base-uri': ("'self'",),
        'form-action': ("'self'",),
        'frame-ancestors': ("'none'",),
    }
}

# Configuración adicional para desarrollo
if DEBUG:
    CONTENT_SECURITY_POLICY['DIRECTIVES']['script-src'] += ("'unsafe-eval'",)
    CONTENT_SECURITY_POLICY['DIRECTIVES']['connect-src'] += ("ws:", "wss:")
