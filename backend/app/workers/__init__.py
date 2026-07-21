"""Background job workers for async task processing.

Provides job classes for:
- Maintenance operations (overdue checks, archiving, scheduling)
- Bulk imports (assets, incidents, maintenance)
- Bulk exports (assets, incidents, maintenance, reports)
- Notifications (sending, cleanup, retries)

All jobs inherit from BackgroundJob and can be swapped with Celery or other
task queue implementations in the future.
"""

from app.workers.base import BackgroundJob
from app.workers.maintenance_jobs import (
    MaintenanceOverdueCheckJob,
    MaintenanceHistoryArchiveJob,
    MaintenanceScheduleUpdateJob,
)
from app.workers.import_jobs import (
    BulkAssetImportJob,
    BulkIncidentImportJob,
    BulkMaintenanceImportJob,
)
from app.workers.export_jobs import (
    AssetExportJob,
    IncidentExportJob,
    MaintenanceExportJob,
    ReportExportJob,
)
from app.workers.notification_jobs import (
    NotificationSendJob,
    BulkNotificationSendJob,
    NotificationCleanupJob,
    DeliveryRetryJob,
)

__all__ = [
    "BackgroundJob",
    # Maintenance jobs
    "MaintenanceOverdueCheckJob",
    "MaintenanceHistoryArchiveJob",
    "MaintenanceScheduleUpdateJob",
    # Import jobs
    "BulkAssetImportJob",
    "BulkIncidentImportJob",
    "BulkMaintenanceImportJob",
    # Export jobs
    "AssetExportJob",
    "IncidentExportJob",
    "MaintenanceExportJob",
    "ReportExportJob",
    # Notification jobs
    "NotificationSendJob",
    "BulkNotificationSendJob",
    "NotificationCleanupJob",
    "DeliveryRetryJob",
]
