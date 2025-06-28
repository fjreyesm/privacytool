# core/views/verification_views.py - ACTUALIZADA

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_exempt

# Imports de Ratelimit
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

# Imports de tu aplicación
from core.services.hibp_service import HIBPService, check_hibp_service_status
from core.models.verification import Verification
from core.models.breach import Breach

# Import para newsletter
from newsletter.models import Subscriber
from newsletter.views import send_confirmation_email

import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def verification_home(request):
    """Vista principal de la página de verificación."""
    return render(request, "verification/check.html")


@ratelimit(key='ip', rate='15/m', block=True)
@require_http_methods(["POST"])
def check_email_view(request):
    """Vista para verificar un email usando HTMX, con límite de peticiones y manejo robusto de errores."""
    email = request.POST.get("email", "").strip()
    newsletter_subscription = request.POST.get("newsletter_subscription") == "on"
    
    if not email:
        return HttpResponse(
            "<div class='alert alert-danger'>"
            "<i class='fas fa-exclamation-triangle'></i> "
            "Por favor, introduce un email válido."
            "</div>",
            status=400
        )
    
    # Validación básica de email
    if '@' not in email or '.' not in email.split('@')[-1]:
        return HttpResponse(
            "<div class='alert alert-danger'>"
            "<i class='fas fa-exclamation-triangle'></i> "
            "El formato del email no es válido."
            "</div>",
            status=400
        )
    
    # Crear registro de verificación
    verification = None
    try:
        verification = Verification.objects.create(
            email=email,
            user=request.user if request.user.is_authenticated else None,
            status="processing"
        )
        
        logger.info(f"[Verification] Starting check for {email} - ID: {verification.id}")
        
        # Manejar suscripción al newsletter SI está marcada
        newsletter_result = None
        if newsletter_subscription:
            try:
                # Verificar si ya existe suscriptor
                subscriber, created = Subscriber.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name': '',
                        'status': 'pending',
                        'privacy_consent': True,
                        'interests': ['security']  # Default para verificaciones
                    }
                )
                
                if created:
                    # Enviar email de confirmación
                    send_confirmation_email(subscriber, request)
                    newsletter_result = "subscribed"
                    logger.info(f"[Newsletter] New subscription from verification: {email}")
                else:
                    newsletter_result = "already_subscribed"
                    logger.info(f"[Newsletter] Email already subscribed: {email}")
                    
            except Exception as e:
                logger.error(f"[Newsletter] Error subscribing {email}: {str(e)}")
                newsletter_result = "error"
        
        # Usar el nuevo servicio HIBP robusto
        hibp_service = HIBPService()
        result = hibp_service.check_email(email)
        
        # Actualizar verificación con resultados
        verification.status = "completed"
        verification.completed_at = timezone.now()
        
        # Manejar diferentes tipos de respuesta
        if result['status'] == 'service_unavailable':
            verification.status = "warning"
            verification.error_message = result.get('message', 'Service temporarily unavailable')
            verification.save()
            
            return HttpResponse(
                f"<div class='alert alert-warning'>"
                f"<i class='fas fa-exclamation-circle'></i> "
                f"{result['message']}<br>"
                f"<small class='text-muted'>Tu email será verificado cuando el servicio esté disponible.</small>"
                f"</div>"
            )
        
        breaches = result['breaches']
        breach_count = result['count']
        is_cached = result.get('cached', False)
        
        verification.save()
        
        # Asociar brechas encontradas con la verificación
        if breaches:
            verification.breaches.set(breaches)
        
        logger.info(f"[Verification] Completed for {email} - Found {breach_count} breaches")
        
        # Preparar contexto para el template
        context = {
            "email": email,
            "breaches": breaches,
            "count": breach_count,
            "verification_id": verification.id,
            "is_cached": is_cached,
            "status": result['status'],
            "newsletter_result": newsletter_result
        }
        
        return render(request, "verification/results_partial.html", context)

    except Ratelimited:
        if verification:
            verification.status = "rate_limited"
            verification.error_message = "Rate limit exceeded"
            verification.save()
            
        return HttpResponse(
            "<div class='alert alert-danger'>"
            "<i class='fas fa-clock'></i> "
            "Has excedido el límite de verificaciones. "
            "Por favor, inténtalo de nuevo en un minuto."
            "</div>",
            status=429
        )
    
    except Exception as e:
        logger.error(f"[Verification] Unexpected error for {email}: {str(e)}")
        
        if verification:
            verification.status = "failed"
            verification.error_message = str(e)
            verification.save()
        
        return HttpResponse(
            "<div class='alert alert-danger'>"
            "<i class='fas fa-exclamation-triangle'></i> "
            "Ha ocurrido un error inesperado al verificar el email. "
            "<small class='text-muted'>Por favor, inténtalo de nuevo más tarde.</small>"
            "</div>",
            status=500
        )


