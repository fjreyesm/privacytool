from core.views.verification_views import verification_home, check_email_view, breach_detail
from core.views.dashboard_views import index
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
]