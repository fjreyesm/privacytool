# core/views.py

from django.shortcuts import render
from core.models.tool import Tool

def tools_list(request, category_slug=None):
    """
    Muestra la lista de herramientas, permitiendo filtrar por categoría.
    """
    
    # 1. Obtenemos la lista de categorías directamente del modelo Tool.
    #    Esto solucionará que los filtros NO aparezcan.
    categories = Tool.CATEGORY_CHOICES

    # 2. Obtenemos las herramientas destacadas.
    featured_tools = Tool.objects.filter(is_featured=True)

    # 3. Obtenemos el resto de herramientas para la lista principal.
    if category_slug:
        # Si se filtra, mostramos solo las de esa categoría.
        other_tools = Tool.objects.filter(is_featured=False, category=category_slug)
    else:
        # Si no, mostramos todas las no destacadas.
        other_tools = Tool.objects.filter(is_featured=False)
    
    # 4. Preparamos el contexto con los nombres que la plantilla espera.
    context = {
        'tool_categories': categories,
        'featured_tools': featured_tools,
        'tools': other_tools,
        'current_category': category_slug,
    }
    
    return render(request, 'tools/tools_list.html', context)