"""Base abstract class for background jobs.

All background jobs (maintenance, imports, exports, notifications) inherit from
BackgroundJob and implement the run() method. This allows for easy swapping between
in-process and external task queues (e.g., Celery) in the future.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession


class BackgroundJob(ABC):
    """Abstract base class for all background jobs.
    
    Attributes:
        job_id: Unique identifier for this job execution
        job_type: Type of job (e.g., "maintenance_check", "import_csv")
        status: Job status ("pending", "running", "completed", "failed")
        created_at: When the job was created
        started_at: When the job actually started execution
        completed_at: When the job completed (success or failure)
        error_message: Error message if job failed
        context: Job-specific context data (e.g., file path, entity IDs)
    """
    
    def __init__(
        self,
        job_id: str,
        job_type: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a background job.
        
        Args:
            job_id: Unique identifier for this job
            job_type: Type of job being executed
            context: Optional dict of job-specific data
        """
        self.job_id = job_id
        self.job_type = job_type
        self.context = context or {}
        
        self.status = "pending"
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
    
    @abstractmethod
    async def run(self, session: AsyncSession) -> Dict[str, Any]:
        """Execute the background job.
        
        Args:
            session: AsyncSession for database access
            
        Returns:
            Dict with job result data (e.g., {"processed": 100, "errors": 2})
            
        Raises:
            Exception: If job execution fails (caught by caller)
        """
        pass
    
    async def execute(self, session: AsyncSession) -> Dict[str, Any]:
        """Execute job with lifecycle tracking.
        
        Handles status transitions, timestamps, and error capture.
        
        Args:
            session: AsyncSession for database access
            
        Returns:
            Dict with job result, status, and metadata
        """
        self.status = "running"
        self.started_at = datetime.utcnow()
        
        try:
            result = await self.run(session)
            self.status = "completed"
            self.completed_at = datetime.utcnow()
            return {
                "job_id": self.job_id,
                "job_type": self.job_type,
                "status": "completed",
                "result": result,
                "created_at": self.created_at,
                "completed_at": self.completed_at,
            }
        except Exception as e:
            self.status = "failed"
            self.completed_at = datetime.utcnow()
            self.error_message = str(e)
            return {
                "job_id": self.job_id,
                "job_type": self.job_type,
                "status": "failed",
                "error": str(e),
                "created_at": self.created_at,
                "completed_at": self.completed_at,
            }
