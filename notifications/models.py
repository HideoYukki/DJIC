import datetime
from mongoengine import Document, StringField, DateTimeField, BooleanField, DictField


class Notification(Document):
    user_id = StringField(required=True)
    type = StringField(default='INFO')
    title = StringField(required=True)
    body = StringField(default='')
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    metadata = DictField()

    meta = {'collection': 'notifications', 'ordering': ['-created_at']}

    def to_dict(self):
        icon_map = {
            'ACHIEVEMENT': '🏆',
            'COURSE': '📚',
            'PROGRESS': '✅',
            'WARNING': '⚠️',
            'INFO': '📢',
        }
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.body,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata or {},
            'icon': icon_map.get(self.type, '📢'),
        }
