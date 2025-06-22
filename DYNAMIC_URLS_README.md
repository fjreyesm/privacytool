# Configuración de Variables de Entorno para URLs Dinámicas

## 🎯 Problema Solucionado

Antes tenías URLs hardcodeadas que requerían cambios manuales entre desarrollo y producción. Ahora el sistema se adapta automáticamente usando variables de entorno.

## ⚙️ Configuración Implementada

### 1. Variables de Entorno Añadidas

En `settings.py`:
```python
# Configuración de URL del sitio para diferentes entornos
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', '127.0.0.1:8000')
```

### 2. Context Processor Creado

En `core/context_processors.py`:
```python
def site_settings(request):
    return {
        'SITE_URL': settings.SITE_URL,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'DEBUG': settings.DEBUG,
    }
```

Esto hace que estas variables estén disponibles en **todos los templates** automáticamente.

### 3. Template Mejorado

En `base.html` ahora tienes:
```html
<!-- URL Canónica automática -->
<link rel="canonical" href="{{ SITE_URL }}{{ request.get_full_path }}">

<!-- Open Graph con URLs dinámicas -->
<meta property="og:url" content="{{ SITE_URL }}{{ request.get_full_path }}">

<!-- Meta robots condicional -->
{% if not DEBUG %}
<meta name="robots" content="index, follow">
{% else %}
<meta name="robots" content="noindex, nofollow">
{% endif %}
```

## 🚀 Cómo Usar

### Para Desarrollo Local

1. **Crea tu archivo `.env`**:
   ```bash
   cp .env.example .env
   ```

2. **Configura para desarrollo** (`.env`):
   ```env
   SITE_URL=http://127.0.0.1:8000
   SITE_DOMAIN=127.0.0.1:8000
   DEBUG=True
   ```

### Para Producción

**Configura variables de entorno** (`.env` o servidor):
```env
SITE_URL=https://yoursecurescan.com
SITE_DOMAIN=yoursecurescan.com
DEBUG=False
ALLOWED_HOSTS=yoursecurescan.com,www.yoursecurescan.com
```

## ✨ Beneficios Automáticos

### ✅ En Templates
```html
<!-- En cualquier template puedes usar: -->
<a href="{{ SITE_URL }}/verification/">Ver verificación</a>
<img src="{{ SITE_URL }}/static/logo.png" alt="Logo">

<!-- URLs canónicas automáticas -->
<link rel="canonical" href="{{ SITE_URL }}{{ request.get_full_path }}">

<!-- Open Graph automático -->
<meta property="og:url" content="{{ SITE_URL }}{{ request.get_full_path }}">
```

### ✅ En Robots.txt
- **Desarrollo**: `Sitemap: http://127.0.0.1:8000/sitemap.xml`
- **Producción**: `Sitemap: https://yoursecurescan.com/sitemap.xml`

### ✅ En Meta Tags
- **Desarrollo**: `<meta name="robots" content="noindex, nofollow">`
- **Producción**: `<meta name="robots" content="index, follow">`

## 🔧 Comandos Útiles

### Verificar configuración actual:
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(f"SITE_URL: {settings.SITE_URL}")
>>> print(f"SITE_DOMAIN: {settings.SITE_DOMAIN}")
>>> print(f"DEBUG: {settings.DEBUG}")
```

### Verificar que funciona en templates:
```bash
python manage.py shell
>>> from django.template import Context, Template
>>> from django.conf import settings
>>> from core.context_processors import site_settings
>>> from django.http import HttpRequest
>>> 
>>> request = HttpRequest()
>>> context = site_settings(request)
>>> print(context)
```

## 📝 Casos de Uso

### 1. URLs en Email Templates
```html
<a href="{{ SITE_URL }}{% url 'core:verification_home' %}">
  Verificar tu email aquí
</a>
```

### 2. APIs que devuelven URLs
```python
def get_verification_url(self):
    return f"{settings.SITE_URL}{reverse('core:verification_home')}"
```

### 3. Social Media Share
```html
<a href="https://twitter.com/intent/tweet?url={{ SITE_URL }}{{ request.get_full_path }}&text=Mira esta herramienta de privacidad">
  Compartir en Twitter
</a>
```

### 4. Structured Data
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "url": "{{ SITE_URL }}{{ request.get_full_path }}",
  "name": "{{ page_title }}"
}
</script>
```

## 🎯 Para Diferentes Entornos

### Desarrollo
```env
SITE_URL=http://127.0.0.1:8000
DEBUG=True
```

### Staging
```env
SITE_URL=https://staging.yoursecurescan.com
DEBUG=False
```

### Producción
```env
SITE_URL=https://yoursecurescan.com
DEBUG=False
```

## 🔄 Migración Automática

**No necesitas cambiar nada manualmente**. El sistema:

1. ✅ **Lee automáticamente** las variables de entorno
2. ✅ **Sirve el robots.txt** con la URL correcta
3. ✅ **Genera URLs canónicas** automáticamente
4. ✅ **Configura meta tags** según el entorno
5. ✅ **Ajusta comportamiento** de indexación por bots

¡Tu aplicación ahora es **environment-aware** y se adapta automáticamente! 🎉