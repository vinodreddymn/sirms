from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    title: str
    message: str
    notification_type: str
    related_entity_id: UUID | None = None


class NotificationRead(NotificationCreate):
    id: UUID
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None


class NotificationPreferenceUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email_enabled: bool = False
    sms_enabled: bool = False
    push_enabled: bool = False
    in_app_enabled: bool = True


class NotificationPreferenceRead(NotificationPreferenceUpdate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
