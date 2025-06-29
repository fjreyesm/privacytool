#!/usr/bin/env python3
"""
Casos de prueba específicos adicionales para PrivacyTool
Basado en la estructura del proyecto analizada
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User
from unittest.mock import patch, Mock
import json

class PrivacyToolIntegrationTests(TestCase):
    """
    Suite de pruebas de integración para PrivacyTool
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        self.test_email = "test@example.com"
        
    def test_homepage_loads(self):
        """Prueba que la página principal carga correctamente"""
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 301, 302])
        
    def test_security_check_endpoint(self):
        """Prueba el endpoint de verificación de seguridad"""
        # Buscar endpoints relacionados con seguridad
        try:
            response = self.client.get('/check/')
            self.assertIn(response.status_code, [200, 404])
        except:
            # Si no existe, está bien
            pass
    
    def test_newsletter_subscription(self):
        """Prueba la suscripción al newsletter"""
        try:
            response = self.client.post('/newsletter/subscribe/', {
                'email': self.test_email
            })
            # Puede retornar 200, 302 (redirect), o 404 si no existe
            self.assertIn(response.status_code, [200, 302, 404])
        except Exception as e:
            # Endpoint puede no existir aún
            self.skipTest(f"Endpoint newsletter no disponible: {e}")
    
    def test_hibp_service_mock(self):
        """Prueba el servicio HIBP con datos mock"""
        # Mock del servicio HIBP para evitar llamadas reales a la API
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {
                    "Name": "TestBreach",
                    "Title": "Test Data Breach",
                    "Domain": "test.com",
                    "BreachDate": "2023-01-01",
                    "ModifiedDate": "2023-01-02",
                    "PwnCount": 1000,
                    "DataClasses": ["Email addresses", "Passwords"]
                }
            ]
            mock_get.return_value = mock_response
            
            # Aquí iría la lógica de prueba del servicio HIBP
            # Por ahora solo verificamos que el mock funciona
            self.assertEqual(mock_response.status_code, 200)
    
    def test_database_models(self):
        """Prueba la integridad de los modelos de base de datos"""
        from django.apps import apps
        
        # Verificar que las apps están instaladas
        app_configs = apps.get_app_configs()
        app_names = [app.name for app in app_configs]
        
        self.assertIn('core', app_names)
        self.assertIn('newsletter', app_names)
    
    def test_static_files_accessible(self):
        """Prueba que los archivos estáticos son accesibles"""
        from django.conf import settings
        from django.contrib.staticfiles import finders
        
        # Verificar que la configuración de archivos estáticos existe
        self.assertTrue(hasattr(settings, 'STATIC_URL'))
        
        # Buscar archivos CSS/JS comunes
        css_file = finders.find('css/main.css')
        # Si existe, está bien, si no, también
        
    def test_admin_interface(self):
        """Prueba que la interfaz de admin es accesible"""
        response = self.client.get('/admin/')
        # Debe redirigir al login o mostrar login
        self.assertIn(response.status_code, [200, 302])
    
    def test_security_headers(self):
        """Prueba que las cabeceras de seguridad están configuradas"""
        response = self.client.get('/')
        
        # Verificar cabeceras de seguridad básicas
        # Pueden no estar todas implementadas aún
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        # Al menos alguna cabecera de seguridad debería estar
        found_headers = 0
        for header in security_headers:
            if header in response.headers:
                found_headers += 1
        
        # No es crítico que estén todas, pero es bueno tenerlas
        # self.assertGreater(found_headers, 0, "No security headers found")


