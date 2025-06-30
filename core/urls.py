from core.views.verification_views import (
    verification_home, 
    check_email_view, 
    BreachDetailView,
    service_status_view,
    recheck_email_view
)
from core.views.dashboard_views import index
from core.views import verification_views, dashboard_views, tools_views, blog_views
from core.views.views import terms_of_use_view,faq_view,privacy_policy_view, PoliticaCookiesView  # Importación específica
from django.urls import path

app_name = 'core'

urlpatterns = [
    # Páginas principales
    path('', index, name='index'),
    
    # Verificación
    path('verification/', verification_home, name='verification_home'),
    path('verification/check/', check_email_view, name='check_email'),
    path('verification/recheck/', recheck_email_view, name='recheck_email'),
    path('verification/status/', service_status_view, name='service_status'),
    path('breach/detail/<uuid:pk>/', BreachDetailView.as_view(), name='breach_detail'),
    
    # Herramientas
    path('tools/', tools_views.tools_list, name='tools_page'),
    path('tools/category/<slug:category_slug>/', tools_views.tools_list, name='tools_category_page'),
    
    # Blog
    path('blog/', blog_views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', blog_views.blog_post_detail, name='blog_post_detail'),
    
    # Páginas estáticas
    path('terminos/', terms_of_use_view, name='terms_of_use'),
    path('faq/', faq_view, name='faq'),
    path('privacidad/', privacy_policy_view, name='privacy_policy'),
    path('politica-cookies/', PoliticaCookiesView.as_view(), name='politica-cookies'),

]
