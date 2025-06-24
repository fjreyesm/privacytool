#!/usr/bin/env python3
"""
Script para corregir problemas del newsletter en PrivacyTool
Ejecutar: python newsletter_fixes.py
"""

import os
import sys

def update_requirements():
    """Actualiza requirements.txt con dependencias faltantes"""
    requirements_content = """Django==4.2.16
django-htmx==1.17.2
django-csp==3.8
django-ratelimit==4.1.0
python-dotenv==1.0.0
requests==2.31.0
psycopg2-binary==2.9.9"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    print("✅ requirements.txt actualizado")

def update_env_example():
    """Actualiza .env.example con configuración de email"""
    env_content = """# Configuración de entorno para PrivacyTool
# Copia este archivo como .env y configura las variables según tu entorno

# Configuración básica de Django
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DEBUG=True

# Configuración de URLs del sitio
# DESARROLLO - Usar para local/desarrollo
SITE_URL=http://127.0.0.1:8000
SITE_DOMAIN=127.0.0.1:8000

# PRODUCCIÓN - Usar cuando deploys a producción
# SITE_URL=https://yoursecurescan.com
# SITE_DOMAIN=yoursecurescan.com

# Hosts permitidos (separados por comas)
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.0.16

# API Keys (opcional)
HIBP_API_KEY=tu-api-key-de-have-i-been-pwned

# Configuración de base de datos (opcional, por defecto usa SQLite)
# DATABASE_URL=postgresql://usuario:password@localhost:5432/privacytool

# ===== CONFIGURACIÓN DE EMAIL (NUEVO) =====
# Backend de email - cambiar a smtp para envío real
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend  # Para envío real

# Opción 1: Gmail (RECOMENDADO para MVP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-gmail
DEFAULT_FROM_EMAIL=PrivacyTool <tu-email@gmail.com>

# Opción 2: SendGrid (MEJOR para producción)
# EMAIL_HOST=smtp.sendgrid.net
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=apikey
# EMAIL_HOST_PASSWORD=tu-sendgrid-api-key
# DEFAULT_FROM_EMAIL=PrivacyTool <noreply@yoursecurescan.com>

# Opción 3: Mailtrap (Solo para testing)
# EMAIL_HOST=smtp.mailtrap.io
# EMAIL_PORT=2525
# EMAIL_HOST_USER=tu-mailtrap-user
# EMAIL_HOST_PASSWORD=tu-mailtrap-password
# DEFAULT_FROM_EMAIL=PrivacyTool <test@privacytool.com>

# Newsletter específico
NEWSLETTER_FROM_EMAIL=PrivacyTool Newsletter <newsletter@yoursecurescan.com>
NEWSLETTER_REPLY_TO=contact@yoursecurescan.com
ADMIN_EMAIL=admin@yoursecurescan.com
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    print("✅ .env.example actualizado con configuración de email")

