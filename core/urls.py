from core.views.verification_views import verification_home, check_email_view, breach_detail
from core.views.dashboard_views import index
from core.views import verification_views, dashboard_views, tools_views, blog_views
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Páginas principales
    path('', index, name='index'),
    
    # Verificación
    path('verification/', verification_home, name='verification_home'),
    path('verification/check/', check_email_view, name='check_email'),
    path('breach/detail/<uuid:breach_id>/', breach_detail, name='breach_detail'),

        # Herramientas
    path('tools/', tools_views.tools_list, name='tools_list'),
    
    # Blog
    path('blog/', blog_views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', blog_views.blog_post_detail, name='blog_post_detail'),
]