# Core Services Module
from .hibp_service import HIBPService, check_email, check_hibp_service_status
from .report_service import *

# Alias for backward compatibility
EmailBreachService = HIBPService
