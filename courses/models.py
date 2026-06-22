import datetime
from mongoengine import (
    Document, StringField, DateTimeField, BooleanField,
    FloatField, IntField, ListField,
)


class Course(Document):
    title = StringField(required=True)
    description = StringField(default='')
    category = StringField(default='')
    thumbnail_url = StringField()
    creator_id = StringField(required=True)
    status = StringField(default='DRAFT', choices=('DRAFT', 'REVIEW', 'ACTIVE', 'ARCHIVED'))
    price = FloatField(default=0)
    duration_minutes = IntField(default=0)
    level = StringField(default='BEGINNER', choices=('BEGINNER', 'INTERMEDIATE', 'ADVANCED'))
    tags = ListField(StringField())
    reject_reason = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    published_at = DateTimeField()

    meta = {'collection': 'courses'}

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'thumbnail_url': self.thumbnail_url,
            'creator_id': self.creator_id,
            'status': self.status,
            'price': self.price,
            'duration_minutes': self.duration_minutes,
            'level': self.level,
            'tags': self.tags,
            'reject_reason': self.reject_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }


class Material(Document):
    course_id = StringField(required=True)
    title = StringField(required=True)
    type = StringField(required=True, choices=('VIDEO', 'TEXT', 'QUIZ'))
    order = IntField(default=0)
    content = StringField(default='')  # URL / HTML / quiz_id
    duration_seconds = IntField(default=0)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'materials'}

    def to_dict(self):
        return {
            'id': str(self.id),
            'course_id': self.course_id,
            'title': self.title,
            'type': self.type,
            'order': self.order,
            'content': self.content,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