@require_http_methods(["GET"])
def service_status_view(request):
    """API endpoint para verificar el estado del servicio HIBP"""
    try:
        status = check_hibp_service_status()
        
        return JsonResponse({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"[ServiceStatus] Error checking status: {str(e)}")
        
        return JsonResponse({
            'status': 'error',
            'message': 'Unable to check service status',
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def recheck_email_view(request):
    """Vista para revericar un email, forzando bypass del caché"""
    email = request.POST.get("email", "").strip()
    verification_id = request.POST.get("verification_id")
    
    if not email:
        return HttpResponse(
            "<div class='alert alert-danger'>Email requerido para la reverificación.</div>",
            status=400
        )
    
    try:
        # Buscar la verificación original si se proporciona ID
        original_verification = None
        if verification_id:
            try:
                original_verification = Verification.objects.get(id=verification_id)
            except Verification.DoesNotExist:
                pass
        
        # Limpiar caché para forzar nueva verificación
        from django.core.cache import cache
        cache_key = f"hibp:email:{email.lower()}"
        cache.delete(cache_key)
        
        logger.info(f"[Recheck] Forcing fresh check for {email}")
        
        # Crear nueva verificación
        verification = Verification.objects.create(
            email=email,
            user=request.user if request.user.is_authenticated else None,
            status="processing"
        )
        
        # Usar servicio HIBP
        hibp_service = HIBPService()
        result = hibp_service.check_email(email)
        
        verification.status = "completed"
        verification.completed_at = timezone.now()
        
        if result['status'] == 'service_unavailable':
            verification.status = "warning"
            verification.error_message = result.get('message')
            verification.save()
            
            return HttpResponse(
                f"<div class='alert alert-warning'>"
                f"<i class='fas fa-exclamation-circle'></i> "
                f"Servicio temporalmente no disponible. Inténtalo más tarde."
                f"</div>"
            )
        
        breaches = result['breaches']
        verification.save()
        
        if breaches:
            verification.breaches.set(breaches)
        
        context = {
            "email": email,
            "breaches": breaches,
            "count": len(breaches),
            "verification_id": verification.id,
            "is_cached": False,
            "status": result['status'],
            "rechecked": True
        }
        
        return render(request, "verification/results_partial.html", context)
        
    except Exception as e:
        logger.error(f"[Recheck] Error for {email}: {str(e)}")
        
        if verification:
            verification.status = "failed"
            verification.error_message = str(e)
            verification.save()
        
        return HttpResponse(
            "<div class='alert alert-danger'>"
            "Error al reverificar el email. Inténtalo de nuevo."
            "</div>",
            status=500
        )


class BreachDetailView(DetailView):
    """
    Vista Basada en Clase para mostrar los detalles de una filtración específica.
    Busca un objeto Breach por su 'pk' desde la URL.
    """
    model = Breach
    template_name = 'verification/breach_detail_modal.html'
    context_object_name = 'breach'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar información adicional si es necesario
        breach = self.object
        context['formatted_date'] = breach.breach_date
        context['data_classes_list'] = breach.data_classes if breach.data_classes else []
        
        return context