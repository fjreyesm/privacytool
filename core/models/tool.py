from django.db import models
import uuid

class Tool(models.Model):
    """Modelo para herramientas de seguridad recomendadas."""
    
    CATEGORY_CHOICES = [
        ('vpn', 'VPN'),
        ('antivirus', 'Antivirus'),
        ('password', 'Gestores de Contraseñas'),
        ('encryption', 'Encriptación'),
        ('firewall', 'Firewalls'),
        ('other', 'Otras'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Categoría")
    description = models.TextField(verbose_name="Descripción")
    url = models.URLField(verbose_name="URL")
    affiliate_url = models.URLField(blank=True, null=True, verbose_name="URL de Afiliado")
    image = models.ImageField(upload_to='tools/', blank=True, null=True, verbose_name="Imagen")
    is_featured = models.BooleanField(default=False, verbose_name="Destacada")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name="Valoración (1-5)")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Herramienta"
        verbose_name_plural = "Herramientas"
        ordering = ['-is_featured', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def display_url(self):
        """Devuelve la URL de afiliado si existe, de lo contrario la URL normal."""
        return self.affiliate_url or self.url
