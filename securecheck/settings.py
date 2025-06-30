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

# 🍪 COOKIE BANNER CONFIGURATION - Opción 2 implementada
SHOW_COOKIE_BANNER = not DEBUG  # False en desarrollo, True en producción
ENABLE_COOKIE_CONSENT = not DEBUG  # Banner funcional solo en producción

# CSRF Configuration - FIX CRITICAL
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://192.168.0.16:8000',  # Tu IP móvil
]

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
    'csp',  # CSP reactivado con configuración corregida
    
    # Apps propias
    'core.apps.CoreConfig',
    'newsletter.apps.NewsletterConfig',  # Newsletter app added
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',  # CSP reactivado
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
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'privacytool'),
        'USER': os.environ.get('POSTGRES_USER', 'privacyuser'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'secure_password_2024'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    },
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

# ===== CONFIGURACIÓN DE EMAIL MEJORADA =====
# 🔧 FIX: Configuración de email forzada para usar SMTP siempre que esté configurado

# Verificar si tenemos configuración de email válida
HAS_EMAIL_CONFIG = all([
    os.environ.get('EMAIL_HOST_USER'),
    os.environ.get('EMAIL_HOST_PASSWORD'),
    os.environ.get('EMAIL_BACKEND')
])

# Email configuration
if HAS_EMAIL_CONFIG:
    # Si tenemos configuración completa, usar SMTP
    EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    print(f"📧 Email configurado: {EMAIL_HOST_USER} via {EMAIL_HOST}")
else:
    # Sin configuración, usar console en desarrollo
    if DEBUG:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        print("📧 Email: modo console (desarrollo)")
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = 'smtp.gmail.com'
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True
        EMAIL_HOST_USER = ''
        EMAIL_HOST_PASSWORD = ''
        print("⚠️ Email: configuración incompleta en producción")

# Email settings
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'PrivacyTool <noreply@privacytool.com>')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@privacytool.com')

# Newsletter specific settings
NEWSLETTER_FROM_EMAIL = os.environ.get('NEWSLETTER_FROM_EMAIL', DEFAULT_FROM_EMAIL)
NEWSLETTER_REPLY_TO = os.environ.get('NEWSLETTER_REPLY_TO', 'contact@privacytool.com')

# Email timeout settings
EMAIL_TIMEOUT = 30

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

# --- CONFIGURACIÓN DE DJANGO-RATELIMIT (DIFERENTE POR ENTORNO) ---
if DEBUG:
    # Desarrollo: Rate limiting muy permisivo
    RATELIMIT_RATE = '999/m'  # Sin límites prácticos en desarrollo
    RATELIMIT_ENABLE = False   # Deshabilitado en desarrollo
else:
    # Producción: Rate limiting normal
    RATELIMIT_RATE = '30/h'    # 30 peticiones por hora en producción
    RATELIMIT_ENABLE = True    # Habilitado en producción

RATELIMIT_KEY = 'ip'           # Limita por dirección IP del usuario
RATELIMIT_BLOCK = True         # Si se supera el límite, bloquea la petición
RATELIMIT_METHOD = 'all'       # Aplica el límite a todos los métodos (GET, POST, etc.)

# Configuración del sitio para sitemaps
SITE_ID = 1

# ===== CONTENT SECURITY POLICY (CSP) - CONFIGURACIÓN CORREGIDA =====
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'", "https://unpkg.com", "https://cdn.jsdelivr.net"),
        'style-src': ("'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com"),
        'font-src': ("'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"),
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

# ===== LOGGING CONFIGURATION =====
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
            'formatter': 'simple'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'newsletter': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ===== NEWSLETTER SPECIFIC SETTINGS =====
# Configuración específica para el newsletter
NEWSLETTER_SETTINGS = {
    'SITE_NAME': 'PrivacyTool',
    'SITE_DESCRIPTION': 'Tu herramienta de privacidad y seguridad',
    'CONTACT_EMAIL': 'contact@privacytool.com',
    'SOCIAL_MEDIA': {
        'twitter': 'https://twitter.com/privacytool',
        'linkedin': 'https://linkedin.com/company/privacytool',
    },
    'UNSUBSCRIBE_REASONS': [
        'No me interesa el contenido',
        'Recibo demasiados emails',
        'No solicité este newsletter',
        'Problemas técnicos',
        'Otro'
    ]
}

# --- CONFIGURACIÓN DE CONTENT SECURITY POLICY (CSP) ---
# settings.py - CONFIGURACIÓN FINAL RECOMENDADA

CSP_DEFAULT_SRC = ("'self'",)

CSP_CONNECT_SRC = (
    "'self'",
    "https://haveibeenpwned.com",  # ← AGREGAR ESTO
)

CSP_STYLE_SRC = (
    "'self'",
    "fonts.googleapis.com",
    "cdnjs.cloudflare.com",
    "'unsafe-inline'", # Requerido por Tailwind CSS y otros estilos en línea
)

CSP_SCRIPT_SRC = (
    "'self'",
    "unpkg.com",
    "cdn.jsdelivr.net",
    "'unsafe-eval'",  # Requerido por Alpine.js para funcionar
    "'unsafe-inline'",

)

CSP_FONT_SRC = ("'self'", "fonts.gstatic.com", "cdnjs.cloudflare.com")
CSP_IMG_SRC = ("'self'", "data:") 

# Activa nonces para scripts y estilos, permitiendo eliminar 'unsafe-inline'
CSP_INCLUDE_NONCE_IN = ['style-src']


#