from .incident import (
    IncidentBase as WorkRequestBase,
    IncidentCreate as WorkRequestCreate,
    IncidentUpdate as WorkRequestUpdate,
    IncidentRead as WorkRequestRead,
    IncidentAssetAction as WorkRequestAssetAction,
    IncidentUpdateBase as WorkRequestUpdateBase,
    IncidentUpdateCreate as WorkRequestUpdateCreate,
    IncidentUpdateRead as WorkRequestUpdateRead,
    IncidentAttachmentCreate as WorkRequestAttachmentCreate,
    IncidentAttachmentRead as WorkRequestAttachmentRead,
)

__all__ = [
    "WorkRequestBase",
    "WorkRequestCreate",
    "WorkRequestUpdate",
    "WorkRequestRead",
    "WorkRequestAssetAction",
    "WorkRequestUpdateBase",
    "WorkRequestUpdateCreate",
    "WorkRequestUpdateRead",
    "WorkRequestAttachmentCreate",
    "WorkRequestAttachmentRead",
]
