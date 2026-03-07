"""Notification system for user alerts."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["notifications"])


class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "info"  # info, success, warning, error


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    read: bool
    created_at: str


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int


# In-memory notification store (in production, use database)
NOTIFICATIONS: dict[int, list[dict]] = {}


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get all notifications for current user."""
    user_id = current_user.id

    if user_id not in NOTIFICATIONS:
        NOTIFICATIONS[user_id] = []

    notifications = NOTIFICATIONS[user_id].copy()

    if unread_only:
        notifications = [n for n in notifications if not n.get("read", False)]

    # Sort by created_at descending
    notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    unread_count = len([n for n in NOTIFICATIONS[user_id] if not n.get("read", False)])

    return NotificationListResponse(
        notifications=[
            NotificationResponse(
                id=n["id"],
                title=n["title"],
                message=n["message"],
                type=n["type"],
                read=n.get("read", False),
                created_at=n["created_at"],
            )
            for n in notifications[:50]  # Limit to 50
        ],
        unread_count=unread_count,
    )


@router.post(
    "/notifications/{notification_id}/read", response_model=NotificationResponse
)
async def mark_read(
    notification_id: str, current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read."""
    user_id = current_user.id

    if user_id not in NOTIFICATIONS:
        raise HTTPException(status_code=404, detail="Notification not found")

    for n in NOTIFICATIONS[user_id]:
        if n["id"] == notification_id:
            n["read"] = True
            return NotificationResponse(
                id=n["id"],
                title=n["title"],
                message=n["message"],
                type=n["type"],
                read=n.get("read", False),
                created_at=n["created_at"],
            )

    raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/notifications/read-all")
async def mark_all_read(current_user: User = Depends(get_current_active_user)):
    """Mark all notifications as read."""
    user_id = current_user.id

    if user_id in NOTIFICATIONS:
        for n in NOTIFICATIONS[user_id]:
            n["read"] = True

    return {"status": "success", "message": "All notifications marked as read"}


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str, current_user: User = Depends(get_current_active_user)
):
    """Delete a notification."""
    user_id = current_user.id

    if user_id not in NOTIFICATIONS:
        raise HTTPException(status_code=404, detail="Notification not found")

    NOTIFICATIONS[user_id] = [
        n for n in NOTIFICATIONS[user_id] if n["id"] != notification_id
    ]

    return {"status": "success", "message": "Notification deleted"}


@router.delete("/notifications")
async def clear_notifications(current_user: User = Depends(get_current_active_user)):
    """Clear all notifications."""
    user_id = current_user.id
    NOTIFICATIONS[user_id] = []

    return {"status": "success", "message": "All notifications cleared"}


# Helper function to create notifications (can be called from other endpoints)
async def create_notification(
    user_id: str, title: str, message: str, type: str = "info"
):
    """Create a notification for a user."""
    if user_id not in NOTIFICATIONS:
        NOTIFICATIONS[user_id] = []

    notification = {
        "id": str(uuid.uuid4()),
        "title": title,
        "message": message,
        "type": type,
        "read": False,
        "created_at": datetime.utcnow().isoformat(),
    }

    NOTIFICATIONS[user_id].append(notification)

    # Keep only last 100 notifications
    if len(NOTIFICATIONS[user_id]) > 100:
        NOTIFICATIONS[user_id] = NOTIFICATIONS[user_id][-100:]

    return notification
