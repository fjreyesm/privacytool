from django.db import models

from django.contrib.auth.models import User

class ApiRequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    email_requested = models.EmailField() 
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['email_requested', 'timestamp']),
        ]