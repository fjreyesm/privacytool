# NEWSLETTER EMAIL TROUBLESHOOTING GUIDE

## Problema Identificado

Los emails de confirmación del newsletter no se están enviando correctamente porque hay un conflicto entre la configuración de desarrollo (console backend) y la configuración de producción (SMTP).

## Causas del Problema

### 1. Configuración de DEBUG vs EMAIL_BACKEND

En `settings.py` teníamos:

```python
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

Esto significa que en modo DEBUG=True, los emails solo se muestran en consola, no se envían realmente.

### 2. Variables de entorno faltantes

El archivo `.env` no tenía las configuraciones de Gmail necesarias.

### 3. Inconsistencia en DEFAULT_FROM_EMAIL

El test_email command funcionaba porque usaba configuraciones diferentes a las del newsletter real.

## Soluciones Implementadas

### 1. ✅ Archivo `.env.gmail`

Creé un archivo con la configuración completa de Gmail:

```bash
# Usar este archivo como base para tu .env
cp .env.gmail .env
```

**IMPORTANTE**: Reemplaza `xxxx_tu_app_password_aqui` con tu App Password real de Google.

### 2. ✅ Settings.py Mejorado

- Lógica mejorada para detectar si hay configuración de email válida
- Fuerza el uso de SMTP cuando hay configuración disponible
- Mejor logging para debugging

### 3. ✅ Comando de Diagnóstico

Nuevo comando para diagnosticar problemas:

```bash
# Verificar solo la configuración
docker compose exec web python manage.py email_diagnosis --check-config

# Enviar email de prueba
docker compose exec web python manage.py email_diagnosis --email tu@email.com
```

## Pasos para Resolver el Problema

### Paso 1: Configurar Gmail App Password

1. Ve a tu cuenta de Google → Seguridad
2. Habilita autenticación de 2 pasos si no la tienes
3. Genera una "App Password" específica para esta aplicación
4. Copia los 16 caracteres (sin espacios)

### Paso 2: Actualizar .env

```bash
# En tu directorio del proyecto
cp .env.gmail .env

# Editar .env y reemplazar xxxx_tu_app_password_aqui con tu App Password real
# 
```

### Paso 3: Reiniciar Docker

```bash
docker compose down
docker compose up -d
```

### Paso 4: Verificar Configuración

```bash
docker compose exec web python manage.py email_diagnosis --check-config
```

Deberías ver algo como:

```
📧
✅ Configuración SMTP completa
```

### Paso 5: Probar Email

```bash
docker compose exec web python manage.py email_diagnosis --email info@yoursecurescan.com
```

### Paso 6: Probar Newsletter Real

1. Ve a tu sitio web
2. Suscríbete al newsletter con un email de prueba
3. Deberías recibir el email de confirmación

## Debugging Adicional

### Ver logs en tiempo real

```bash
docker compose logs -f web
```

### Verificar que las variables se cargaron

```bash
docker compose exec web python manage.py shell
>>> import os
>>> print(os.environ.get('EMAIL_HOST_USER'))
>>> print(os.environ.get('EMAIL_BACKEND'))
```

### Test manual desde Django shell

```bash
docker compose exec web python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# Verificar configuración
print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"User: {settings.EMAIL_HOST_USER}")

# Enviar test
send_mail(
    'Test desde shell',
    'Este es un test manual',
    settings.DEFAULT_FROM_EMAIL,
    ['tu@email.com'],
    fail_silently=False
)
```

## Errores Comunes y Soluciones

### Error: "SMTPAuthenticationError"

- **Causa**: App Password incorrecto o no configurado
- **Solución**: Regenerar App Password en Google y actualizar .env

### Error: "Connection refused"

- **Causa**: Firewall bloqueando puerto 587
- **Solución**: Verificar que el puerto 587 esté abierto

### Error: "User not authenticated"

- **Causa**: Usando contraseña normal en lugar de App Password
- **Solución**: Usar App Password de 16 caracteres

### Los emails van a spam

- **Causa**: Gmail detecta el email como posible spam
- **Solución**:
  - Verificar configuración SPF/DKIM en tu dominio
  - Usar un dominio verificado
  - Por ahora, revisar carpeta de spam

## Verificación Final

Una vez configurado correctamente, deberías poder:

1. ✅ Ver confirmación de configuración en el comando diagnosis
2. ✅ Recibir emails de prueba del comando test_email
3. ✅ Recibir emails de confirmación del newsletter
4. ✅ Ver logs sin errores de SMTP

## Archivo de configuración completa (.env)

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.0.16
SITE_URL=http://127.0.0.1:8000
SITE_DOMAIN=127.0.0.1:8000

# Database
POSTGRES_DB=privacytool
POSTGRES_USER=privacyuser
POSTGRES_PASSWORD=secure_password_2024
POSTGRES_HOST=db
POSTGRES_PORT=5432
USE_SQLITE=False

# Email Configuration Gmail


# API Keys
HIBP_API_KEY=
```

## Contacto para Soporte

Si después de seguir estos pasos sigues teniendo problemas:

1. Ejecuta el comando de diagnóstico y comparte la salida
2. Verifica que el App Password sea correcto
3. Revisa los logs de Docker
4. Confirma que las variables de entorno se están cargando

**¡El newsletter debería funcionar perfectamente después de estos cambios!**
