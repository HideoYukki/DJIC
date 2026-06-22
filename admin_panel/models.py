import datetime
from mongoengine import Document, StringField, DateTimeField, DictField, BooleanField


class SystemLog(Document):
    level = StringField(required=True, choices=('INFO', 'WARN', 'ERROR'), default='INFO')
    source = StringField(required=True)
    message = StringField(required=True)
    user_id = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    metadata = DictField()

    meta = {'collection': 'system_logs', 'ordering': ['-created_at']}

    def to_dict(self):
        return {
            'id': str(self.id),
            'level': self.level,
            'source': self.source,
            'message': self.message,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata or {},
        }


class SystemSettings(Document):
    key = StringField(required=True, unique=True)
    value = StringField()
    description = StringField()
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'system_settings'}

    def to_dict(self):
        return {
            'id': str(self.id),
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


def log_event(level: str, source: str, message: str, user_id: str = None, metadata: dict = None):
    SystemLog(
        level=level,
        source=source,
        message=message,
        user_id=user_id,
        metadata=metadata or {},
    ).save()
