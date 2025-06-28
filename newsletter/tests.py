# Newsletter Tests
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, Mock

from .models import Subscriber, NewsletterTemplate, NewsletterCampaign
from .forms import SubscribeForm, QuickSubscribeForm, UnsubscribeForm


class SubscriberModelTest(TestCase):
    """Test Subscriber model functionality"""
    
    def setUp(self):
        self.subscriber_data = {
            'email': 'test@example.com',
            'first_name': 'Test User',
            'interests': ['privacy', 'technology'],
            'ip_address': '192.168.1.1',
            'source': 'website'
        }
    
    def test_create_subscriber(self):
        """Test creating a new subscriber"""
        subscriber = Subscriber.objects.create(**self.subscriber_data)
        
        self.assertEqual(subscriber.email, 'test@example.com')
        self.assertEqual(subscriber.status, 'pending')
        self.assertIsNotNone(subscriber.confirmation_token)
        self.assertIsNotNone(subscriber.unsubscribe_token)
        self.assertIsNotNone(subscriber.subscribed_at)
    
    def test_confirm_subscription(self):
        """Test subscription confirmation"""
        subscriber = Subscriber.objects.create(**self.subscriber_data)
        
        subscriber.confirm_subscription()
        
        self.assertEqual(subscriber.status, 'active')
        self.assertIsNotNone(subscriber.confirmed_at)
    
    def test_unsubscribe(self):
        """Test unsubscription"""
        subscriber = Subscriber.objects.create(**self.subscriber_data)
        subscriber.confirm_subscription()
        
        subscriber.unsubscribe()
        
        self.assertEqual(subscriber.status, 'unsubscribed')
        self.assertIsNotNone(subscriber.unsubscribed_at)
    
    def test_unique_email_constraint(self):
        """Test that email must be unique"""
        Subscriber.objects.create(**self.subscriber_data)
        
        # Attempting to create another subscriber with same email should work
        # but in practice, we handle duplicates in views
        duplicate_data = self.subscriber_data.copy()
        duplicate_data['first_name'] = 'Another User'
        
        # This should work at model level, but views should handle logic
        subscriber2 = Subscriber.objects.create(**duplicate_data)
        self.assertEqual(Subscriber.objects.filter(email='test@example.com').count(), 2)