def create_newsletter_css_fix():
    """Crea archivo CSS con correcciones para newsletter"""
    css_content = """/* 
Correcciones CSS para Newsletter PrivacyTool
Agregar al bloque extra_head de templates/newsletter/subscribe.html
*/

/* Hero section con mejor gradiente */
.hero-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
}

/* Card del newsletter con mejor visibilidad */
.newsletter-card {
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.98) !important;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    border-radius: 1rem;
}

/* Asegurar texto visible - CRÍTICO */
.newsletter-card h2,
.newsletter-card h3,
.newsletter-card p,
.newsletter-card label,
.newsletter-card span {
    color: #1f2937 !important; /* Gris oscuro */
    font-weight: 500;
}

/* Inputs del formulario */
.newsletter-card input[type="text"],
.newsletter-card input[type="email"] {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    transition: all 0.3s ease;
    background: white;
    color: #1f2937 !important;
    font-weight: 500;
}

.newsletter-card input[type="text"]:focus,
.newsletter-card input[type="email"]:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.newsletter-card input[type="text"]::placeholder,
.newsletter-card input[type="email"]::placeholder {
    color: #9ca3af;
}

/* Checkbox de intereses - Mejor visibilidad */
.interest-option {
    position: relative;
}

.interest-option input[type="checkbox"] {
    position: absolute;
    opacity: 0;
    z-index: -1;
}

.interest-option label {
    display: block;
    padding: 0.75rem;
    border: 2px solid #d1d5db;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
    font-size: 0.75rem;
    background: white;
    color: #4b5563 !important;
    font-weight: 500;
}

.interest-option label:hover {
    border-color: #9ca3af;
    transform: translateY(-1px);
}

.interest-option input[type="checkbox"]:checked + label {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-color: #667eea !important;
    transform: scale(1.05);
    font-weight: 600;
}

/* Checkbox de privacidad */
.newsletter-card .privacy-checkbox {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
}

.newsletter-card .privacy-checkbox input[type="checkbox"] {
    width: 1.25rem;
    height: 1.25rem;
    margin: 0;
    accent-color: #667eea;
}

.newsletter-card .privacy-checkbox label {
    flex: 1;
    margin: 0;
    font-size: 0.75rem;
    line-height: 1.4;
    color: #6b7280 !important;
}

.newsletter-card .privacy-checkbox a {
    color: #3b82f6 !important;
    text-decoration: underline;
}

/* Botón principal */
.btn-subscribe {
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.btn-subscribe:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.btn-subscribe:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* Elementos flotantes menos intrusivos */
.floating-element {
    opacity: 0.05;
    animation: float 25s infinite ease-in-out;
}

/* Iconos de características */
.feature-icon {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem;
}

/* Mejoras responsivas */
@media (max-width: 768px) {
    .newsletter-card {
        margin: 1rem;
        padding: 1.5rem !important;
    }
    
    .hero-gradient {
        min-height: auto;
        padding: 2rem 0;
    }
    
    .floating-element {
        display: none; /* Ocultar en móvil */
    }
}

/* Estados de carga */
.loading {
    pointer-events: none;
    opacity: 0.7;
}

.loading .btn-subscribe {
    background: #9ca3af;
}

/* Mensajes de éxito/error */
.alert {
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    font-weight: 500;
}

.alert-success {
    background-color: #d1fae5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}

.alert-error {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
}

.alert-info {
    background-color: #dbeafe;
    color: #1e40af;
    border: 1px solid #93c5fd;
}
"""
    
    os.makedirs('static/css', exist_ok=True)
    with open('static/css/newsletter-fixes.css', 'w') as f:
        f.write(css_content)
    print("✅ CSS de correcciones creado en static/css/newsletter-fixes.css")

def create_email_test_command():
    """Crea comando de Django para probar emails"""
    command_content = """from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from newsletter.models import Subscriber
import uuid

class Command(BaseCommand):
    help = 'Envía un email de prueba para verificar configuración'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email de destino para la prueba')

    def handle(self, *args, **options):
        email = options.get('email')
        
        if not email:
            email = input("Introduce el email de destino: ")
        
        try:
            # Crear suscriptor temporal para prueba
            test_token = uuid.uuid4()
            
            # Enviar email de prueba
            send_mail(
                subject='✅ Prueba de Newsletter PrivacyTool',
                message=f'''
Hola!

Este es un email de prueba para verificar que la configuración del newsletter funciona correctamente.

Si recibes este email, significa que:
✅ La configuración SMTP está funcionando
✅ Los emails se envían correctamente
✅ El newsletter está listo para el MVP

Token de prueba: {test_token}

Saludos,
El equipo de PrivacyTool
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email de prueba enviado exitosamente a {email}')
            )
            self.stdout.write('Revisa tu bandeja de entrada (y spam)')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error enviando email: {e}')
            )
            self.stdout.write('Verifica tu configuración de email en .env')
"""
    
    # Crear directorio si no existe
    os.makedirs('newsletter/management', exist_ok=True)
    os.makedirs('newsletter/management/commands', exist_ok=True)
    
    # Crear __init__.py files
    with open('newsletter/management/__init__.py', 'w') as f:
        f.write('')
    with open('newsletter/management/commands/__init__.py', 'w') as f:
        f.write('')
    
    # Crear comando
    with open('newsletter/management/commands/test_email.py', 'w') as f:
        f.write(command_content)
    
    print("✅ Comando de prueba de email creado: python manage.py test_email")

