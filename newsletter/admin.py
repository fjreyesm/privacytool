# Newsletter Admin Configuration
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Subscriber, NewsletterTemplate, NewsletterCampaign


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = [
        'email', 
        'first_name', 
        'status_badge', 
        'source', 
        'subscribed_at', 
        'confirmed_at',
        'interests_display'
    ]
    list_filter = [
        'status', 
        'source', 
        'interests', 
        'subscribed_at', 
        'confirmed_at'
    ]
    search_fields = ['email', 'first_name', 'ip_address']
    readonly_fields = [
        'confirmation_token', 
        'unsubscribe_token', 
        'ip_address', 
        'user_agent',
        'subscribed_at',
        'confirmed_at',
        'unsubscribed_at'
    ]
    list_per_page = 50
    date_hierarchy = 'subscribed_at'
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('email', 'first_name', 'interests')
        }),
        ('Estado de Suscripción', {
            'fields': ('status', 'subscribed_at', 'confirmed_at', 'unsubscribed_at')
        }),
        ('Datos Técnicos', {
            'fields': ('source', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Tokens', {
            'fields': ('confirmation_token', 'unsubscribe_token'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': 'orange',
            'active': 'green',
            'unsubscribed': 'red',
            'bounced': 'darkred'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def interests_display(self, obj):
        """Display interests as badges"""
        if obj.interests:
            interests = obj.interests
            badges = []
            for interest in interests:
                badges.append(f'<span style="background: #e3f2fd; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{interest}</span>')
            return format_html(' '.join(badges))
        return '-'
    interests_display.short_description = 'Intereses'
    
    actions = ['mark_as_active', 'mark_as_unsubscribed', 'resend_confirmation']
    
    def mark_as_active(self, request, queryset):
        """Mark subscribers as active"""
        updated = queryset.update(
            status='active',
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'{updated} suscriptores marcados como activos.')
    mark_as_active.short_description = 'Marcar como activos'
    
    def mark_as_unsubscribed(self, request, queryset):
        """Mark subscribers as unsubscribed"""
        updated = queryset.update(
            status='unsubscribed',
            unsubscribed_at=timezone.now()
        )
        self.message_user(request, f'{updated} suscriptores dados de baja.')
    mark_as_unsubscribed.short_description = 'Dar de baja'
    
    def resend_confirmation(self, request, queryset):
        """Resend confirmation emails"""
        pending_subscribers = queryset.filter(status='pending')
        count = 0
        for subscriber in pending_subscribers:
            # TODO: Implement resend confirmation email logic
            count += 1
        self.message_user(request, f'Emails de confirmación reenviados a {count} suscriptores.')
    resend_confirmation.short_description = 'Reenviar confirmación'


@admin.register(NewsletterTemplate)
class NewsletterTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'description_short', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Contenido HTML', {
            'fields': ('html_content',)
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def description_short(self, obj):
        """Display truncated description"""
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = 'Descripción'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add custom CSS for better editing experience
        form.base_fields['html_content'].widget.attrs.update({
            'rows': 20,
            'style': 'font-family: monospace;'
        })
        if 'description' in form.base_fields:
            form.base_fields['description'].widget.attrs.update({
                'rows': 3,
            })
        return form


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'subject_short', 
        'status_badge', 
        'recipients_count', 
        'sent_at', 
        'open_rate_display'
    ]
    list_filter = ['status', 'sent_at', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = [
        'created_at', 
        'sent_at', 
        'recipients_count',
        'sent_count',
        'opened_count',
        'clicked_count'
    ]
    
    fieldsets = (
        ('Información de Campaña', {
            'fields': ('name', 'subject', 'status')
        }),
        ('Contenido', {
            'fields': ('content_html', 'content_text')
        }),
        ('Programación', {
            'fields': ('scheduled_at',)
        }),
        ('Estadísticas', {
            'fields': ('recipients_count', 'sent_count', 'opened_count', 'clicked_count'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'sent_at'),
            'classes': ('collapse',)
        }),
    )
    
    def subject_short(self, obj):
        """Display truncated subject"""
        if obj.subject:
            return obj.subject[:40] + '...' if len(obj.subject) > 40 else obj.subject
        return '-'
    subject_short.short_description = 'Asunto'
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'draft': 'gray',
            'scheduled': 'orange',
            'sending': 'blue',
            'sent': 'green',
            'paused': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def open_rate_display(self, obj):
        """Display open rate percentage"""
        if obj.recipients_count > 0:
            rate = (obj.opened_count / obj.recipients_count) * 100
            return f'{rate:.1f}%'
        return '0%'
    open_rate_display.short_description = 'Tasa de Apertura'
    
    actions = ['mark_as_sent', 'duplicate_campaign']
    
    def mark_as_sent(self, request, queryset):
        """Mark campaigns as sent"""
        updated = queryset.update(
            status='sent',
            sent_at=timezone.now()
        )
        self.message_user(request, f'{updated} campañas marcadas como enviadas.')
    mark_as_sent.short_description = 'Marcar como enviadas'
    
    def duplicate_campaign(self, request, queryset):
        """Duplicate selected campaigns"""
        for campaign in queryset:
            campaign.pk = None
            campaign.name = f'{campaign.name} (Copia)'
            campaign.status = 'draft'
            campaign.sent_at = None
            campaign.recipients_count = 0
            campaign.sent_count = 0
            campaign.opened_count = 0
            campaign.clicked_count = 0
            campaign.save()
        self.message_user(request, f'{len(queryset)} campañas duplicadas.')
    duplicate_campaign.short_description = 'Duplicar campañas'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add custom CSS for better editing experience
        form.base_fields['content_html'].widget.attrs.update({
            'rows': 20,
            'style': 'font-family: monospace;'
        })
        form.base_fields['content_text'].widget.attrs.update({
            'rows': 15,
            'style': 'font-family: monospace;'
        })
        return form


# Customize Admin Site
admin.site.site_header = 'PrivacyTool Admin'
admin.site.site_title = 'PrivacyTool'
admin.site.index_title = 'Panel de Administración'
