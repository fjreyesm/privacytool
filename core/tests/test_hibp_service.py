"""
Tests for the robust HIBP service implementation
"""

import json
from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.conf import settings
from core.services.hibp_service import HIBPService, HIBPServiceError, check_email, check_hibp_service_status
from core.models.breach import Breach
from core.views.verification_views import check_email_view, service_status_view, recheck_email_view


class HIBPServiceTests(TestCase):
    """Test cases for HIBPService class"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.service = HIBPService()
        cache.clear()
        
    def tearDown(self):
        cache.clear()
        
    @patch('core.services.hibp_service.requests.get')
    def test_successful_api_call(self, mock_get):
        """Test successful HIBP API call"""
        # Mock response data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'Name': 'TestBreach',
                'Domain': 'test.com',
                'BreachDate': '2023-01-01',
                'PwnCount': 1000,
                'AddedDate': '2023-01-02',
                'Description': 'Test breach description',
                'DataClasses': ['Email addresses', 'Passwords'],
                'IsVerified': True,
                'IsFabricated': False,
                'IsSensitive': False,
                'IsRetired': False,
                'IsSpamList': False
            }
        ]
        mock_get.return_value = mock_response
        
        result = self.service.check_email('test@example.com')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['count'], 1)
        self.assertFalse(result['cached'])
        self.assertEqual(len(result['breaches']), 1)
        
        # Verify breach was created
        breach = Breach.objects.get(name='TestBreach')
        self.assertEqual(breach.domain, 'test.com')
        self.assertEqual(breach.pwn_count, 1000)
        
    @patch('core.services.hibp_service.requests.get')
    def test_no_breaches_found(self, mock_get):
        """Test when no breaches are found (404 response)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.service.check_email('clean@example.com')
        
        self.assertEqual(result['status'], 'no_breaches')
        self.assertEqual(result['count'], 0)
        self.assertEqual(len(result['breaches']), 0)
        
    @patch('core.services.hibp_service.requests.get')
    def test_rate_limiting_handling(self, mock_get):
        """Test rate limiting with retry-after header"""
        # First call - rate limited
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {'retry-after': '1'}
        
        # Second call - success
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = []
        
        mock_get.side_effect = [mock_response_429, mock_response_200]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = self.service.check_email('ratelimited@example.com')
            
        self.assertEqual(result['status'], 'no_breaches')
        self.assertEqual(mock_get.call_count, 2)
        
    @patch('core.services.hibp_service.requests.get')
    def test_api_key_missing(self, mock_get):
        """Test behavior when API key is missing"""
        with patch.object(settings, 'HIBP_API_KEY', None):
            result = self.service.check_email('test@example.com')
            
        self.assertEqual(result['status'], 'service_unavailable')
        self.assertIn('API key not configured', result['message'])
        mock_get.assert_not_called()
        
    @patch('core.services.hibp_service.requests.get')
    def test_unauthorized_api_key(self, mock_get):
        """Test handling of unauthorized API key"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = self.service.check_email('test@example.com')
        
        self.assertEqual(result['status'], 'service_unavailable')
        self.assertIn('Invalid or missing API key', result['message'])
        
    @patch('core.services.hibp_service.requests.get')
    def test_service_timeout(self, mock_get):
        """Test handling of service timeout"""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Connection timeout")
        
        result = self.service.check_email('timeout@example.com')
        
        self.assertEqual(result['status'], 'service_unavailable')
        self.assertIn('Service timeout', result['message'])
        
    def test_caching_mechanism(self):
        """Test caching of results"""
        email = 'cached@example.com'
        
        # Mock first call
        with patch('core.services.hibp_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            # First call - should hit API
            result1 = self.service.check_email(email)
            self.assertFalse(result1['cached'])
            self.assertEqual(mock_get.call_count, 1)
            
            # Second call - should use cache
            result2 = self.service.check_email(email)
            self.assertTrue(result2['cached'])
            self.assertEqual(mock_get.call_count, 1)  # No additional API calls
            
    def test_invalid_email_validation(self):
        """Test email validation"""
        with self.assertRaises(ValueError):
            self.service.check_email('')
            
        with self.assertRaises(ValueError):
            self.service.check_email('invalid-email')
            
    @patch('core.services.hibp_service.requests.get')
    def test_connection_error_fallback(self, mock_get):
        """Test fallback when connection fails"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")
        
        result = self.service.check_email('connection@example.com')
        
        self.assertEqual(result['status'], 'service_unavailable')
        self.assertIn('Unable to connect', result['message'])


