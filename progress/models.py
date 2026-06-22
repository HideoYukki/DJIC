import datetime
from mongoengine import (
    Document, StringField, DateTimeField, IntField,
    ListField, BooleanField,
)


class Enrollment(Document):
    user_id = StringField(required=True)
    course_id = StringField(required=True)
    enrolled_at = DateTimeField(default=datetime.datetime.utcnow)
    completed_at = DateTimeField()

    meta = {
        'collection': 'enrollments',
        'indexes': [{'fields': ['user_id', 'course_id'], 'unique': True}],
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class Progress(Document):
    user_id = StringField(required=True)
    course_id = StringField(required=True)
    completed_material_ids = ListField(StringField())
    xp_earned = IntField(default=0)
    last_activity_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'progress',
        'indexes': [{'fields': ['user_id', 'course_id'], 'unique': True}],
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'course_id': self.course_id,
            'completed_material_ids': self.completed_material_ids,
            'xp_earned': self.xp_earned,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
        }


BADGE_CATALOGUE = {
    'first_enrollment': {'name': 'Pierwszy krok', 'description': 'Zapisałeś się na swój pierwszy kurs.', 'xp': 10},
    'first_completion': {'name': 'Ukończono!', 'description': 'Ukończyłeś swój pierwszy kurs.', 'xp': 100},
    'quiz_master': {'name': 'Mistrz Quizów', 'description': 'Zaliczyłeś 10 quizów.', 'xp': 50},
    'xp_100': {'name': 'Setka', 'description': 'Zdobyłeś 100 XP.', 'xp': 20},
    'xp_500': {'name': 'Półtysięcznik', 'description': 'Zdobyłeś 500 XP.', 'xp': 50},
}


class Achievement(Document):
    user_id = StringField(required=True)
    badge_id = StringField(required=True)
    earned_at = DateTimeField(default=datetime.datetime.utcnow)
    xp_value = IntField(default=0)

    meta = {'collection': 'achievements'}

    def to_dict(self):
        badge_info = BADGE_CATALOGUE.get(self.badge_id, {})
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': badge_info.get('name', self.badge_id),
            'badge_description': badge_info.get('description', ''),
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'xp_value': self.xp_value,
        }
