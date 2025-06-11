from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from core.models.verification import Verification
from core.models.breach import Breach

def generate_verification_report(verification_id):
    """
    Genera un informe detallado de una verificación.
    
    Args:
        verification_id: ID de la verificación
        
    Returns:
        dict: Datos del informe
    """
    try:
        verification = Verification.objects.get(id=verification_id)
    except Verification.DoesNotExist:
        raise ValueError(f"Verificación no encontrada")
    
    # Obtener todas las filtraciones asociadas
    breaches = verification.breaches.all().order_by('-breach_date')
    
    # Calcular estadísticas
    stats = {
        'total_breaches': breaches.count(),
        'sensitive_breaches': breaches.filter(is_sensitive=True).count(),
        'oldest_breach': breaches.order_by('breach_date').first(),
        'newest_breach': breaches.order_by('-breach_date').first(),
        'common_data_classes': get_common_data_classes(breaches),
        'risk_level': calculate_risk_level(breaches),
    }
    
    # Generar recomendaciones basadas en las filtraciones
    recommendations = generate_recommendations(breaches)
    
    # Crear informe
    report = {
        'verification': verification,
        'breaches': breaches,
        'stats': stats,
        'recommendations': recommendations,
        'generated_at': timezone.now(),
    }
    
    return report

def get_common_data_classes(breaches):
    """
    Identifica las clases de datos más comunes en las filtraciones.
    
    Args:
        breaches: QuerySet de filtraciones
        
    Returns:
        list: Lista de clases de datos más comunes
    """
    data_class_count = {}
    
    for breach in breaches:
        for data_class in breach.data_classes:
            if data_class in data_class_count:
                data_class_count[data_class] += 1
            else:
                data_class_count[data_class] = 1
    
    # Ordenar por frecuencia
    sorted_data_classes = sorted(
        data_class_count.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    # Devolver las 5 más comunes
    return [item[0] for item in sorted_data_classes[:5]]

def calculate_risk_level(breaches):
    """
    Calcula el nivel de riesgo basado en las filtraciones.
    
    Args:
        breaches: QuerySet de filtraciones
        
    Returns:
        str: Nivel de riesgo ('low', 'medium', 'high', 'critical')
    """
    if not breaches:
        return 'low'
    
    # Factores de riesgo
    sensitive_count = breaches.filter(is_sensitive=True).count()
    recent_count = breaches.filter(breach_date__gte=timezone.now().date().replace(year=timezone.now().year - 1)).count()
    total_count = breaches.count()
    
    # Lógica de evaluación de riesgo
    if sensitive_count >= 2 or (sensitive_count >= 1 and recent_count >= 1) or total_count >= 5:
        return 'critical'
    elif sensitive_count >= 1 or recent_count >= 2 or total_count >= 3:
        return 'high'
    elif recent_count >= 1 or total_count >= 1:
        return 'medium'
    else:
        return 'low'

def generate_recommendations(breaches):
    """
    Genera recomendaciones personalizadas basadas en las filtraciones.
    
    Args:
        breaches: QuerySet de filtraciones
        
    Returns:
        list: Lista de recomendaciones
    """
    recommendations = []
    
    # Recomendaciones básicas
    recommendations.append({
        'title': 'Cambiar contraseñas',
        'description': 'Cambia tus contraseñas en todos los servicios afectados y en cualquier otro donde hayas usado la misma contraseña.',
        'priority': 'high'
    })
    
    # Verificar si hay filtraciones con contraseñas
    password_breach = any('Passwords' in breach.data_classes for breach in breaches)
    if password_breach:
        recommendations.append({
            'title': 'Usar un gestor de contraseñas',
            'description': 'Considera usar un gestor de contraseñas para generar y almacenar contraseñas únicas y seguras para cada servicio.',
            'priority': 'high'
        })
    
    # Verificar si hay filtraciones con datos financieros
    financial_breach = any(any(data in breach.data_classes for data in ['Credit Cards', 'Banking Details', 'Financial Information']) for breach in breaches)
    if financial_breach:
        recommendations.append({
            'title': 'Monitorear cuentas financieras',
            'description': 'Revisa tus estados de cuenta bancarios y tarjetas de crédito para detectar transacciones sospechosas.',
            'priority': 'critical'
        })
    
    # Recomendación de autenticación de dos factores
    recommendations.append({
        'title': 'Activar autenticación de dos factores',
        'description': 'Activa la autenticación de dos factores en todos los servicios que lo permitan para añadir una capa extra de seguridad.',
        'priority': 'medium'
    })
    
    return recommendations
