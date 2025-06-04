from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.services.hibp_service import check_email
from core.services.report_service import generate_verification_report
from core.models.verification import Verification
from core.models.breach import Breach

@require_http_methods(["GET"])
def verification_home(request):
    """Vista principal de verificación."""
    return render(request, "core/verification/check.html")

@require_http_methods(["POST"])
def check_email_view(request):
    """Vista para verificar un email usando HTMX."""
    email = request.POST.get("email")
    if not email:
        return HttpResponse(
            "<div class='text-danger'>Por favor, introduce un email válido.</div>",
            headers={"HX-Trigger": '{"showToast": {"message": "Email inválido", "type": "error"}}'}
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
        return render(
            request,
            "core/verification/results_partial.html",
            {
                "verification": verification, 
                "breaches": breaches,
                "count": len(breaches)
            }
        )
    except Exception as e:
        verification.status = "failed"
        verification.error_message = str(e)
        verification.save()
        
        return HttpResponse(
            f"<div class='text-danger'>Error al verificar el email: {str(e)}</div>",
            headers={"HX-Trigger": f'{{"showToast": {{"message": "Error en la verificación: {str(e)}", "type": "error"}}}}'}
        )

@require_http_methods(["GET"])
def breach_detail(request, breach_id):
    """Vista para mostrar detalles de una filtración (cargada en modal vía HTMX)."""
    breach = get_object_or_404(Breach, id=breach_id)
    return render(request, "core/verification/breach_detail_modal.html", {"breach": breach})
