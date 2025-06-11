from django.contrib import admin
#from core.models import Breach, Verification, Tool, BlogCategory, BlogPost
from core.models.breach import Breach
from core.models.verification import Verification
from core.models.tool import Tool
from core.models.blog import BlogCategory, BlogPost 
# Register your models here.

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

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rating', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('is_featured',)

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'is_featured', 'published_at')
    list_filter = ('is_published', 'is_featured', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'is_featured')
    date_hierarchy = 'published_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'content', 'excerpt', 'featured_image')
        }),
        ('Opciones de publicación', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
    )
