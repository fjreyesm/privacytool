# Newsletter Views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django_ratelimit.decorators import ratelimit
import json
import logging

from .models import Subscriber, NewsletterCampaign
from .forms import SubscribeForm, QuickSubscribeForm, UnsubscribeForm

logger = logging.getLogger(__name__)


@ratelimit(key='ip', rate='5/m', method=['GET', 'POST'])
def subscribe_view(request):
    """Main subscription page with full form"""
    
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        
        if form.is_valid():
            # Get client info
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create subscriber
            subscriber = form.save(commit=False)
            subscriber.ip_address = ip_address
            subscriber.user_agent = user_agent
            subscriber.source = 'website'
            subscriber.save()
            
            # Send confirmation email
            try:
                send_confirmation_email(subscriber, request)
                
                messages.success(
                    request, 
                    '¡Gracias! Te hemos enviado un email de confirmación. '
                    'Revisa tu bandeja de entrada (y spam) para activar tu suscripción.'
                )
                
                logger.info(f"New subscription: {subscriber.email}")
                
                # HTMX response for modal/popup
                if request.headers.get('HX-Request'):
                    return render(request, 'newsletter/partials/success_message.html', {
                        'message': 'Email de confirmación enviado. ¡Revisa tu bandeja de entrada!'
                    })
                
                return redirect('newsletter:subscribe_success')
                
            except Exception as e:
                logger.error(f"Error sending confirmation email: {e}")
                messages.error(
                    request,
                    'Hubo un problema enviando el email de confirmación. '
                    'Por favor, intenta de nuevo más tarde.'
                )
        
        else:
            # Form has errors
            if request.headers.get('HX-Request'):
                return render(request, 'newsletter/partials/subscribe_form.html', {
                    'form': form
                })
    
    else:
        form = SubscribeForm()
    
    return render(request, 'newsletter/subscribe.html', {
        'form': form,
        'subscriber_count': Subscriber.objects.filter(status='active').count()
    })


@ratelimit(key='ip', rate='10/m', method=['POST'])
@require_http_methods(["POST"])
def quick_subscribe(request):
    """Quick subscription for footer, popups, etc."""
    
    form = QuickSubscribeForm(request.POST)
    
    if form.is_valid():
        email = form.cleaned_data['email']
        
        # Check if already exists
        existing = Subscriber.objects.filter(email=email).first()
        
        if existing:
            if existing.status == 'active':
                response_data = {
                    'success': False,
                    'message': 'Ya estás suscrito a nuestro newsletter.'
                }
            elif existing.status == 'pending':
                response_data = {
                    'success': False,
                    'message': 'Ya enviamos un email de confirmación. Revisa tu bandeja de entrada.'
                }
            else:
                # Reactivate unsubscribed user
                existing.status = 'pending'
                existing.subscribed_at = timezone.now()
                existing.save()
                
                try:
                    send_confirmation_email(existing, request)
                    response_data = {
                        'success': True,
                        'message': 'Email de confirmación enviado. ¡Revisa tu bandeja de entrada!'
                    }
                except Exception as e:
                    logger.error(f"Error sending confirmation email: {e}")
                    response_data = {
                        'success': False,
                        'message': 'Error enviando email. Intenta más tarde.'
                    }
        else:
            # Create new subscriber
            subscriber = Subscriber.objects.create(
                email=email,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                source=request.POST.get('source', 'quick_subscribe')
            )
            
            try:
                send_confirmation_email(subscriber, request)
                response_data = {
                    'success': True,
                    'message': '¡Gracias! Email de confirmación enviado.'
                }
                logger.info(f"Quick subscription: {subscriber.email}")
            except Exception as e:
                logger.error(f"Error sending confirmation email: {e}")
                response_data = {
                    'success': False,
                    'message': 'Error enviando email. Intenta más tarde.'
                }
    else:
        response_data = {
            'success': False,
            'message': 'Email inválido. Por favor, verifica e intenta de nuevo.'
        }
    
    # HTMX response
    if request.headers.get('HX-Request'):
        return render(request, 'newsletter/partials/quick_subscribe_response.html', 
                     response_data)
    
    return JsonResponse(response_data)


