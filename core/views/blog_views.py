from django.shortcuts import render, get_object_or_404
from core.models.blog import BlogPost, BlogCategory

def blog_list(request):
    """Vista para mostrar la lista de artículos del blog."""
    # Obtener artículos publicados
    posts = BlogPost.objects.filter(is_published=True)
    
    # Artículos destacados
    featured_posts = posts.filter(is_featured=True)[:3]
    
    # Categorías
    categories = BlogCategory.objects.all()
    
    # Filtrar por categoría si se proporciona
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(BlogCategory, slug=category_slug)
        posts = posts.filter(category=category)
        context_category = category
    else:
        context_category = None
    
    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
        'current_category': context_category,
    }
    
    return render(request, 'core/blog/blog_list.html', context)

def blog_post_detail(request, slug):
    """Vista para mostrar un artículo específico del blog."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Artículos relacionados (misma categoría)
    related_posts = BlogPost.objects.filter(
        category=post.category, 
        is_published=True
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'core/blog/blog_post_detail.html', context)
