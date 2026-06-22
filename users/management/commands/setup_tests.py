"""
Komenda pomocnicza do uruchamiania testów — czyści dane testowe i tworzy świeżego admina.
Użycie: python manage.py setup_tests
"""
import os
import hashlib
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from cryptography.fernet import Fernet


TEST_EMAILS = [
    'student1@test.djic',
    'creator1@test.djic',
    'creator2@test.djic',
    'admin1@test.djic',
    'fake_admin@test.djic',
    'adminCreated@test.djic',
    'adminCreated2@test.djic',
    'noname@test.djic',
    'new@test.djic',
]


def _fernet():
    return Fernet(os.getenv('ENCRYPTION_KEY').encode())


def encrypt(text):
    return _fernet().encrypt(text.encode()).decode()


def sha3(text):
    return hashlib.sha3_256(text.strip().lower().encode()).hexdigest()


class Command(BaseCommand):
    help = 'Czyści testowe dane z bazy i przygotowuje środowisko testowe'

    def handle(self, *args, **options):
        from users.models import MongoUser
        from courses.models import Course, Material
        from progress.models import Enrollment, Progress, Achievement

        self.stdout.write('Czyszczenie danych testowych...')

        test_hashes = [sha3(e) for e in TEST_EMAILS]
        test_users = list(MongoUser.objects(email_hash__in=test_hashes))
        test_user_ids = [str(u.id) for u in test_users]

        # Usuń kursy twórców testowych i powiązane dane
        for uid in test_user_ids:
            courses = list(Course.objects(creator_id=uid))
            for c in courses:
                cid = str(c.id)
                Material.objects(course_id=cid).delete()
                Enrollment.objects(course_id=cid).delete()
                Progress.objects(course_id=cid).delete()
                c.delete()
            Enrollment.objects(user_id=uid).delete()
            Progress.objects(user_id=uid).delete()
            Achievement.objects(user_id=uid).delete()

        deleted = MongoUser.objects(email_hash__in=test_hashes).delete()
        self.stdout.write(f'  Usunieto {deleted} uzytkownikow testowych.')

        # Stwórz świeżego admina
        user = MongoUser(
            email=encrypt('admin1@test.djic'),
            email_hash=sha3('admin1@test.djic'),
            password=make_password('Test1234!'),
            name=encrypt('Admin Jeden'),
            role='ADMIN',
            is_verified=True,
            is_active=True,
        )
        user.save()
        self.stdout.write(self.style.SUCCESS('Admin admin1@test.djic utworzony pomyslnie.'))
        self.stdout.write(self.style.SUCCESS('Srodowisko testowe gotowe!'))
