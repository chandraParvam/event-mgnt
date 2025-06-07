class EventManagementException(Exception):
    """Base exception for event management system"""
    pass

class EventNotFound(EventManagementException):
    """Exception raised when event is not found"""
    pass

class EventCapacityExceeded(EventManagementException):
    """Exception raised when event capacity is exceeded"""
    pass

class DuplicateRegistration(EventManagementException):
    """Exception raised when duplicate registration is attempted"""
    pass

class InvalidEventData(EventManagementException):
    """Exception raised when event data is invalid"""
    pass