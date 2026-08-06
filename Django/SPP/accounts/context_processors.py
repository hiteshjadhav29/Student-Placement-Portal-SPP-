from .models import UserNotification


def unread_notifications_context(request):
    if request.user.is_authenticated:
        notifications = UserNotification.objects.filter(user=request.user)
        unread_count = notifications.filter(is_read=False).count()
        recent_notifications = notifications[:5]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications,
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }
