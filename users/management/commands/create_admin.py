import os
import getpass
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
import hashlib


def _fernet():
    return Fernet(os.getenv('ENCRYPTION_KEY').encode())


def encrypt_data(text):
    return _fernet().encrypt(text.encode()).decode()


def hash_data(text):
    return hashlib.sha3_256(text.encode()).hexdigest()


class Command(BaseCommand):
    help = 'Tworzy konto administratora (pierwszego lub kolejnego)'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str)
        parser.add_argument('--name', type=str, default='Administrator')
        parser.add_argument('--password', type=str)

    def handle(self, *args, **options):
        from users.models import MongoUser

        email = options.get('email') or input('Email: ').strip().lower()
        name = options.get('name') or input('Imię i nazwisko: ').strip()
        password = options.get('password') or getpass.getpass('Hasło: ')

        try:
            validate_email(email)
        except ValidationError:
            self.stderr.write(self.style.ERROR('Niepoprawny format adresu e-mail.'))
            return

        e_hash = hash_data(email)
        if MongoUser.objects(email_hash=e_hash).first():
            self.stderr.write(self.style.ERROR(f'Użytkownik {email} już istnieje.'))
            return

        user = MongoUser(
            email=encrypt_data(email),
            email_hash=e_hash,
            password=make_password(password),
            name=encrypt_data(name),
            role='ADMIN',
            is_verified=True,
            is_active=True,
        )
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Administrator {email} utworzony. ID: {user.id}'))
