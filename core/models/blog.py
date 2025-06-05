from django.db import models
import uuid
from django.utils.text import slugify
from django.urls import reverse

class BlogCategory(models.Model ):
    """Modelo para categorías de blog."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    
    class Meta:
        verbose_name = "Categoría de Blog"
        verbose_name_plural = "Categorías de Blog"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class BlogPost(models.Model):
    """Modelo para artículos de blog."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Contenido")
    excerpt = models.TextField(verbose_name="Extracto", blank=True, null=True)
    featured_image = models.ImageField(upload_to='blog/', verbose_name="Imagen Destacada", blank=True, null=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name="Categoría")
    is_published = models.BooleanField(default=True, verbose_name="Publicado")
    is_featured = models.BooleanField(default=False, verbose_name="Destacado")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Publicación")
    
    class Meta:
        verbose_name = "Artículo de Blog"
        verbose_name_plural = "Artículos de Blog"
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200] + '...' if len(self.content) > 200 else self.content
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:blog_post_detail', kwargs={'slug': self.slug})
