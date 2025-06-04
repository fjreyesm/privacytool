from django.contrib import admin
from core.models import Breach, Verification

@admin.register(Breach)
class BreachAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'breach_date', 'is_sensitive', 'severity')
    list_filter = ('is_sensitive', 'is_verified', 'is_fabricated', 'is_retired', 'is_spam_list')
    search_fields = ('name', 'domain', 'description')
    date_hierarchy = 'breach_date'

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'status', 'created_at', 'completed_at', 'breach_count')
    list_filter = ('status',)
    search_fields = ('email',)
    date_hierarchy = 'created_at'
    
    def breach_count(self, obj):
        return obj.breaches.count()
    breach_count.short_description = 'Filtraciones'