class HIBPViewTests(TestCase):
    """Test cases for HIBP-related views"""
    
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()
        
    def tearDown(self):
        cache.clear()
        
    @patch('core.views.verification_views.HIBPService')
    def test_check_email_view_success(self, mock_hibp_service):
        """Test successful email check view"""
        mock_service = Mock()
        mock_service.check_email.return_value = {
            'status': 'no_breaches',
            'breaches': [],
            'count': 0,
            'cached': False
        }
        mock_hibp_service.return_value = mock_service
        
        request = self.factory.post('/verification/check/', {'email': 'test@example.com'})
        response = check_email_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('¡Buenas noticias!', response.content.decode())
        
    def test_check_email_view_invalid_email(self):
        """Test email check view with invalid email"""
        request = self.factory.post('/verification/check/', {'email': ''})
        response = check_email_view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('email válido', response.content.decode())
        
    @patch('core.views.verification_views.HIBPService')
    def test_check_email_view_service_unavailable(self, mock_hibp_service):
        """Test email check view when service is unavailable"""
        mock_service = Mock()
        mock_service.check_email.return_value = {
            'status': 'service_unavailable',
            'message': 'Service temporarily unavailable',
            'breaches': [],
            'count': 0,
            'cached': False
        }
        mock_hibp_service.return_value = mock_service
        
        request = self.factory.post('/verification/check/', {'email': 'test@example.com'})
        response = check_email_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('temporalmente no disponible', response.content.decode())
        
    @patch('core.services.hibp_service.check_hibp_service_status')
    def test_service_status_view(self, mock_status_check):
        """Test service status endpoint"""
        mock_status_check.return_value = {
            'available': True,
            'status': 'operational',
            'message': 'Service working normally'
        }
        
        request = self.factory.get('/verification/status/')
        response = service_status_view(request)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['data']['available'])
        
    @patch('core.views.verification_views.HIBPService')
    def test_recheck_email_view(self, mock_hibp_service):
        """Test recheck email functionality"""
        mock_service = Mock()
        mock_service.check_email.return_value = {
            'status': 'no_breaches',
            'breaches': [],
            'count': 0,
            'cached': False
        }
        mock_hibp_service.return_value = mock_service
        
        request = self.factory.post('/verification/recheck/', {
            'email': 'test@example.com',
            'verification_id': 'test-id'
        })
        response = recheck_email_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('¡Buenas noticias!', response.content.decode())
        
        # Verify cache was cleared
        with patch('django.core.cache.cache.delete') as mock_cache_delete:
            recheck_email_view(request)
            mock_cache_delete.assert_called()


class HIBPLegacyFunctionTests(TestCase):
    """Test cases for legacy function compatibility"""
    
    def setUp(self):
        cache.clear()
        
    @patch('core.services.hibp_service.HIBPService')
    def test_legacy_check_email_function(self, mock_hibp_service):
        """Test legacy check_email function works correctly"""
        mock_service = Mock()
        mock_service.check_email.return_value = {
            'status': 'success',
            'breaches': [],
            'count': 0
        }
        mock_hibp_service.return_value = mock_service
        
        result = check_email('test@example.com')
        
        self.assertEqual(result, [])
        
    @patch('core.services.hibp_service.HIBPService')
    def test_legacy_function_service_unavailable(self, mock_hibp_service):
        """Test legacy function handles service unavailable"""
        mock_service = Mock()
        mock_service.check_email.return_value = {
            'status': 'service_unavailable',
            'message': 'Service down'
        }
        mock_hibp_service.return_value = mock_service
        
        with self.assertRaises(Exception) as context:
            check_email('test@example.com')
            
        self.assertIn('Service down', str(context.exception))


class HIBPServiceStatusTests(TestCase):
    """Test cases for service status checking"""
    
    @patch('core.services.hibp_service.HIBPService')
    def test_service_status_check_operational(self, mock_hibp_service):
        """Test service status when operational"""
        mock_service = Mock()
        mock_service.check_email.return_value = {
            'status': 'no_breaches',
            'breaches': [],
            'count': 0
        }
        mock_hibp_service.return_value = mock_service
        
        status = check_hibp_service_status()
        
        self.assertTrue(status['available'])
        self.assertEqual(status['status'], 'operational')
        
    @patch('core.services.hibp_service.HIBPService')
    def test_service_status_check_degraded(self, mock_hibp_service):
        """Test service status when degraded"""
        mock_service = Mock()
        mock_service.check_email.side_effect = Exception("Service error")
        mock_hibp_service.return_value = mock_service
        
        status = check_hibp_service_status()
        
        self.assertFalse(status['available'])
        self.assertEqual(status['status'], 'degraded')
        self.assertIn('Service error', status['message'])
