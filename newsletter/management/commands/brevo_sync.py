# Newsletter management utilities para Brevo integration
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json

class Command(BaseCommand):
    help = 'Sincroniza suscriptores con Brevo'

    def add_arguments(self, parser):
        parser.add_argument('--action', choices=['sync', 'create_list', 'stats'], required=True)
        parser.add_argument('--list-name', default='YourSecureScan Newsletter')

    def handle(self, *args, **options):
        if not hasattr(settings, 'BREVO_API_KEY'):
            self.stdout.write(self.style.ERROR('BREVO_API_KEY no configurado en settings'))
            return

        if options['action'] == 'create_list':
            self.create_brevo_list(options['list_name'])
        elif options['action'] == 'sync':
            self.sync_subscribers()
        elif options['action'] == 'stats':
            self.show_stats()

    def create_brevo_list(self, list_name):
        """Crear lista de contactos en Brevo"""
        url = "https://api.brevo.com/v3/contacts/lists"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": settings.BREVO_API_KEY
        }
        data = {
            "name": list_name,
            "folderId": 1
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                result = response.json()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Lista creada: {list_name} (ID: {result["id"]})')
                )
                self.stdout.write(f'Actualiza BREVO_LIST_ID={result["id"]} en tu .env')
            else:
                self.stdout.write(self.style.ERROR(f'Error: {response.text}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

    def sync_subscribers(self):
        """Sincronizar suscriptores de Django con Brevo"""
        from newsletter.models import Subscriber
        
        subscribers = Subscriber.objects.filter(confirmed=True)
        self.stdout.write(f'Sincronizando {subscribers.count()} suscriptores...')

        url = "https://api.brevo.com/v3/contacts"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": settings.BREVO_API_KEY
        }

        success_count = 0
        for subscriber in subscribers:
            data = {
                "email": subscriber.email,
                "listIds": [int(settings.BREVO_LIST_ID)],
                "attributes": {
                    "FIRSTNAME": subscriber.name or "",
                    "SUBSCRIBED_DATE": subscriber.created_at.isoformat(),
                    "SOURCE": "YourSecureScan"
                }
            }

            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code in [201, 204]:
                    success_count += 1
                    self.stdout.write(f'✅ {subscriber.email}')
                else:
                    self.stdout.write(f'❌ {subscriber.email}: {response.text}')
            except Exception as e:
                self.stdout.write(f'❌ {subscriber.email}: {e}')

        self.stdout.write(
            self.style.SUCCESS(f'✅ {success_count}/{subscribers.count()} suscriptores sincronizados')
        )

    def show_stats(self):
        """Mostrar estadísticas de Brevo"""
        url = f"https://api.brevo.com/v3/contacts/lists/{settings.BREVO_LIST_ID}"
        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(f'📊 Lista: {data["name"]}')
                self.stdout.write(f'👥 Total contactos: {data["totalSubscribers"]}')
                self.stdout.write(f'✅ Activos: {data["totalSubscribers"]}')
            else:
                self.stdout.write(self.style.ERROR(f'Error: {response.text}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
