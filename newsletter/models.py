# Newsletter App
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
import uuid

class Subscriber(models.Model):
    """Modelo para suscriptores del newsletter"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente de confirmación'),
        ('active', 'Activo'),
        ('unsubscribed', 'Dado de baja'),
        ('bounced', 'Rebotado'),
    ]
    
    INTEREST_CHOICES = [
        ('privacy', 'Privacidad y Seguridad'),
        ('tech', 'Tecnología'),
        ('security', 'Ciberseguridad'),
        ('compliance', 'Cumplimiento RGPD'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    first_name = models.CharField(max_length=100, blank=True)
    
    # Status y fechas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subscribed_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # Intereses
    interests = models.JSONField(default=list, blank=True)
    
    # Tokens para confirmación/unsubscribe
    confirmation_token = models.UUIDField(default=uuid.uuid4)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4)
    
    # Metadatos
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    source = models.CharField(max_length=100, default='website')  # website, popup, footer
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Suscriptor'
        verbose_name_plural = 'Suscriptores'
    
    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"
    
    def confirm_subscription(self):
        """Confirma la suscripción"""
        self.status = 'active'
        self.confirmed_at = timezone.now()
        self.save()
    
    def unsubscribe(self):
        """Dar de baja suscripción"""
        self.status = 'unsubscribed'
        self.unsubscribed_at = timezone.now()
        self.save()
    
    @property
    def is_active(self):
        return self.status == 'active'


class NewsletterCampaign(models.Model):
    """Modelo para campañas de newsletter"""
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('scheduled', 'Programado'),
        ('sending', 'Enviando'),
        ('sent', 'Enviado'),
        ('paused', 'Pausado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=300)
    
    # Contenido
    content_html = models.TextField(help_text="Contenido HTML del newsletter")
    content_text = models.TextField(help_text="Versión texto plano", blank=True)
    
    # Status y fechas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(default=timezone.now)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Métricas
    recipients_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    opened_count = models.PositiveIntegerField(default=0)
    clicked_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campaña Newsletter'
        verbose_name_plural = 'Campañas Newsletter'
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class NewsletterTemplate(models.Model):
    """Templates predefinidos para newsletters"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    html_content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