def confirm_subscription(request, token):
    """Confirm email subscription"""
    
    subscriber = get_object_or_404(Subscriber, confirmation_token=token)
    
    if subscriber.status == 'pending':
        subscriber.confirm_subscription()
        
        messages.success(
            request,
            '¡Suscripción confirmada! Bienvenido a nuestro newsletter. '
            'Recibirás contenido de calidad sobre privacidad y seguridad.'
        )
        
        logger.info(f"Subscription confirmed: {subscriber.email}")
        
        # Send welcome email (optional)
        try:
            send_welcome_email(subscriber, request)
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
    
    else:
        if subscriber.status == 'active':
            messages.info(request, 'Tu suscripción ya estaba confirmada.')
        else:
            messages.warning(request, 'Este enlace de confirmación no es válido.')
    
    return render(request, 'newsletter/confirmation_success.html', {
        'subscriber': subscriber
    })


def unsubscribe_view(request, token=None):
    """Unsubscribe from newsletter"""
    
    subscriber = None
    if token:
        subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
    
    if request.method == 'POST':
        if subscriber:
            # Direct unsubscribe via token
            reason = request.POST.get('reason', '')
            feedback = request.POST.get('feedback', '')
            
            subscriber.unsubscribe()
            
            # Log unsubscribe reason (for analytics)
            logger.info(f"Unsubscribe: {subscriber.email}, reason: {reason}")
            
            messages.success(
                request,
                'Te has dado de baja exitosamente. Lamentamos verte partir.'
            )
            
            return render(request, 'newsletter/unsubscribe_success.html')
        
        else:
            # Unsubscribe via email form
            form = UnsubscribeForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                try:
                    subscriber = Subscriber.objects.get(email=email, status='active')
                    subscriber.unsubscribe()
                    
                    messages.success(
                        request,
                        f'Email {email} dado de baja exitosamente.'
                    )
                    
                    return render(request, 'newsletter/unsubscribe_success.html')
                    
                except Subscriber.DoesNotExist:
                    messages.error(
                        request,
                        'Este email no está suscrito a nuestro newsletter.'
                    )
            
            return render(request, 'newsletter/unsubscribe.html', {'form': form})
    
    else:
        if subscriber and subscriber.status == 'active':
            # Show confirmation page
            return render(request, 'newsletter/unsubscribe_confirm.html', {
                'subscriber': subscriber
            })
        else:
            # Show email form
            form = UnsubscribeForm()
            return render(request, 'newsletter/unsubscribe.html', {'form': form})


def subscribe_success(request):
    """Success page after subscription"""
    return render(request, 'newsletter/subscribe_success.html')


# === UTILITY FUNCTIONS ===

def get_client_ip(request):
    """Get real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_confirmation_email(subscriber, request):
    """Send confirmation email to subscriber"""
    
    confirmation_url = request.build_absolute_uri(
        reverse('newsletter:confirm', kwargs={'token': subscriber.confirmation_token})
    )
    
    context = {
        'subscriber': subscriber,
        'confirmation_url': confirmation_url,
        'site_url': settings.SITE_URL,
    }
    
    # HTML version
    html_message = render_to_string('newsletter/emails/confirmation.html', context)
    
    # Text version
    text_message = render_to_string('newsletter/emails/confirmation.txt', context)
    
    send_mail(
        subject='Confirma tu suscripción - PrivacyTool Newsletter',
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscriber.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_welcome_email(subscriber, request):
    """Send welcome email after confirmation"""
    
    unsubscribe_url = request.build_absolute_uri(
        reverse('newsletter:unsubscribe_token', kwargs={'token': subscriber.unsubscribe_token})
    )
    
    context = {
        'subscriber': subscriber,
        'unsubscribe_url': unsubscribe_url,
        'site_url': settings.SITE_URL,
    }
    
    html_message = render_to_string('newsletter/emails/welcome.html', context)
    text_message = render_to_string('newsletter/emails/welcome.txt', context)
    
    send_mail(
        subject='¡Bienvenido a PrivacyTool Newsletter!',
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscriber.email],
        html_message=html_message,
        fail_silently=True,  # Welcome email is not critical
    )


# === API ENDPOINTS ===

@require_http_methods(["GET"])
def subscriber_stats(request):
    """API endpoint for subscriber statistics"""
    
    stats = {
        'total_subscribers': Subscriber.objects.filter(status='active').count(),
        'pending_confirmations': Subscriber.objects.filter(status='pending').count(),
        'total_campaigns': NewsletterCampaign.objects.filter(status='sent').count(),
    }
    
    return JsonResponse(stats)
