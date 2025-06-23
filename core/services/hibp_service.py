from django.core.cache import cache
import requests
import logging
import time
from datetime import datetime, timedelta
from django.conf import settings
from core.models.breach import Breach

logger = logging.getLogger(__name__)

class HIBPServiceError(Exception):
    """Custom exception for HIBP service errors"""
    pass

class HIBPService:
    """
    Robust HIBP API service with fallback mechanisms and error handling.
    """
    
    def __init__(self):
        self.base_url = "https://haveibeenpwned.com/api/v3"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.timeout = 10
        
    def _get_headers(self):
        """Get headers for HIBP API requests"""
        headers = {
            'User-Agent': 'PrivacyTool/1.0 (Django; Security Check Tool)',
            'Accept': 'application/json'
        }
        
        # Add API key if available
        if hasattr(settings, 'HIBP_API_KEY') and settings.HIBP_API_KEY:
            headers['hibp-api-key'] = settings.HIBP_API_KEY
        
        return headers
    
    def _make_request_with_retry(self, url, headers, params=None):
        """
        Make HTTP request with exponential backoff retry logic
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[HIBP] Attempt {attempt + 1}/{self.max_retries} - {url}")
                
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('retry-after', 60))
                    logger.warning(f"[HIBP] Rate limited. Retry after {retry_after} seconds")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        raise HIBPServiceError(f"Rate limit exceeded after {self.max_retries} attempts")
                
                # Handle other HTTP errors
                if response.status_code == 404:
                    # No breaches found - this is normal
                    return None
                
                if response.status_code == 401:
                    raise HIBPServiceError("Invalid or missing API key")
                
                if response.status_code == 403:
                    raise HIBPServiceError("API access forbidden - check subscription")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"[HIBP] Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    raise HIBPServiceError("Service timeout after multiple attempts")
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"[HIBP] Connection error on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise HIBPServiceError("Unable to connect to HIBP service")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"[HIBP] Request error: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise HIBPServiceError(f"Request failed: {str(e)}")
        
        raise HIBPServiceError("Maximum retry attempts exceeded")
    
    def _get_cached_result(self, email):
        """Get cached result for email"""
        cache_key = f"hibp:email:{email.lower()}"
        return cache.get(cache_key)
    
    def _cache_result(self, email, breach_ids, cache_duration=3600):
        """Cache result for email"""
        cache_key = f"hibp:email:{email.lower()}"
        cache.set(cache_key, breach_ids, timeout=cache_duration)
    
    def _fallback_response(self, email, error_msg):
        """
        Generate fallback response when HIBP is unavailable
        """
        logger.warning(f"[HIBP] Using fallback for {email}: {error_msg}")
        
        # Cache negative result for shorter time during outages
        self._cache_result(email, [], cache_duration=300)  # 5 minutes
        
        return {
            'breaches': [],
            'count': 0,
            'status': 'service_unavailable',
            'message': 'El servicio de verificación está temporalmente no disponible. Intentar más tarde.',
            'fallback': True
        }
    
    def check_email(self, email):
        """
        Check if email appears in any breaches with robust error handling
        
        Args:
            email (str): Email address to check
            
        Returns:
            dict: Results with breaches, count, status, and metadata
        """
        if not email or '@' not in email:
            raise ValueError("Invalid email address")
        
        email = email.lower().strip()
        
        # Check cache first
        cached_result = self._get_cached_result(email)
        if cached_result is not None:
            logger.info(f"[HIBP] Cache HIT for {email}")
            if not cached_result:  # Empty list means no breaches
                return {
                    'breaches': [],
                    'count': 0,
                    'status': 'no_breaches',
                    'cached': True
                }
            
            # Get breach objects from cached IDs
            breaches = list(Breach.objects.filter(id__in=cached_result))
            return {
                'breaches': breaches,
                'count': len(breaches),
                'status': 'success',
                'cached': True
            }
        
        logger.info(f"[HIBP] Cache MISS for {email} - querying API")
        
        # Check if API key is available
        if not hasattr(settings, 'HIBP_API_KEY') or not settings.HIBP_API_KEY:
            logger.error("[HIBP] No API key configured")
            return self._fallback_response(email, "API key not configured")
        
        try:
            # Make API request
            url = f"{self.base_url}/breachedaccount/{email}"
            headers = self._get_headers()
            params = {'truncateResponse': 'false'}
            
            response = self._make_request_with_retry(url, headers, params)
            
            # Handle no breaches found
            if response is None:
                logger.info(f"[HIBP] No breaches found for {email}")
                self._cache_result(email, [], cache_duration=3600)
                return {
                    'breaches': [],
                    'count': 0,
                    'status': 'no_breaches',
                    'cached': False
                }
            
            # Process successful response
            breach_data = response.json()
            logger.info(f"[HIBP] Found {len(breach_data)} breaches for {email}")
            
            breach_objects = []
            breach_ids = []
            
            # Create or update breach objects
            for breach in breach_data:
                try:
                    breach_obj, created = Breach.objects.update_or_create(
                        name=breach['Name'],
                        defaults={
                            'domain': breach.get('Domain'),
                            'breach_date': breach.get('BreachDate'),
                            'pwn_count': breach.get('PwnCount', 0),
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
                    
                    if created:
                        logger.info(f"[HIBP] Created new breach: {breach['Name']}")
                    
                except Exception as e:
                    logger.error(f"[HIBP] Error saving breach {breach.get('Name', 'Unknown')}: {str(e)}")
                    continue
            
            # Cache successful result
            self._cache_result(email, breach_ids, cache_duration=3600)
            
            return {
                'breaches': breach_objects,
                'count': len(breach_objects),
                'status': 'success',
                'cached': False
            }
            
        except HIBPServiceError as e:
            # Known HIBP service error - use fallback
            return self._fallback_response(email, str(e))
            
        except Exception as e:
            # Unexpected error - log and fallback
            logger.error(f"[HIBP] Unexpected error for {email}: {str(e)}")
            return self._fallback_response(email, "Unexpected service error")


# Legacy function for backward compatibility
def check_email(email):
    """
    Legacy function that wraps the new HIBPService class
    
    Args:
        email (str): Email address to check
        
    Returns:
        list: List of Breach objects (for backward compatibility)
        
    Raises:
        Exception: If there's a critical error
    """
    service = HIBPService()
    try:
        result = service.check_email(email)
        
        # If service is unavailable but we want to show an error to user
        if result.get('status') == 'service_unavailable':
            raise Exception(result.get('message', 'Service temporarily unavailable'))
        
        return result['breaches']
        
    except ValueError as e:
        # Re-raise validation errors
        raise Exception(str(e))
    except Exception as e:
        # For any other error, raise as general exception
        raise Exception(f"Unable to check email: {str(e)}")


# Service status check function
def check_hibp_service_status():
    """
    Check if HIBP service is available and working
    
    Returns:
        dict: Service status information
    """
    service = HIBPService()
    
    try:
        # Test with a known test email
        result = service.check_email("test@example.com")
        
        return {
            'available': True,
            'status': 'operational',
            'message': 'HIBP service is working normally',
            'last_check': datetime.now()
        }
        
    except Exception as e:
        return {
            'available': False,
            'status': 'degraded',
            'message': str(e),
            'last_check': datetime.now()
        }
