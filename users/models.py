import datetime
from mongoengine import Document, StringField, DateTimeField, BooleanField


class MongoUser(Document):
    email = StringField(required=True)
    email_hash = StringField(required=True, unique=True)
    password = StringField(required=True)
    name = StringField(max_length=500)
    role = StringField(default='STUDENT', choices=('STUDENT', 'CREATOR', 'ADMIN'))
    avatar_url = StringField()
    bio = StringField(max_length=2000)
    is_verified = BooleanField(default=False)
    verification_token = StringField()
    password_reset_token = StringField()
    password_reset_expires = DateTimeField()
    is_active = BooleanField(default=True)
    last_login = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'users'}

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return f"MongoUser({self.email_hash[:8]}...)"
