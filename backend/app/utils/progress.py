"""Reusable SSE progress streaming utilities for long-running operations."""

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


@dataclass
class JobState:
    job_id: str
    status: JobStatus = JobStatus.PENDING
    total: int = 0
    completed: int = 0
    failed: int = 0
    errors: list = field(default_factory=list)
    current_row: int = 0
    started_at: float = 0.0
    finished_at: float = 0.0

    @property
    def percentage(self) -> int:
        if self.total == 0:
            return 0
        return int((self.completed + self.failed) / self.total * 100)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "percentage": self.percentage,
            "current_row": self.current_row,
            "errors": self.errors[-5:],  # last 5 errors only
        }


class JobManager:
    """In-memory job state manager. One instance per process."""

    def __init__(self):
        self._jobs: dict[str, JobState] = {}

    def create(self, total: int) -> JobState:
        job = JobState(
            job_id=str(uuid.uuid4()),
            total=total,
            started_at=time.time(),
        )
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> JobState | None:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs) -> JobState | None:
        job = self._jobs.get(job_id)
        if job:
            for k, v in kwargs.items():
                setattr(job, k, v)
        return job


# Global instance
job_manager = JobManager()


def sse_event(event: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
