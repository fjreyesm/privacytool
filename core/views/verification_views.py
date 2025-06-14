from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.views.generic import DetailView

# Imports de Ratelimit
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

# Imports de tu aplicación
from core.services.hibp_service import check_email
from core.models.verification import Verification
from core.models.breach import Breach


@require_http_methods(["GET"])
def verification_home(request):
    """Vista principal de la página de verificación."""
    return render(request, "verification/check.html")


@ratelimit(key='ip', rate='5/m', block=True)
@require_http_methods(["POST"])
def check_email_view(request):
    """Vista para verificar un email usando HTMX, con límite de peticiones."""
    email = request.POST.get("email")
    if not email:
        return HttpResponse(
            "<div class='alert alert-danger'>Por favor, introduce un email válido.</div>",
            status=400
        )
    
    try:
        verification = Verification.objects.create(
            email=email,
            user=request.user if request.user.is_authenticated else None,
            status="processing"
        )
        
        breaches = check_email(email)
        
        verification.status = "completed"
        verification.completed_at = timezone.now()
        verification.save()
        
        if breaches:
            verification.breaches.set(breaches)
        
        context = {
            "breaches": breaches,
            "count": len(breaches) if breaches else 0,
        }
        return render(request, "verification/results_partial.html", context)

    except Ratelimited:
        return HttpResponse(
            "<div class='alert alert-danger'>Has excedido el límite de verificaciones. Por favor, inténtalo de nuevo en un minuto.</div>",
            status=429
        )
    except Exception as e:
        verification.status = "failed"
        verification.error_message = str(e)
        verification.save()
        
        return HttpResponse(
            f"<div class='alert alert-danger'>Ha ocurrido un error inesperado al verificar el email.</div>"
        )


class BreachDetailView(DetailView):
    """
    Vista Basada en Clase para mostrar los detalles de una filtración específica.
    Busca un objeto Breach por su 'pk' desde la URL.
    """
    model = Breach
    template_name = 'verification/breach_detail_modal.html'
    context_object_name = 'breach'