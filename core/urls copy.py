from django.urls import path
from core.views import verification_views, dashboard_views

app_name = 'core'

urlpatterns = [
    # Páginas principales
    path('', dashboard_views.index, name='index'),
    
    # Verificación
    path('verification/', verification_views.verification_home, name='verification_home'),
    path('verification/check/', verification_views.check_email_view, name='check_email'),
    path('breach/detail/<uuid:breach_id>/', verification_views.breach_detail, name='breach_detail'),
]
