
class EmailServiceError(Exception):
    """Base exception for email service errors."""
    pass


class EmailServiceConnectionError(EmailServiceError):
    """Raised when email service connection fails."""
    pass


class EmailServiceRateLimitError(EmailServiceError):
    """Raised when email service rate limit is exceeded."""
    pass


class EmailServiceAuthenticationError(EmailServiceError):
    """Raised when email service authentication fails."""
    pass


class EmailServiceQuotaExceededError(EmailServiceError):
    """Raised when email service quota is exceeded."""
    pass