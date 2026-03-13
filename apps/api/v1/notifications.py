from ninja import Router, Schema, Query

router = Router()


class NotificationSchema(Schema):
    id: str
    title: str
    message: str
    type: str
    is_read: bool
    sent_at: str


class PaginatedResponse(Schema):
    items: list
    total: int
    page: int
    pages: int
    unread_count: int = 0


@router.get("", response=PaginatedResponse)
def get_notifications(request, page: int = 1, limit: int = 20):
    """Get user notifications"""
    from apps.notifications.models import Notification
    
    queryset = Notification.objects.filter(user=request.user)
    unread_count = queryset.filter(is_read=False).count()
    
    total = queryset.count()
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    
    items = [
        NotificationSchema(
            id=str(n.id),
            title=n.title,
            message=n.message,
            type=n.type,
            is_read=n.is_read,
            sent_at=n.sent_at.isoformat(),
        )
        for n in queryset[offset:offset + limit]
    ]
    
    return PaginatedResponse(
        items=items, total=total, page=page, pages=pages, unread_count=unread_count
    )


@router.post("/{notification_id}/read")
def mark_as_read(request, notification_id: str):
    """Mark notification as read"""
    from apps.notifications.models import Notification
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    return {"success": True}