from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from newsletter.models import Subscriber
import uuid
import os

class Command(BaseCommand):
    help = 'Diagnóstica y prueba la configuración de email del newsletter'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email de destino para la prueba')
        parser.add_argument('--check-config', action='store_true', help='Solo verificar configuración')

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('=' * 60)
        )
        self.stdout.write(
            self.style.HTTP_INFO('🔧 DIAGNÓSTICO DE EMAIL - NEWSLETTER PRIVACYTOOL')
        )
        self.stdout.write(
            self.style.HTTP_INFO('=' * 60)
        )
        
        # 1. Verificar configuración
        self.check_email_configuration()
        
        if options.get('check_config'):
            return
        
        # 2. Enviar email de prueba
        email = options.get('email')
        if not email:
            email = input("Introduce el email de destino: ")
        
        self.send_test_email(email)

    def check_email_configuration(self):
        """Verificar la configuración de email"""
        self.stdout.write(
            self.style.HTTP_INFO('\n📋 VERIFICANDO CONFIGURACIÓN DE EMAIL:')
        )
        
        # Verificar backend
        backend = getattr(settings, 'EMAIL_BACKEND', 'No configurado')
        self.stdout.write(f"   EMAIL_BACKEND: {backend}")
        
        if 'smtp' in backend.lower():
            # Verificar configuración SMTP
            host = getattr(settings, 'EMAIL_HOST', 'No configurado')
            port = getattr(settings, 'EMAIL_PORT', 'No configurado')
            use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
            use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
            user = getattr(settings, 'EMAIL_HOST_USER', 'No configurado')
            password = getattr(settings, 'EMAIL_HOST_PASSWORD', 'No configurado')
            
            self.stdout.write(f"   EMAIL_HOST: {host}")
            self.stdout.write(f"   EMAIL_PORT: {port}")
            self.stdout.write(f"   EMAIL_USE_TLS: {use_tls}")
            self.stdout.write(f"   EMAIL_USE_SSL: {use_ssl}")
            self.stdout.write(f"   EMAIL_HOST_USER: {user}")
            self.stdout.write(f"   EMAIL_HOST_PASSWORD: {'*' * len(str(password)) if password and password != 'No configurado' else 'No configurado'}")
            
            # Verificar si la configuración está completa
            if all([host != 'No configurado', user != 'No configurado', password != 'No configurado']):
                self.stdout.write(
                    self.style.SUCCESS("   ✅ Configuración SMTP completa")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("   ❌ Configuración SMTP incompleta")
                )
        
        # Verificar DEFAULT_FROM_EMAIL
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'No configurado')
        self.stdout.write(f"   DEFAULT_FROM_EMAIL: {from_email}")
        
        # Verificar variables de entorno relevantes
        self.stdout.write(
            self.style.HTTP_INFO('\n🔍 VARIABLES DE ENTORNO:')
        )
        
        env_vars = [
            'EMAIL_BACKEND', 'EMAIL_HOST', 'EMAIL_PORT', 
            'EMAIL_USE_TLS', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD',
            'DEFAULT_FROM_EMAIL'
        ]
        
        for var in env_vars:
            value = os.environ.get(var, 'No definida')
            if 'PASSWORD' in var and value != 'No definida':
                value = '*' * len(value)
            self.stdout.write(f"   {var}: {value}")

    def send_test_email(self, email):
        """Enviar email de prueba"""
        self.stdout.write(
            self.style.HTTP_INFO(f'\n📧 ENVIANDO EMAIL DE PRUEBA A: {email}')
        )
        
        try:
            # Crear token de prueba
            test_token = uuid.uuid4()
            
            # Mensaje de prueba
            subject = '✅ Prueba de Newsletter PrivacyTool'
            message = f'''
Hola!

Este es un email de prueba para verificar que la configuración del newsletter funciona correctamente.

Si recibes este email, significa que:
✅ La configuración SMTP está funcionando
✅ Los emails se envían correctamente  
✅ El newsletter está listo para el MVP

Información técnica:
- Servidor SMTP: {getattr(settings, 'EMAIL_HOST', 'No configurado')}
- Puerto: {getattr(settings, 'EMAIL_PORT', 'No configurado')}
- TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}
- Usuario: {getattr(settings, 'EMAIL_HOST_USER', 'No configurado')}
- Backend: {getattr(settings, 'EMAIL_BACKEND', 'No configurado')}

Token de prueba: {test_token}

Saludos,
El equipo de PrivacyTool
            '''
            
            # Enviar email
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Email de prueba enviado exitosamente a {email}')
                )
                self.stdout.write('📨 Revisa tu bandeja de entrada (y spam)')
                
                # Información adicional
                self.stdout.write(
                    self.style.HTTP_INFO('\n📊 INFORMACIÓN ADICIONAL:')
                )
                self.stdout.write(f"   From: {settings.DEFAULT_FROM_EMAIL}")
                self.stdout.write(f"   To: {email}")
                self.stdout.write(f"   Subject: {subject}")
                
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Email enviado pero resultado incierto')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error enviando email: {e}')
            )
            
            # Sugerencias de troubleshooting
            self.stdout.write(
                self.style.HTTP_INFO('\n🔧 POSIBLES SOLUCIONES:')
            )
            self.stdout.write('   1. Verifica que tengas habilitada la autenticación de 2 pasos en Gmail')
            self.stdout.write('   2. Asegúrate de usar una App Password, no tu contraseña normal')
            self.stdout.write('   3. Copia el archivo .env.gmail a .env:')
            self.stdout.write('      cp .env.gmail .env')
            self.stdout.write('   4. Reinicia el contenedor Docker:')
            self.stdout.write('      docker compose down && docker compose up -d')
            self.stdout.write('   5. Verifica que las variables estén en .env, no solo en environment')
