from django.shortcuts import render
from core.models.tool import Tool

def tools_list(request):
    """Vista para mostrar la lista de herramientas recomendadas."""
    # Obtener herramientas por categoría
    vpn_tools = Tool.objects.filter(category='vpn')
    antivirus_tools = Tool.objects.filter(category='antivirus')
    password_tools = Tool.objects.filter(category='password')
    encryption_tools = Tool.objects.filter(category='encryption')
    firewall_tools = Tool.objects.filter(category='firewall')
    other_tools = Tool.objects.filter(category='other')
    
    # Herramientas destacadas
    featured_tools = Tool.objects.filter(is_featured=True)
    
    context = {
        'vpn_tools': vpn_tools,
        'antivirus_tools': antivirus_tools,
        'password_tools': password_tools,
        'encryption_tools': encryption_tools,
        'firewall_tools': firewall_tools,
        'other_tools': other_tools,
        'featured_tools': featured_tools,
    }
    
    return render(request, 'core/tools/tools_list.html', context)