def create_readme_fixes():
    """Crea README con instrucciones de corrección"""
    readme_content = """# 🔧 Correcciones Newsletter PrivacyTool

## 🚨 PROBLEMAS IDENTIFICADOS

1. **❌ Emails no se envían**: Backend configurado como `console`, falta SMTP
2. **❌ Texto blanco invisible**: Problemas de contraste en el formulario
3. **❌ Dependencias faltantes**: `django-ratelimit` y `python-dotenv`

## ⚡ SOLUCIÓN RÁPIDA (30 min)

### 1. Instalar dependencias actualizadas
```bash
pip install -r requirements.txt
```

### 2. Configurar email en .env
```bash
# Copiar configuración de .env.example
cp .env.example .env

# Editar .env con tus credenciales de email
# Para Gmail: generar App Password
# Para SendGrid: usar API key
```

### 3. Aplicar correcciones CSS
- El archivo `static/css/newsletter-fixes.css` contiene las correcciones
- Incluirlo en el template o copiar estilos al template existente

### 4. Probar configuración
```bash
python manage.py test_email --email tu-email@gmail.com
```

## 📧 CONFIGURACIÓN RECOMENDADA

### Opción 1: Gmail (Más Fácil)
1. Ir a Configuración de Gmail → Seguridad
2. Activar verificación en 2 pasos
3. Generar contraseña de aplicación
4. Usar en EMAIL_HOST_PASSWORD

### Opción 2: SendGrid (Profesional)
1. Crear cuenta gratuita en SendGrid
2. Verificar dominio
3. Generar API key
4. Configurar en .env

### Opción 3: Mailtrap (Solo Testing)
1. Crear cuenta en Mailtrap
2. Usar credenciales de inbox
3. Solo para desarrollo

## ✅ CHECKLIST FINAL

- [ ] Dependencies instaladas
- [ ] .env configurado
- [ ] Email de prueba enviado ✅
- [ ] CSS aplicado
- [ ] Formulario visible
- [ ] Confirmación funciona
- [ ] Admin panel accesible

## 🎯 RESULTADO ESPERADO

Después de aplicar las correcciones:
- ✅ Newsletter completamente funcional
- ✅ Emails se envían y reciben
- ✅ Formulario completamente visible
- ✅ Listo para MVP

**Tiempo estimado: 30-60 minutos**
"""
    
    with open('NEWSLETTER_FIXES_README.md', 'w') as f:
        f.write(readme_content)
    print("✅ README de correcciones creado: NEWSLETTER_FIXES_README.md")

def main():
    """Función principal que ejecuta todas las correcciones"""
    print("🚀 Iniciando correcciones del newsletter PrivacyTool...")
    print("=" * 60)
    
    try:
        update_requirements()
        update_env_example()
        create_newsletter_css_fix()
        create_email_test_command()
        create_readme_fixes()
        
        print("=" * 60)
        print("✅ TODAS LAS CORRECCIONES APLICADAS")
        print("=" * 60)
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("1. pip install -r requirements.txt")
        print("2. Configurar .env con credenciales de email")
        print("3. python manage.py test_email --email tu@email.com")
        print("4. Aplicar CSS fixes al template")
        print()
        print("📖 Lee NEWSLETTER_FIXES_README.md para instrucciones detalladas")
        
    except Exception as e:
        print(f"❌ Error durante las correcciones: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
