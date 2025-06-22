from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
import os

# Vista para servir robots.txt
@cache_control(max_age=86400)  # Cache por 24 horas
def robots_txt(request):
    robots_path = os.path.join(settings.BASE_DIR, 'static', 'robots.txt')
    try:
        with open(robots_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        return HttpResponse('User-agent: *\nDisallow:', content_type='text/plain')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('', include('core.urls')),
]

# Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
