"""Domain-specific exceptions for business rule violations."""


class DomainException(Exception):
    """Base exception for all domain-level errors."""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """Raised when a requested entity does not exist."""
    def __init__(self, entity_name: str, entity_id: int | str):
        super().__init__(f"{entity_name} with id '{entity_id}' not found", "NOT_FOUND")


class DuplicateEntityException(DomainException):
    """Raised when attempting to create a duplicate entity."""
    def __init__(self, entity_name: str, field: str, value: str):
        super().__init__(f"{entity_name} with {field} '{value}' already exists", "DUPLICATE")


class CapacityExceededException(DomainException):
    """Raised when an event or session is full."""
    def __init__(self, entity_name: str):
        super().__init__(f"{entity_name} has reached maximum capacity", "CAPACITY_EXCEEDED")


class InvalidOperationException(DomainException):
    """Raised when a business operation is not allowed."""
    def __init__(self, message: str):
        super().__init__(message, "INVALID_OPERATION")


class AuthenticationException(DomainException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, "AUTHENTICATION_FAILED")


class AuthorizationException(DomainException):
    """Raised when a user lacks permission."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "FORBIDDEN")
