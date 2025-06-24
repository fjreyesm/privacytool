from django.core.management.base import BaseCommand
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
            # Crear token de prueba
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
