class NotificationError(Exception):
    """Base exception for notification related errors"""
    pass


class NotificationNotFoundError(NotificationError):
    """when a notification is not found"""
    pass


class NotificationPersistenceError(NotificationError):
    """error persisting notification data"""
    pass


class InvalidNotificationDataError(NotificationError):
    """notif data is invalid"""
    pass


class NotificationDeliveryError(NotificationError):
    """notif delivery fails"""
    pass


class DeviceTokenError(NotificationError):
    """error with device tokens"""
    pass


class DuplicateDeviceTokenError(NotificationError):
    """register a duplicate device token"""
    pass
