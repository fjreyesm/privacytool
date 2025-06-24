from django.core.management.base import BaseCommand
from newsletter.models import Subscriber, NewsletterCampaign
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Muestra estadísticas del newsletter'

    def handle(self, *args, **options):
        # Estadísticas generales
        total_subscribers = Subscriber.objects.count()
        active_subscribers = Subscriber.objects.filter(status='active').count()
        pending_subscribers = Subscriber.objects.filter(status='pending').count()
        unsubscribed = Subscriber.objects.filter(status='unsubscribed').count()
        
        # Estadísticas de la semana
        week_ago = timezone.now() - timedelta(days=7)
        new_this_week = Subscriber.objects.filter(subscribed_at__gte=week_ago).count()
        
        # Campañas
        total_campaigns = NewsletterCampaign.objects.count()
        sent_campaigns = NewsletterCampaign.objects.filter(status='sent').count()
        
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS DEL NEWSLETTER'))
        self.stdout.write('=' * 50)
        
        self.stdout.write(f'📧 Total suscriptores: {total_subscribers}')
        self.stdout.write(f'✅ Activos: {active_subscribers}')
        self.stdout.write(f'⏳ Pendientes: {pending_subscribers}')
        self.stdout.write(f'❌ Dados de baja: {unsubscribed}')
        self.stdout.write(f'🆕 Nuevos esta semana: {new_this_week}')
        self.stdout.write('')
        self.stdout.write(f'📰 Total campañas: {total_campaigns}')
        self.stdout.write(f'✉️ Campañas enviadas: {sent_campaigns}')
        
        if active_subscribers > 0:
            engagement_rate = (active_subscribers / total_subscribers) * 100 if total_subscribers > 0 else 0
            self.stdout.write(f'📈 Tasa de compromiso: {engagement_rate:.1f}%')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Newsletter listo para MVP!'))
