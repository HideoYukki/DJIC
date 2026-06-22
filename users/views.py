import os
import hashlib
import secrets
import datetime
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError  # noqa: F401 used in token_refresh
from .models import MongoUser
from .permissions import IsAdminRole


load_dotenv()


class AuthRateThrottle(AnonRateThrottle):
    scope = 'auth'


def _fernet():
    return Fernet(os.getenv('ENCRYPTION_KEY').encode())


def encrypt_data(text: str) -> str:
    return _fernet().encrypt(text.encode()).decode()


def decrypt_data(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()


def hash_data(text: str) -> str:
    return hashlib.sha3_256(text.encode()).hexdigest()


def _serialize_user(user: MongoUser) -> dict:
    try:
        email = decrypt_data(user.email)
    except Exception:
        email = ''
    try:
        name = decrypt_data(user.name) if user.name else ''
    except Exception:
        name = ''
    return {
        'id': str(user.id),
        'name': name,
        'email': email,
        'role': user.role,
        'avatar_url': user.avatar_url,
        'bio': user.bio,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None,
    }


def _make_tokens(user: MongoUser) -> dict:
    refresh = RefreshToken()
    refresh['user_id'] = str(user.id)
    try:
        refresh['email'] = decrypt_data(user.email)
        refresh['name'] = decrypt_data(user.name) if user.name else ''
    except Exception:
        refresh['email'] = ''
        refresh['name'] = ''
    refresh['role'] = user.role
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def register_user(request):
    data = request.data
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    role = data.get('role', 'STUDENT').upper()

    if not all([email, password, name]):
        return Response({'error': 'Pola email, password i name są wymagane.'}, status=400)

    if role not in ('STUDENT', 'CREATOR'):
        role = 'STUDENT'

    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Niepoprawny format adresu e-mail.'}, status=400)

    e_hash = hash_data(email)
    if MongoUser.objects(email_hash=e_hash).first():
        return Response({'error': 'Użytkownik o tym adresie e-mail już istnieje.'}, status=400)

    require_verification = settings.REQUIRE_EMAIL_VERIFICATION
    verification_token = secrets.token_urlsafe(32) if require_verification else None

    new_user = MongoUser(
        email=encrypt_data(email),
        email_hash=e_hash,
        password=make_password(password),
        name=encrypt_data(name),
        role=role,
        is_verified=not require_verification,
        verification_token=verification_token,
        is_active=True,
    )
    new_user.save()

    if require_verification:
        verify_link = f'{settings.FRONTEND_URL}/verify-email/{verification_token}'
        try:
            send_mail(
                subject='Weryfikacja konta — DJIC',
                message=f'Kliknij w link, aby aktywować konto:\n{verify_link}\n\nLink ważny 24 godziny.',
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass
        return Response({'message': 'Konto utworzone. Sprawdź e-mail, aby je zweryfikować.'}, status=201)

    return Response({'message': 'Konto utworzone.'}, status=201)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    from django.shortcuts import redirect
    user = MongoUser.objects(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        user.save()
        return redirect(f'{settings.FRONTEND_URL}/login?verified=true')
    return redirect(f'{settings.FRONTEND_URL}/login?verified=false')


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def login_user(request):
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    e_hash = hash_data(email)
    user = MongoUser.objects(email_hash=e_hash).first()

    if not user or not check_password(password, user.password):
        return Response({'error': 'Nieprawidłowe dane logowania.'}, status=401)

    if not user.is_verified:
        return Response({'error': 'Konto niezweryfikowane. Sprawdź e-mail.'}, status=403)

    if not user.is_active:
        return Response({'error': 'Konto zostało zablokowane.'}, status=403)

    user.last_login = datetime.datetime.utcnow()
    user.save()

    tokens = _make_tokens(user)
    return Response({
        **tokens,
        'user': _serialize_user(user),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    return Response({'message': 'Wylogowano pomyślnie.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'error': 'Brak tokenu refresh.'}, status=400)
    try:
        token = RefreshToken(refresh_token)
        return Response({'access': str(token.access_token)})
    except TokenError as e:
        return Response({'error': 'Nieprawidłowy lub wygasły token.'}, status=401)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def forgot_password(request):
    email = request.data.get('email', '').strip().lower()
    if not email:
        return Response({'error': 'Pole email jest wymagane.'}, status=400)

    e_hash = hash_data(email)
    user = MongoUser.objects(email_hash=e_hash).first()

    # Odpowiadamy zawsze tak samo (bezpieczeństwo — nie ujawniamy, czy konto istnieje)
    if user and user.is_active:
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        user.save()
        reset_link = f'{settings.FRONTEND_URL}/reset-password/{reset_token}'
        try:
            send_mail(
                subject='Reset hasła — DJIC',
                message=f'Kliknij w link, aby zresetować hasło:\n{reset_link}\n\nLink ważny 1 godzinę.',
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

    return Response({'message': 'Jeśli konto istnieje, wysłaliśmy link resetujący.'})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def reset_password(request):
    token = request.data.get('token')
    new_password = request.data.get('password')

    if not token or not new_password:
        return Response({'error': 'Pola token i password są wymagane.'}, status=400)

    user = MongoUser.objects(password_reset_token=token).first()
    if not user:
        return Response({'error': 'Nieprawidłowy token.'}, status=400)

    if user.password_reset_expires and user.password_reset_expires < datetime.datetime.utcnow():
        return Response({'error': 'Token wygasł.'}, status=400)

    user.password = make_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.save()
    return Response({'message': 'Hasło zostało zmienione.'})


_AVATAR_ALLOWED = ('image/jpeg', 'image/png', 'image/webp')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    if 'file' not in request.FILES:
        return Response({'error': 'Brak pliku (pole: file).'}, status=400)
    f = request.FILES['file']
    if f.content_type not in _AVATAR_ALLOWED:
        return Response({'error': 'Dozwolone formaty: JPG, PNG, WebP.'}, status=400)
    if f.size > 2 * 1024 * 1024:
        return Response({'error': 'Maksymalny rozmiar pliku to 2 MB.'}, status=400)
    ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else 'jpg'
    filename = f'avatar_{request.user.id}.{ext}'
    save_path = os.path.join(settings.MEDIA_ROOT, 'avatars', filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    avatar_url = request.build_absolute_uri(f'{settings.MEDIA_URL}avatars/{filename}')
    request.user.avatar_url = avatar_url
    request.user.save()
    return Response({'avatar_url': avatar_url})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    if request.method == 'GET':
        return Response(_serialize_user(user))

    data = request.data
    if 'name' in data:
        user.name = encrypt_data(data['name'].strip())
    if 'bio' in data:
        user.bio = data['bio']
    user.save()
    return Response(_serialize_user(user))


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({'error': 'Pola old_password i new_password są wymagane.'}, status=400)

    user = request.user
    if not check_password(old_password, user.password):
        return Response({'error': 'Obecne hasło jest nieprawidłowe.'}, status=400)

    user.password = make_password(new_password)
    user.save()
    return Response({'message': 'Hasło zostało zmienione.'})


@api_view(['GET', 'POST'])
@permission_classes([IsAdminRole])
def admin_users_list(request):
    if request.method == 'GET':
        role_filter = request.query_params.get('role')
        qs = MongoUser.objects.all()
        if role_filter:
            qs = qs.filter(role=role_filter.upper())
        all_results = [_serialize_user(u) for u in qs]
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        return Response({
            'count': len(all_results),
            'page': page,
            'page_size': page_size,
            'results': all_results[start:end],
        })

    data = request.data
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    role = data.get('role', 'STUDENT').upper()

    if not all([email, password, name]):
        return Response({'error': 'Pola email, password i name są wymagane.'}, status=400)

    e_hash = hash_data(email)
    if MongoUser.objects(email_hash=e_hash).first():
        return Response({'error': 'Użytkownik już istnieje.'}, status=400)

    user = MongoUser(
        email=encrypt_data(email),
        email_hash=e_hash,
        password=make_password(password),
        name=encrypt_data(name),
        role=role,
        is_verified=True,
        is_active=True,
    )
    user.save()
    return Response(_serialize_user(user), status=201)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdminRole])
def admin_user_detail(request, user_id):
    try:
        user = MongoUser.objects.get(id=user_id)
    except Exception:
        return Response({'error': 'Użytkownik nie istnieje.'}, status=404)

    if request.method == 'GET':
        from courses.models import Course
        from progress.models import Enrollment
        data = _serialize_user(user)
        if user.role == 'STUDENT':
            data['courses_count'] = Enrollment.objects(user_id=user_id).count()
        else:
            data['courses_count'] = Course.objects(creator_id=user_id).count()
        return Response(data)

    if request.method == 'PATCH':
        if 'role' in request.data:
            new_role = request.data['role'].upper()
            if new_role in ('STUDENT', 'CREATOR', 'ADMIN'):
                user.role = new_role
        if 'is_active' in request.data:
            user.is_active = bool(request.data['is_active'])
        user.save()
        return Response(_serialize_user(user))

    if request.method == 'DELETE':
        from courses.models import Course, Material
        from progress.models import Enrollment, Progress, Achievement
        uid = str(user.id)
        if user.role in ('CREATOR', 'ADMIN'):
            creator_courses = list(Course.objects(creator_id=uid))
            for course in creator_courses:
                cid = str(course.id)
                Material.objects(course_id=cid).delete()
                Enrollment.objects(course_id=cid).delete()
                Progress.objects(course_id=cid).delete()
                course.delete()
        Enrollment.objects(user_id=uid).delete()
        Progress.objects(user_id=uid).delete()
        Achievement.objects(user_id=uid).delete()
        user.delete()
        return Response(status=204)
