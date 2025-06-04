from django.db import models
import uuid

class Breach(models.Model):
    """Modelo para almacenar información de filtraciones de datos."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, null=True, blank=True)
    breach_date = models.DateField(null=True, blank=True)
    added_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    data_classes = models.JSONField(default=list)
    
    # Flags de estado
    is_verified = models.BooleanField(default=True)
    is_fabricated = models.BooleanField(default=False)
    is_sensitive = models.BooleanField(default=False)
    is_retired = models.BooleanField(default=False)
    is_spam_list = models.BooleanField(default=False)
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Filtración"
        verbose_name_plural = "Filtraciones"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['domain']),
            models.Index(fields=['breach_date']),
            models.Index(fields=['is_sensitive']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.domain or 'Sin dominio'})"
    
    @property
    def severity(self):
        """Determina la severidad de la filtración basada en sus características."""
        if self.is_sensitive:
            return "high"
        elif self.is_spam_list:
            return "low"
        else:
            return "medium"
    
    @property
    def severity_color(self):
        """Devuelve el color asociado a la severidad para uso en UI."""
        severity_colors = {
            "high": "danger",    # Rojo
            "medium": "warning", # Amarillo
            "low": "secondary"   # Verde
        }
        return severity_colors.get(self.severity, "neutral")
