"""Custom exceptions"""


class PlaybookPulseException(Exception):
    """Base exception for all PlaybookPulse errors"""
    pass


class AgentException(PlaybookPulseException):
    """Raised when an agent fails"""
    pass


class IntegrationException(PlaybookPulseException):
    """Raised when an integration fails"""
    pass


class AuthenticationException(PlaybookPulseException):
    """Raised when authentication fails"""
    pass


class ValidationException(PlaybookPulseException):
    """Raised when validation fails"""
    pass


class ConfigurationException(PlaybookPulseException):
    """Raised when configuration is invalid"""
    pass


class RateLimitException(PlaybookPulseException):
    """Raised when rate limit is exceeded"""
    pass


class TimeoutException(PlaybookPulseException):
    """Raised when an operation times out"""
    pass
