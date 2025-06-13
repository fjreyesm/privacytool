from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings


from core.services.hibp_service import check_email
from core.services.report_service import generate_verification_report
from core.models.verification import Verification
from core.models.breach import Breach

@require_http_methods(["GET"])
def verification_home(request):
    """Vista principal de verificación."""
    return render(request, "verification/check.html")

@require_http_methods(["POST"])
# tu_app/views.py

def check_email_view(request):
    """Vista para verificar un email usando HTMX."""
    email = request.POST.get("email")
    if not email:
        return HttpResponse(
            "<div class='alert alert-danger'>Por favor, introduce un email válido.</div>",
            status=400
        )
    
    # Crear verificación en la base de datos
    verification = Verification.objects.create(
        email=email,
        user=request.user if request.user.is_authenticated else None,
        status="processing"
    )
    
    try:
        # Verificar email con HIBP
        breaches = check_email(email)
        
        # Actualizar verificación con resultados
        verification.status = "completed"
        verification.completed_at = timezone.now()
        verification.save()
        
        # Asociar filtraciones a la verificación
        if breaches:
            verification.breaches.set(breaches)
        
        # Renderizar resultados con HTMX
        context = {
            "verification": verification, 
            "breaches": breaches,
            "count": len(breaches) if breaches else 0,
        }
        return render(request, "verification/results_partial.html", context)

    except Exception as e:
        verification.status = "failed"
        verification.error_message = str(e)
        verification.save()
        
        return HttpResponse(
            f"<div class='alert alert-danger'>Error al verificar el email: {str(e)}</div>"
        )

@require_http_methods(["GET"])
def breach_detail(request, breach_id):
    """Vista para mostrar detalles de una filtración (cargada en modal vía HTMX)."""
    breach = get_object_or_404(Breach, id=breach_id)
    return render(request, "verification/breach_detail_modal.html", {"breach": breach})