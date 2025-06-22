from django.db import models
import uuid
from django.utils.text import slugify
from django.urls import reverse
from django.utils.html import strip_tags

class BlogCategory(models.Model):
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
            # Limpiar HTML del contenido antes de crear el extracto
            clean_content = strip_tags(self.content)
            self.excerpt = clean_content[:200] + '...' if len(clean_content) > 200 else clean_content
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:blog_post_detail', kwargs={'slug': self.slug})
    
    def get_image_alt_text(self):
        """
        Genera un texto alt optimizado para la imagen destacada.
        Prioriza: extracto manual > extracto generado > título
        """
        if self.excerpt:
            # Limpiar HTML si existe en el extracto
            clean_excerpt = strip_tags(self.excerpt)
            # Truncar a 125 caracteres (límite recomendado para alt)
            if len(clean_excerpt) > 125:
                return clean_excerpt[:125].rsplit(' ', 1)[0] + '...'
            return clean_excerpt
        
        # Fallback al título si no hay extracto
        return f"Imagen del artículo: {self.title}"
    
    def get_short_excerpt(self, words=25):
        """
        Obtiene un extracto corto para meta descriptions, etc.
        """
        if self.excerpt:
            clean_excerpt = strip_tags(self.excerpt)
            words_list = clean_excerpt.split()
            if len(words_list) > words:
                return ' '.join(words_list[:words]) + '...'
            return clean_excerpt
        return f"Artículo sobre {self.title}"
