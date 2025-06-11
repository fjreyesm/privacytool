from django.core.cache import cache
import requests
import logging
from django.conf import settings
from core.models.breach import Breach

logger = logging.getLogger(__name__)

def check_email(email):
    """
    Consulta la API de HIBP para verificar si un email ha sido comprometido.
    Utiliza caché para almacenar resultados temporalmente.
    
    Args:
        email (str): El email a verificar.
        
    Returns:
        list: Lista de objetos Breach encontrados.
        
    Raises:
        Exception: Si hay un error en la consulta.
    """
    if not settings.HIBP_API_KEY:
        logger.error("CRITICAL: La HIBP_API_KEY no está configurada en las variables de entorno.")
        raise Exception("Servicio HIBP no disponible por falta de API Key.")
    
    # Clave de caché para este email
    cache_key = f"hibp:email:{email}"
    
    # Intentar obtener resultado desde caché
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"[HIBP Service] Cache HIT para el email: {email}")
        # Convertir IDs cacheados a objetos Breach
        if isinstance(cached_result, list) and not cached_result:
            return []
        return list(Breach.objects.filter(id__in=cached_result))
    
    logger.info(f"[HIBP Service] Cache MISS para el email: {email}. Consultando API HIBP...")
    
    # Configuración de cabeceras para HIBP
    headers = {
        'hibp-api-key': settings.HIBP_API_KEY,
        'User-Agent': 'SecureCheck/1.0 (Django; contacto@securecheck.com)'
    }
    
    try:
        # Realizar petición a la API de HIBP
        response = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers=headers,
            params={'truncateResponse': 'false'}
        )
        
        # Si el email no está en ninguna filtración (404)
        if response.status_code == 404:
            logger.info(f"[HIBP Service] Email {email} no encontrado en brechas (404). Cacheando resultado negativo.")
            # Cachear resultado negativo por 15 minutos
            cache.set(cache_key, [], timeout=60 * 15)
            return []
        
        # Si hay otro error
        response.raise_for_status()
        
        # Procesar respuesta exitosa
        breach_data = response.json()
        logger.info(f"[HIBP Service] Datos crudos de la API para {email}: {breach_data}")
        breach_objects = []
        breach_ids = []
        
        # Crear o actualizar objetos Breach en la base de datos
        for breach in breach_data:
            breach_obj, created = Breach.objects.update_or_create(
                name=breach['Name'],
                defaults={
                    'domain': breach.get('Domain'),
                    'breach_date': breach.get('BreachDate'),
                    'pwn_count': breach.get('PwnCount', 0),
                    'added_date': breach.get('AddedDate'),
                    'added_date': breach.get('AddedDate'),
                    'description': breach.get('Description'),
                    'data_classes': breach.get('DataClasses', []),
                    'is_verified': breach.get('IsVerified', True),
                    'is_fabricated': breach.get('IsFabricated', False),
                    'is_sensitive': breach.get('IsSensitive', False),
                    'is_retired': breach.get('IsRetired', False),
                    'is_spam_list': breach.get('IsSpamList', False)
                }
            )
            breach_objects.append(breach_obj)
            breach_ids.append(breach_obj.id)
        
        logger.info(f"[HIBP Service] Respuesta de API para {email} guardada en caché.")
        # Cachear IDs de filtraciones por 1 hora
        cache.set(cache_key, breach_ids, timeout=60 * 60)
        return breach_objects
        
    except requests.exceptions.RequestException as e:
        # Manejar errores de red o API
        logger.error(f"[HIBP Service] Error al consultar HIBP para {email}: {str(e)}")
        raise Exception(f"Error al consultar HIBP: {str(e)}")
