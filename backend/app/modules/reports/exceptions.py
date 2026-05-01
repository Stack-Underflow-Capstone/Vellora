class ReportError(Exception):
    """Base class for all report exceptions"""


class InvalidReportDataError(ReportError):
    """Bad input or invalid report data"""


class ReportPersistenceError(ReportError):
    """Persistence error for reports"""


class ReportNotFoundError(ReportError):
    """For reports that don't exist"""


class ReportPermissionError(ReportError):
    """For permission denied errors"""


class ReportRateLimitError(ReportError):
    """For rate limiting violations"""


class ReportSystemLimitError(ReportError):
    """For system-wide limits reached"""


class ReportExpiredError(ReportError):
    """For expired reports"""


class ReportMaxRetriesError(ReportError):
    """For max retry attempts reached"""


class ReportInvalidStateError(ReportError):
    """For invalid state transitions"""

class InvalidMonthAnalyticsError(ReportError):
    """For invalid months errors"""

class InvalidDataAnalyticsError(ReportError):
    """For invalid data gathered from data_builder errors"""