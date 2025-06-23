# Newsletter URLs
from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # Main subscription page
    path('', views.subscribe_view, name='subscribe'),
    path('subscribe/', views.subscribe_view, name='subscribe_main'),
    path('success/', views.subscribe_success, name='subscribe_success'),
    
    # Quick subscribe (HTMX/AJAX)
    path('quick-subscribe/', views.quick_subscribe, name='quick_subscribe'),
    
    # Email confirmation
    path('confirm/<uuid:token>/', views.confirm_subscription, name='confirm'),
    
    # Unsubscribe
    path('unsubscribe/', views.unsubscribe_view, name='unsubscribe'),
    path('unsubscribe/<uuid:token>/', views.unsubscribe_view, name='unsubscribe_token'),
    
    # API endpoints
    path('api/stats/', views.subscriber_stats, name='api_stats'),
]
