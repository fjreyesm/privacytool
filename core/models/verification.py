from django.db import models
import uuid
from django.contrib.auth.models import User

class Verification(models.Model):
    """Modelo para almacenar verificaciones de email en HIBP."""
    
    STATUS_CHOICES = [
        ('processing', 'Procesando'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(null=True, blank=True)
    
    # Relación con filtraciones encontradas
    breaches = models.ManyToManyField('Breach', blank=True)
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Verificación"
        verbose_name_plural = "Verificaciones"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Verificación de {self.email} ({self.status})"
    
    @property
    def breach_count(self):
        """Devuelve el número de filtraciones encontradas."""
        return self.breaches.count()
    
    @property
    def has_sensitive_breaches(self):
        """Verifica si hay filtraciones sensibles."""
        return self.breaches.filter(is_sensitive=True).exists()
    
    @property
    def risk_level(self):
        """Calcula el nivel de riesgo basado en las filtraciones."""
        if not self.breaches.exists():
            return "low"
        
        # Factores de riesgo
        sensitive_count = self.breaches.filter(is_sensitive=True).count()
        total_count = self.breaches.count()
        
        if sensitive_count >= 2 or total_count >= 5:
            return "critical"
        elif sensitive_count >= 1 or total_count >= 3:
            return "high"
        elif total_count >= 1:
            return "medium"
        else:
            return "low"
