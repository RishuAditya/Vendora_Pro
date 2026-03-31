from backend.extensions import db
from backend.models.user_model import Notification

def send_notification(sender_id, receiver_id, message):
    notif = Notification(sender_id=sender_id, receiver_id=receiver_id, message=message)
    db.session.add(notif)
    db.session.commit()