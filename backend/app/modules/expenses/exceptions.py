class ExpenseError(Exception):
    """Base class for all expense exceptions"""

class InvalidExpenseDataError(ExpenseError):
    """Bad inout or missing fields"""

class ExpensePersistenceError(ExpenseError):
    """persistence error for expenses"""

class ExpenseNotFoundError(ExpenseError):
    """for expenses that dont exist"""


class DuplicateExpenseError(ExpenseError):
    """for when an expense with the same type already exists for the trip"""


class ReceiptError(ExpenseError):
    """Base for receipt-specific issues"""


class ReceiptValidationError(ReceiptError):
    """Bad file input (type/size)"""


class ReceiptStorageConfigError(ReceiptError):
    """Misconfigured storage backend"""


class ReceiptUploadError(ReceiptError):
    """Unexpected storage or persistence failure"""


class ReceiptNotFoundError(ReceiptError):
    """Receipt not found or not owned by user"""