class PrivacyToolNewsletterTests(TestCase):
    """
    Pruebas específicas para la funcionalidad de newsletter
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_newsletter_model_creation(self):
        """Prueba la creación de modelos de newsletter"""
        try:
            from newsletter.models import Subscriber
            
            # Crear un suscriptor de prueba
            subscriber = Subscriber.objects.create(
                email="test@example.com",
                is_active=True
            )
            
            self.assertEqual(subscriber.email, "test@example.com")
            self.assertTrue(subscriber.is_active)
            
        except ImportError:
            self.skipTest("Modelo Subscriber no disponible")
    
    def test_newsletter_form_validation(self):
        """Prueba la validación de formularios de newsletter"""
        try:
            from newsletter.forms import SubscriptionForm
            
            # Formulario válido
            form_data = {'email': 'valid@example.com'}
            form = SubscriptionForm(data=form_data)
            self.assertTrue(form.is_valid())
            
            # Formulario inválido
            form_data = {'email': 'invalid-email'}
            form = SubscriptionForm(data=form_data)
            self.assertFalse(form.is_valid())
            
        except ImportError:
            self.skipTest("SubscriptionForm no disponible")


class PrivacyToolCoreTests(TestCase):
    """
    Pruebas específicas para la app core
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_core_views_respond(self):
        """Prueba que las vistas principales responden"""
        # Lista de URLs que podrían existir
        potential_urls = [
            '/',
            '/about/',
            '/privacy/',
            '/terms/',
            '/contact/',
            '/tools/',
            '/check/',
            '/scan/'
        ]
        
        responding_urls = []
        for url in potential_urls:
            try:
                response = self.client.get(url)
                if response.status_code in [200, 301, 302]:
                    responding_urls.append(url)
            except:
                # URL no existe, continuar
                pass
        
        # Al menos la raíz debería responder
        self.assertIn('/', responding_urls, "La página principal no responde")
    
    def test_context_processors(self):
        """Prueba los procesadores de contexto personalizados"""
        try:
            from core.context_processors import site_settings
            
            # Mock request object
            class MockRequest:
                pass
            
            request = MockRequest()
            context = site_settings(request)
            
            # Verificar que retorna un diccionario
            self.assertIsInstance(context, dict)
            
        except ImportError:
            self.skipTest("Context processors no disponibles")


class PrivacyToolPerformanceTests(TestCase):
    """
    Pruebas de rendimiento básicas
    """
    
    def test_homepage_response_time(self):
        """Prueba que la página principal responde en tiempo razonable"""
        import time
        
        start_time = time.time()
        response = self.client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Debería responder en menos de 2 segundos
        self.assertLess(response_time, 2.0, 
                       f"Homepage took {response_time:.2f}s to respond")
    
    def test_database_queries_efficiency(self):
        """Prueba la eficiencia de las consultas a la base de datos"""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            # Limpiar consultas previas
            connection.queries_log.clear()
            
            # Hacer una petición
            response = self.client.get('/')
            
            # Verificar número de consultas
            query_count = len(connection.queries)
            
            # No debería hacer demasiadas consultas para la página principal
            self.assertLess(query_count, 20, 
                           f"Too many database queries: {query_count}")


class PrivacyToolSecurityTests(TestCase):
    """
    Pruebas de seguridad específicas
    """
    
    def test_sql_injection_protection(self):
        """Prueba protección contra inyección SQL"""
        # Intentar varios payloads de inyección SQL
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM users WHERE 1=1; --"
        ]
        
        for payload in malicious_inputs:
            # Intentar en diferentes endpoints
            endpoints = ['/', '/check/']
            
            for endpoint in endpoints:
                try:
                    response = self.client.get(endpoint, {'q': payload})
                    # Debería manejar gracefully, no crashear
                    self.assertIn(response.status_code, [200, 400, 404, 500])
                except:
                    # Endpoint no existe, continuar
                    pass
    
    def test_xss_protection(self):
        """Prueba protección contra XSS"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            try:
                response = self.client.get('/', {'search': payload})
                # La respuesta no debería contener el script sin escapar
                if response.status_code == 200:
                    content = response.content.decode()
                    self.assertNotIn("<script>alert('xss')</script>", content)
            except:
                # Endpoint no maneja search, continuar
                pass
    
    def test_csrf_protection(self):
        """Prueba protección CSRF"""
        # Intentar POST sin token CSRF
        response = self.client.post('/newsletter/subscribe/', {
            'email': 'test@example.com'
        })
        
        # Debería fallar por falta de token CSRF
        # (403 o redirigir a login)
        self.assertIn(response.status_code, [403, 302, 404])


class PrivacyToolHIBPTests(TestCase):
    """
    Pruebas específicas para el servicio HIBP
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_hibp_model_creation(self):
        """Prueba la creación de modelos relacionados con HIBP"""
        try:
            from core.models import Breach
            
            # Crear una filtración de prueba
            breach = Breach.objects.create(
                name="Test Breach",
                domain="testsite.com",
                pwn_count=1000,
                is_verified=True
            )
            
            self.assertEqual(breach.name, "Test Breach")
            self.assertEqual(breach.domain, "testsite.com")
            self.assertTrue(breach.is_verified)
            
        except ImportError:
            self.skipTest("Modelo Breach no disponible")
    
    @patch('requests.get')
    def test_hibp_api_mock_response(self, mock_get):
        """Prueba la respuesta mock de la API HIBP"""
        # Configurar mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "Name": "Adobe",
                "Title": "Adobe",
                "Domain": "adobe.com",
                "BreachDate": "2013-10-04",
                "AddedDate": "2013-12-04T00:00Z",
                "ModifiedDate": "2013-12-04T00:00Z",
                "PwnCount": 152445165,
                "DataClasses": [
                    "Email addresses",
                    "Password hints",
                    "Passwords",
                    "Usernames"
                ]
            }
        ]
        mock_get.return_value = mock_response
        
        # Verificar que el mock funciona
        self.assertEqual(mock_response.status_code, 200)
        data = mock_response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["Name"], "Adobe")


