class UserError(Exception):
    """Base class for all user related exceptions."""

class UserPersistenceError(UserError):
    """database or commit error"""

class DuplicateUsernameError(UserError):
    """when a user tries to update to a username that already exists"""

class InvalidPasswordError(UserError):
    """when the current password is incorrect during a password change"""
