from app.models import Notification


def unread_notification_count(user_id):
    return Notification.query.filter_by(student_user_id=user_id, status="Unread").count()
