# Newsletter Forms
from django import forms
from django.core.validators import EmailValidator
from .models import Subscriber


class SubscribeForm(forms.ModelForm):
    """Form for newsletter subscription"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email',
        }),
        validators=[EmailValidator()],
        help_text='Nunca compartiremos tu email. Cancela cuando quieras.'
    )
    
    first_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Tu nombre (opcional)',
            'autocomplete': 'given-name',
        })
    )
    
    interests = forms.MultipleChoiceField(
        choices=Subscriber.INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox text-primary',
        }),
        required=False,
        help_text='Selecciona tus intereses para contenido personalizado'
    )
    
    # Campo honeypot para spam protection
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    # GDPR compliance
    privacy_consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox text-primary',
        }),
        label='Acepto recibir emails informativos y puedo cancelar en cualquier momento.',
        error_messages={
            'required': 'Debes aceptar para continuar.'
        }
    )
    
    class Meta:
        model = Subscriber
        fields = ['email', 'first_name', 'interests']
    
    def clean_website(self):
        """Honeypot field - should be empty"""
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError('Spam detected')
        return website
    
    def clean_email(self):
        """Check for existing subscriptions"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if already subscribed
            existing = Subscriber.objects.filter(email=email).first()
            if existing:
                if existing.status == 'active':
                    raise forms.ValidationError(
                        'Este email ya está suscrito a nuestro newsletter.'
                    )
                elif existing.status == 'pending':
                    raise forms.ValidationError(
                        'Ya enviamos un email de confirmación a esta dirección. Revisa tu bandeja de entrada.'
                    )
                elif existing.status == 'unsubscribed':
                    # Allow re-subscription
                    pass
        return email


class QuickSubscribeForm(forms.Form):
    """Simplified form for popups and quick subscribe"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'flex-1 px-4 py-3 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email',
        }),
        validators=[EmailValidator()]
    )
    
    # Honeypot
    website = forms.CharField(required=False, widget=forms.HiddenInput())
    
    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError('Spam detected')
        return website


class UnsubscribeForm(forms.Form):
    """Form for unsubscribing"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'placeholder': 'tu@email.com',
        }),
        help_text='Introduce el email que quieres dar de baja'
    )
    
    reason = forms.ChoiceField(
        choices=[
            ('too_frequent', 'Demasiados emails'),
            ('not_relevant', 'Contenido no relevante'),
            ('privacy', 'Preocupaciones de privacidad'),
            ('other', 'Otro motivo'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
        }),
        help_text='Ayúdanos a mejorar (opcional)'
    )
    
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'rows': 3,
            'placeholder': 'Comentarios adicionales (opcional)',
        })
    )
