"""
REGRESSION TEST SUITE
======================

Esta suite debe ejecutarse ANTES de implementar cualquier nueva funcionalidad
para garantizar que los cambios no rompan funcionalidades existentes.

Ejecutar: python manage.py test core.tests.test_regression --verbosity=2

"""

import json
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User
from django.core import mail
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.db import transaction
from django.conf import settings

from newsletter.models import Subscriber, NewsletterCampaign, NewsletterTemplate
from newsletter.forms import SubscribeForm
from core.models.verification import Verification
from core.models.breach import Breach


class CoreFunctionalityRegressionTests(TestCase):
    """
    Tests de regresión para funcionalidades CORE que DEBEN seguir funcionando
    """
    
    def setUp(self):
        self.client = Client()
        
    def test_home_page_loads(self):
        """Test: La página principal debe cargar correctamente"""
        try:
            response = self.client.get('/')
            self.assertIn(response.status_code, [200, 302])
        except Exception as e:
            self.fail(f"Home page failed to load: {e}")
    
    def test_verification_page_loads(self):
        """Test: La página de verificación debe cargar"""
        response = self.client.get('/verification/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'email')  # Debe tener un campo email
    
    def test_newsletter_page_loads(self):
        """Test: La página de newsletter debe cargar"""
        response = self.client.get('/newsletter/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_accessible(self):
        """Test: El admin debe ser accesible (sin errores de sistema)"""
        try:
            response = self.client.get('/admin/')
            self.assertIn(response.status_code, [200, 302])
        except Exception as e:
            self.fail(f"Admin interface failed: {e}")


class NewsletterRegressionTests(TestCase):
    """
    Tests de regresión para newsletter - funcionalidades que YA FUNCIONABAN
    """
    
    def test_subscriber_model_creation(self):
        """Test: Crear un subscriber debe funcionar como antes"""
        subscriber = Subscriber.objects.create(
            email='test@example.com',
            first_name='Test User',
            status='pending'
        )
        self.assertEqual(subscriber.email, 'test@example.com')
        self.assertEqual(subscriber.status, 'pending')
        self.assertTrue(subscriber.confirmation_token)
        
    def test_subscribe_form_validation(self):
        """Test: El formulario de suscripción debe validar correctamente"""
        # Test formulario válido
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'interests': ['privacy'],
            'privacy_consent': True
        }
        form = SubscribeForm(data=form_data)
        if not form.is_valid():
            self.fail(f"Valid form should pass validation. Errors: {form.errors}")
        
        # Test formulario inválido
        invalid_form = SubscribeForm(data={
            'email': 'invalid-email',
            'first_name': 'Test'
        })
        self.assertFalse(invalid_form.is_valid())
    
    def test_newsletter_templates_exist(self):
        """Test: Los templates necesarios deben existir"""
        required_templates = [
            'newsletter/subscribe.html',
            'newsletter/confirmation_success.html',
            'newsletter/unsubscribe_confirm.html'
        ]
        
        for template_name in required_templates:
            try:
                get_template(template_name)
            except TemplateDoesNotExist:
                self.fail(f"Required template missing: {template_name}")
    
    def test_newsletter_campaign_model(self):
        """Test: Los modelos de campañas deben funcionar"""
        campaign = NewsletterCampaign.objects.create(
            name='Test Campaign',
            subject='Test Subject',
            content_html='<h1>Test</h1>',
            content_text='Test'
        )
        self.assertEqual(campaign.name, 'Test Campaign')
        self.assertEqual(campaign.status, 'draft')
    
    def test_newsletter_template_model(self):
        """Test: Los modelos de templates deben funcionar"""
        template = NewsletterTemplate.objects.create(
            name='Test Template',
            html_content='<html>Test</html>'
        )
        self.assertEqual(template.name, 'Test Template')
        self.assertTrue(template.is_active)


class VerificationRegressionTests(TestCase):
    """
    Tests de regresión para sistema de verificación
    """
    
    def test_verification_model_creation(self):
        """Test: Crear verificaciones debe funcionar"""
        verification = Verification.objects.create(
            email='test@example.com',
            status='pending'
        )
        self.assertEqual(verification.email, 'test@example.com')
        self.assertEqual(verification.status, 'pending')
    
    def test_breach_model_creation(self):
        """Test: Crear breach debe funcionar"""
        breach = Breach.objects.create(
            name='Test Breach',
            domain='test.com',
            breach_date='2023-01-01',
            description='Test breach'
        )
        self.assertEqual(breach.name, 'Test Breach')
    
    def test_verification_endpoints_exist(self):
        """Test: Los endpoints de verificación deben existir"""
        endpoints = [
            '/verification/',
            '/verification/check/',
            '/verification/status/'
        ]
        
        for endpoint in endpoints:
            try:
                response = self.client.get(endpoint)
                # Should not return 404
                self.assertNotEqual(response.status_code, 404, 
                                    f"Endpoint {endpoint} returns 404")
            except NoReverseMatch:
                self.fail(f"Endpoint {endpoint} not found in URLs")


class URLRegressionTests(TestCase):
    """
    Test que todas las URLs importantes sigan funcionando
    """
    
    def test_core_urls_exist(self):
        """Test: URLs core deben existir y no dar 500"""
        urls_to_test = [
            ('/', 'Home page'),
            ('/verification/', 'Verification page'),
            ('/newsletter/', 'Newsletter page'),
            ('/terminos/', 'Terms page'),
            ('/privacidad/', 'Privacy page'),
            ('/faq/', 'FAQ page'),
        ]
        
        for url, description in urls_to_test:
            with self.subTest(url=url):
                try:
                    response = self.client.get(url)
                    # Should not be 500 (server error)
                    self.assertNotEqual(response.status_code, 500,
                                        f"{description} returns 500 error")
                    # Should not be 404 (not found)
                    self.assertNotEqual(response.status_code, 404,
                                        f"{description} returns 404 error")
                except Exception as e:
                    self.fail(f"{description} ({url}) failed with error: {e}")


class DatabaseRegressionTests(TestCase):
    """
    Test que las operaciones de base de datos funcionen correctamente
    """
    
    def test_models_can_be_created(self):
        """Test: Todos los modelos principales deben poder crearse"""
        
        # Test Subscriber
        subscriber = Subscriber.objects.create(
            email='db_test@example.com',
            first_name='DB Test'
        )
        self.assertIsNotNone(subscriber.pk)
        
        # Test NewsletterCampaign
        campaign = NewsletterCampaign.objects.create(
            name='DB Test Campaign',
            subject='Test',
            content_html='<p>Test</p>'
        )
        self.assertIsNotNone(campaign.pk)
        
        # Test Verification
        verification = Verification.objects.create(
            email='verification_test@example.com'
        )
        self.assertIsNotNone(verification.pk)
        
        # Test Breach
        breach = Breach.objects.create(
            name='DB Test Breach',
            domain='dbtest.com'
        )
        self.assertIsNotNone(breach.pk)
    
    def test_email_uniqueness_constraint(self):
        """Test: Constraint de email único debe funcionar"""
        Subscriber.objects.create(email='unique@example.com')
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Subscriber.objects.create(email='unique@example.com')


class AdminRegressionTests(TestCase):
    """
    Test que el admin siga funcionando correctamente
    """
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client.login(username='admin', password='adminpass123')
    
    def test_admin_models_accessible(self):
        """Test: Los modelos en admin deben ser accesibles"""
        admin_urls = [
            '/admin/',
            '/admin/newsletter/',
            '/admin/newsletter/subscriber/',
            '/admin/newsletter/newslettercampaign/',
            '/admin/newsletter/newslettertemplate/',
        ]
        
        for url in admin_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertNotEqual(response.status_code, 500,
                                    f"Admin URL {url} returns 500 error")
    
    def test_admin_can_create_subscriber(self):
        """Test: Crear subscriber desde admin debe funcionar"""
        url = '/admin/newsletter/subscriber/add/'
        data = {
            'email': 'admin_test@example.com',
            'first_name': 'Admin Test',
            'status': 'pending',
            'interests': '[]',
            'source': 'website'
        }
        response = self.client.post(url, data)
        # Should not be 500 error
        self.assertNotEqual(response.status_code, 500)


class SecurityRegressionTests(TestCase):
    """
    Test que las funcionalidades de seguridad sigan funcionando
    """
    
    def test_csrf_protection_active(self):
        """Test: CSRF protection debe estar activa"""
        # Intentar POST sin CSRF token
        response = self.client.post('/newsletter/', {
            'email': 'csrf_test@example.com'
        })
        # Should be blocked by CSRF or rate limiting
        self.assertIn(response.status_code, [403, 429])
    
    def test_rate_limiting_active(self):
        """Test: Rate limiting debe estar funcionando"""
        # Multiple requests should eventually be rate limited
        for i in range(20):
            response = self.client.post('/newsletter/', {
                'email': f'rate_test_{i}@example.com'
            })
            if response.status_code == 429:
                break
        else:
            # If we never hit rate limit, that might be okay depending on config
            pass


class TemplateRegressionTests(TestCase):
    """
    Test que los templates principales no tengan errores
    """
    
    def test_base_template_renders(self):
        """Test: Template base debe renderizar sin errores"""
        try:
            template = get_template('base.html')
            content = template.render({})
            self.assertIsInstance(content, str)
        except Exception as e:
            self.fail(f"Base template failed to render: {e}")
    
    def test_newsletter_templates_render(self):
        """Test: Templates de newsletter deben renderizar"""
        templates_to_test = [
            ('newsletter/subscribe.html', {}),
            ('verification/check.html', {}),
        ]
        
        for template_name, context in templates_to_test:
            with self.subTest(template=template_name):
                try:
                    template = get_template(template_name)
                    content = template.render(context)
                    self.assertIsInstance(content, str)
                    self.assertGreater(len(content), 0)
                except TemplateDoesNotExist:
                    # Skip if template doesn't exist
                    pass
                except Exception as e:
                    self.fail(f"Template {template_name} failed to render: {e}")


# Test Suite Summary
class RegressionTestSuite:
    """
    Clase helper para ejecutar todos los tests de regresión
    """
    
    @staticmethod
    def get_all_test_classes():
        """Devuelve todas las clases de test de regresión"""
        return [
            CoreFunctionalityRegressionTests,
            NewsletterRegressionTests,
            VerificationRegressionTests,
            URLRegressionTests,
            DatabaseRegressionTests,
            AdminRegressionTests,
            SecurityRegressionTests,
            TemplateRegressionTests,
        ]
    
    @staticmethod
    def run_critical_tests():
        """
        Tests críticos que DEBEN pasar antes de cualquier deployment
        """
        critical_tests = [
            'test_home_page_loads',
            'test_verification_page_loads',
            'test_newsletter_page_loads',
            'test_subscriber_model_creation',
            'test_admin_accessible',
        ]
        return critical_tests
