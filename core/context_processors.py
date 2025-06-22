from django.conf import settings


def site_settings(request):
    """
    Context processor que hace disponibles las configuraciones del sitio
    en todos los templates.
    """
    return {
        'SITE_URL': settings.SITE_URL,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'DEBUG': settings.DEBUG,
    }
