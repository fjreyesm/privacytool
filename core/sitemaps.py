from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from core.models.blog import BlogPost

class StaticViewSitemap(Sitemap):
    """Sitemap para páginas estáticas"""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return [
            'core:index',
            'core:verification_home', 
            'core:tools_list',
            'core:blog_list',
            'core:terms_of_use',
            'core:faq',
            'core:privacy_policy',
            'core:politica-cookies',
        ]
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return timezone.now()

class BlogPostSitemap(Sitemap):
    """Sitemap para artículos de blog"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return BlogPost.objects.filter(is_published=True).order_by('-published_at')
    
    def lastmod(self, obj):
        return obj.updated_at or obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()
    
    def priority(self, obj):
        # Los artículos destacados tienen mayor prioridad
        return 0.8 if obj.is_featured else 0.6

# Diccionario de sitemaps para Django
sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
}