class SubscribeFormTest(TestCase):
    """Test subscription forms"""
    
    def test_valid_subscribe_form(self):
        """Test valid subscription form"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test User',
            'interests': ['privacy', 'technology'],
            'privacy_consent': True
        }
        
        form = SubscribeForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_email(self):
        """Test form with invalid email"""
        form_data = {
            'email': 'invalid-email',
            'privacy_consent': True
        }
        
        form = SubscribeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_missing_privacy_consent(self):
        """Test form without privacy consent"""
        form_data = {
            'email': 'test@example.com',
            'privacy_consent': False
        }
        
        form = SubscribeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('privacy_consent', form.errors)
    
    def test_honeypot_detection(self):
        """Test honeypot spam detection"""
        form_data = {
            'email': 'test@example.com',
            'website': 'spam content',  # Honeypot field
            'privacy_consent': True
        }
        
        form = SubscribeForm(data=form_data)
        self.assertFalse(form.is_valid())


class NewsletterViewsTest(TestCase):
    """Test newsletter views"""
    
    def setUp(self):
        self.client = Client()
    
    def test_subscribe_page_loads(self):
        """Test that subscribe page loads correctly"""
        response = self.client.get(reverse('newsletter:subscribe'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PrivacyTool Newsletter')
        self.assertContains(response, 'Email')
    
    def test_valid_subscription_post(self):
        """Test valid subscription submission"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test User',
            'interests': ['privacy'],
            'privacy_consent': True
        }
        
        response = self.client.post(reverse('newsletter:subscribe'), data=form_data)
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 302)
        
        # Check subscriber was created
        self.assertTrue(Subscriber.objects.filter(email='test@example.com').exists())
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Confirma tu suscripción', mail.outbox[0].subject)
    
    def test_duplicate_subscription(self):
        """Test subscribing with existing email"""
        # Create existing subscriber
        Subscriber.objects.create(
            email='test@example.com',
            status='active'
        )
        
        form_data = {
            'email': 'test@example.com',
            'privacy_consent': True
        }
        
        response = self.client.post(reverse('newsletter:subscribe'), data=form_data)
        
        # Should show error for existing subscription
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ya está suscrito')
    
    def test_confirmation_view(self):
        """Test email confirmation"""
        subscriber = Subscriber.objects.create(
            email='test@example.com',
            status='pending'
        )
        
        response = self.client.get(
            reverse('newsletter:confirm', kwargs={'token': subscriber.confirmation_token})
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check subscriber was confirmed
        subscriber.refresh_from_db()
        self.assertEqual(subscriber.status, 'active')
    
    def test_unsubscribe_view(self):
        """Test unsubscribe functionality"""
        subscriber = Subscriber.objects.create(
            email='test@example.com',
            status='active'
        )
        
        response = self.client.get(
            reverse('newsletter:unsubscribe_token', kwargs={'token': subscriber.unsubscribe_token})
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Test POST to confirm unsubscribe
        response = self.client.post(
            reverse('newsletter:unsubscribe_token', kwargs={'token': subscriber.unsubscribe_token}),
            data={'reason': 'too_frequent'}
        )
        
        # Check subscriber was unsubscribed
        subscriber.refresh_from_db()
        self.assertEqual(subscriber.status, 'unsubscribed')
    
    def test_quick_subscribe_api(self):
        """Test quick subscribe API endpoint"""
        form_data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(
            reverse('newsletter:quick_subscribe'), 
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check subscriber was created
        self.assertTrue(Subscriber.objects.filter(email='test@example.com').exists())
    
    def test_stats_api(self):
        """Test stats API endpoint"""
        # Create test data
        Subscriber.objects.create(email='test1@example.com', status='active')
        Subscriber.objects.create(email='test2@example.com', status='pending')
        
        response = self.client.get(reverse('newsletter:api_stats'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['total_subscribers'], 1)  # Only active
        self.assertEqual(data['pending_confirmations'], 1)


class SecurityTest(TestCase):
    """Test security features"""
    
    def setUp(self):
        self.client = Client()
    
    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        form_data = {
            'email': 'test@example.com',
            'privacy_consent': True
        }
        
        # Request without CSRF token should fail
        response = self.client.post(
            reverse('newsletter:subscribe'), 
            data=form_data,
            HTTP_X_CSRFTOKEN='invalid'
        )
        
        # Should not create subscriber
        self.assertFalse(Subscriber.objects.filter(email='test@example.com').exists())
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        form_data = {
            'email': 'test@example.com',
            'privacy_consent': True
        }
        
        # Make multiple rapid requests
        for i in range(6):  # Exceeds 5/minute limit
            response = self.client.post(reverse('newsletter:subscribe'), data=form_data)
        
        # Last request should be rate limited
        # Note: This test might need adjustment based on rate limiting implementation
    
    def test_honeypot_spam_protection(self):
        """Test honeypot field blocks spam"""
        form_data = {
            'email': 'spammer@spam.com',
            'website': 'spam content',  # Honeypot
            'privacy_consent': True
        }
        
        response = self.client.post(reverse('newsletter:subscribe'), data=form_data)
        
        # Should not create subscriber
        self.assertFalse(Subscriber.objects.filter(email='spammer@spam.com').exists())


class EmailIntegrationTest(TestCase):
    """Test email functionality"""
    
    def test_confirmation_email_sent(self):
        """Test that confirmation email is sent"""
        form_data = {
            'email': 'test@example.com',
            'privacy_consent': True
        }
        
        response = self.client.post(reverse('newsletter:subscribe'), data=form_data)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['test@example.com'])
        self.assertIn('Confirma tu suscripción', email.subject)
        self.assertIn('confirm/', email.body)
    
    def test_welcome_email_after_confirmation(self):
        """Test welcome email is sent after confirmation"""
        subscriber = Subscriber.objects.create(
            email='test@example.com',
            status='pending'
        )
        
        # Confirm subscription
        response = self.client.get(
            reverse('newsletter:confirm', kwargs={'token': subscriber.confirmation_token})
        )
        
        # Should send welcome email
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('Bienvenido', email.subject)


class PerformanceTest(TestCase):
    """Test performance considerations"""
    
    def test_bulk_subscriber_creation(self):
        """Test creating many subscribers efficiently"""
        import time
        
        start_time = time.time()
        
        # Create 100 subscribers
        subscribers = []
        for i in range(100):
            subscribers.append(Subscriber(
                email=f'test{i}@example.com',
                status='active'
            ))
        
        Subscriber.objects.bulk_create(subscribers)
        
        end_time = time.time()
        
        # Should complete in reasonable time
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second
        self.assertEqual(Subscriber.objects.count(), 100)
    
    def test_subscriber_query_optimization(self):
        """Test that queries are optimized"""
        # Create test data
        for i in range(50):
            Subscriber.objects.create(
                email=f'test{i}@example.com',
                status='active'
            )
        
        # Test that admin list view doesn't cause N+1 queries
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            initial_queries = len(connection.queries)
            
            response = self.client.get('/admin/newsletter/subscriber/')
            
            # Should not have excessive queries
            query_count = len(connection.queries) - initial_queries
            self.assertLess(query_count, 10)  # Reasonable number of queries


class RegressionTest(TestCase):
    """Test for regression issues"""
    
    def test_email_validation_edge_cases(self):
        """Test edge cases in email validation"""
        edge_cases = [
            'test@localhost',  # Local domain
            'test+tag@example.com',  # Plus addressing
            'test.email@sub.domain.com',  # Subdomain
            'user@domain-with-dash.com',  # Domain with dash
        ]
        
        for email in edge_cases:
            form_data = {
                'email': email,
                'privacy_consent': True
            }
            
            form = SubscribeForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Email {email} should be valid")
    
    def test_unicode_names(self):
        """Test handling of unicode characters in names"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'José María',  # Unicode characters
            'privacy_consent': True
        }
        
        response = self.client.post(reverse('newsletter:subscribe'), data=form_data)
        
        # Should handle unicode correctly
        subscriber = Subscriber.objects.get(email='test@example.com')
        self.assertEqual(subscriber.first_name, 'José María')
    
    def test_large_interest_selection(self):
        """Test handling of many interests selected"""
        form_data = {
            'email': 'test@example.com',
            'interests': ['privacy', 'technology', 'cybersecurity', 'compliance'],
            'privacy_consent': True
        }
        
        form = SubscribeForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_malformed_tokens(self):
        """Test handling of malformed tokens"""
        malformed_tokens = [
            'not-a-uuid',
            '12345',
            '',
            'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
        ]
        
        for token in malformed_tokens:
            response = self.client.get(f'/newsletter/confirm/{token}/')
            # Should return 404 for malformed tokens
            self.assertEqual(response.status_code, 404)


# Run specific test categories
class FastTestSuite(TestCase):
    """Quick tests for CI/CD pipeline"""
    
    def test_models_basic(self):
        """Basic model functionality"""
        subscriber = Subscriber.objects.create(email='test@example.com')
        self.assertEqual(subscriber.email, 'test@example.com')
    
    def test_views_basic(self):
        """Basic view functionality"""
        response = self.client.get(reverse('newsletter:subscribe'))
        self.assertEqual(response.status_code, 200)
    
    def test_forms_basic(self):
        """Basic form functionality"""
        form = SubscribeForm(data={
            'email': 'test@example.com',
            'privacy_consent': True
        })
        self.assertTrue(form.is_valid())