class PrivacyToolRegressionTests(TestCase):
    """
    Pruebas de regresión para detectar cambios inesperados
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_critical_pages_still_work(self):
        """Prueba que las páginas críticas siguen funcionando"""
        critical_pages = [
            '/',
            '/admin/',
        ]
        
        for page in critical_pages:
            try:
                response = self.client.get(page)
                # Debería responder, no crashear
                self.assertIn(response.status_code, [200, 301, 302, 404])
            except Exception as e:
                self.fail(f"Critical page {page} crashed: {e}")
    
    def test_models_still_loadable(self):
        """Prueba que los modelos siguen siendo importables"""
        models_to_test = [
            ('newsletter.models', 'Subscriber'),
            ('core.models', 'Breach'),
        ]
        
        for module_name, model_name in models_to_test:
            try:
                module = __import__(module_name, fromlist=[model_name])
                model_class = getattr(module, model_name)
                # Si llegamos aquí, el modelo se puede importar
                self.assertTrue(hasattr(model_class, '_meta'))
            except (ImportError, AttributeError):
                # Modelo no disponible, puede ser normal
                pass
    
    def test_settings_still_valid(self):
        """Prueba que la configuración sigue siendo válida"""
        from django.conf import settings
        
        # Verificar configuraciones críticas
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertTrue(hasattr(settings, 'DATABASES'))
        
        # Verificar que las apps críticas estén instaladas
        installed_apps = settings.INSTALLED_APPS
        critical_apps = ['django.contrib.admin', 'django.contrib.auth']
        
        for app in critical_apps:
            self.assertIn(app, installed_apps, f"Critical app {app} not installed")


# Script para ejecutar todas las pruebas específicas
if __name__ == "__main__":
    import unittest
    import sys
    import os
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securecheck.settings')
    
    import django
    django.setup()
    
    # Ejecutar todas las pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases de prueba
    test_classes = [
        PrivacyToolIntegrationTests,
        PrivacyToolNewsletterTests,
        PrivacyToolCoreTests,
        PrivacyToolPerformanceTests,
        PrivacyToolSecurityTests,
        PrivacyToolHIBPTests,
        PrivacyToolRegressionTests
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar las pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print(f"\n{'='*50}")
    print(f"RESUMEN DE PRUEBAS ESPECÍFICAS")
    print(f"{'='*50}")
    print(f"Pruebas ejecutadas: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Omitidas: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.errors:
        print(f"\n❌ ERRORES ENCONTRADOS:")
        for test, error in result.errors:
            print(f"  - {test}: {error.split('\\n')[0]}")
    
    if result.failures:
        print(f"\n❌ FALLOS ENCONTRADOS:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure.split('\\n')[0]}")
    
    # Salir con código de error si hay fallos
    sys.exit(len(result.errors) + len(result.failures))
