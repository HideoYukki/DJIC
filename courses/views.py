import os
import datetime
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Course, Material
from users.permissions import IsCreatorOrAdmin, IsAdminRole


def _enrich_course(course_dict, students_count=None, creator_name=None):
    if creator_name is not None:
        course_dict['creator_name'] = creator_name
    if students_count is not None:
        course_dict['students_count'] = students_count
    return course_dict


def _resolve_creator_name(creator_id: str) -> str:
    try:
        from users.models import MongoUser
        from users.views import decrypt_data
        user = MongoUser.objects.get(id=creator_id)
        return decrypt_data(user.name) if user.name else ''
    except Exception:
        return ''


def _count_students(course_id: str) -> int:
    try:
        from progress.models import Enrollment
        return Enrollment.objects(course_id=course_id).count()
    except Exception:
        return 0

_THUMB_ALLOWED = ('image/jpeg', 'image/png', 'image/webp')


def _paginate(request, items):
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    return {
        'count': len(items),
        'next': None,
        'previous': None,
        'results': items[start:end],
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    qs = Course.objects(status='ACTIVE')
    if search := request.query_params.get('search'):
        qs = qs.filter(title__icontains=search)
    if category := request.query_params.get('category'):
        qs = qs.filter(category=category)
    if level := request.query_params.get('level'):
        qs = qs.filter(level=level.upper())
    courses = list(qs)
    creator_cache = {}
    items = []
    for c in courses:
        d = c.to_dict()
        if c.creator_id not in creator_cache:
            creator_cache[c.creator_id] = _resolve_creator_name(c.creator_id)
        _enrich_course(d, students_count=_count_students(str(c.id)), creator_name=creator_cache[c.creator_id])
        items.append(d)
    return Response(_paginate(request, items))


@api_view(['GET'])
@permission_classes([AllowAny])
def course_detail(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    data = course.to_dict()
    materials = [m.to_dict() for m in Material.objects(course_id=course_id).order_by('order')]
    data['materials'] = materials
    _enrich_course(
        data,
        students_count=_count_students(course_id),
        creator_name=_resolve_creator_name(course.creator_id),
    )
    return Response(data)


@api_view(['GET'])
@permission_classes([IsCreatorOrAdmin])
def creator_courses(request):
    qs = Course.objects(creator_id=str(request.user.id))
    creator_name = _resolve_creator_name(str(request.user.id))
    items = []
    for c in qs:
        d = c.to_dict()
        _enrich_course(d, students_count=_count_students(str(c.id)), creator_name=creator_name)
        items.append(d)
    return Response(_paginate(request, items))


@api_view(['POST'])
@permission_classes([IsCreatorOrAdmin])
def course_create(request):
    data = request.data
    if not data.get('title'):
        return Response({'error': 'Pole title jest wymagane.'}, status=400)
    course = Course(
        title=data['title'],
        description=data.get('description', ''),
        category=data.get('category', ''),
        thumbnail_url=data.get('thumbnail_url'),
        creator_id=str(request.user.id),
        price=data.get('price', 0),
        duration_minutes=data.get('duration_minutes', 0),
        level=data.get('level', 'BEGINNER'),
        tags=data.get('tags', []),
    )
    course.save()
    return Response(course.to_dict(), status=201)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsCreatorOrAdmin])
def course_update_delete(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)

    user_id = str(request.user.id)
    if course.creator_id != user_id and request.user.role != 'ADMIN':
        return Response({'error': 'Brak uprawnień.'}, status=403)

    if request.method == 'PATCH':
        data = request.data
        for field in ('title', 'description', 'category', 'thumbnail_url', 'price',
                      'duration_minutes', 'level', 'tags'):
            if field in data:
                setattr(course, field, data[field])
        course.updated_at = datetime.datetime.utcnow()
        course.save()
        return Response(course.to_dict())

    if request.method == 'DELETE':
        if course.status != 'DRAFT':
            return Response({'error': 'Można usuwać tylko kursy w statusie DRAFT.'}, status=400)
        course.delete()
        return Response(status=204)


@api_view(['POST'])
@permission_classes([IsCreatorOrAdmin])
def course_publish(request, course_id):
    try:
        course = Course.objects.get(id=course_id, creator_id=str(request.user.id))
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    course.status = 'REVIEW'
    course.updated_at = datetime.datetime.utcnow()
    course.save()
    return Response(course.to_dict())


@api_view(['POST'])
@permission_classes([IsAdminRole])
def course_approve(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    course.status = 'ACTIVE'
    course.published_at = datetime.datetime.utcnow()
    course.updated_at = datetime.datetime.utcnow()
    course.save()
    return Response(course.to_dict())


@api_view(['POST'])
@permission_classes([IsAdminRole])
def course_reject(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    course.status = 'DRAFT'
    course.reject_reason = request.data.get('reason', '')
    course.updated_at = datetime.datetime.utcnow()
    course.save()
    return Response(course.to_dict())


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_courses(request):
    qs = Course.objects.all()
    if status_filter := request.query_params.get('status'):
        qs = qs.filter(status=status_filter.upper())
    creator_cache = {}
    items = []
    for c in qs:
        d = c.to_dict()
        if c.creator_id not in creator_cache:
            creator_cache[c.creator_id] = _resolve_creator_name(c.creator_id)
        _enrich_course(d, students_count=_count_students(str(c.id)), creator_name=creator_cache[c.creator_id])
        items.append(d)
    return Response(_paginate(request, items))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def material_list(request, course_id):
    materials = Material.objects(course_id=course_id).order_by('order')
    return Response([m.to_dict() for m in materials])


@api_view(['POST'])
@permission_classes([IsCreatorOrAdmin])
def material_create(request, course_id):
    data = request.data
    if not data.get('title') or not data.get('type'):
        return Response({'error': 'Pola title i type są wymagane.'}, status=400)
    material = Material(
        course_id=course_id,
        title=data['title'],
        type=data['type'].upper(),
        order=data.get('order', 0),
        content=data.get('content', ''),
        duration_seconds=data.get('duration_seconds', 0),
    )
    material.save()
    return Response(material.to_dict(), status=201)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsCreatorOrAdmin])
def material_detail(request, course_id, material_id):

    try:
        material = Material.objects.get(id=material_id, course_id=course_id)
    except Exception:
        return Response({'error': 'Materiał nie istnieje.'}, status=404)

    if request.method == 'GET':
        return Response(material.to_dict())

    if request.method == 'PATCH':
        data = request.data
        for field in ('title', 'type', 'order', 'content', 'duration_seconds'):
            if field in data:
                setattr(material, field, data[field])
        material.save()
        return Response(material.to_dict())

    if request.method == 'DELETE':
        material.delete()
        return Response(status=204)


_VIDEO_ALLOWED_TYPES = ('video/mp4', 'video/webm')
_VIDEO_ALLOWED_EXTS  = ('mp4', 'webm')
_VIDEO_MAX_SIZE      = 500 * 1024 * 1024  # 500 MB


@api_view(['POST'])
@permission_classes([IsCreatorOrAdmin])
def material_video_upload(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    if course.creator_id != str(request.user.id) and request.user.role != 'ADMIN':
        return Response({'error': 'Brak uprawnień.'}, status=403)
    if 'video' not in request.FILES:
        return Response({'error': 'Brak pliku (pole: video).'}, status=400)
    f = request.FILES['video']
    ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
    if f.content_type not in _VIDEO_ALLOWED_TYPES and ext not in _VIDEO_ALLOWED_EXTS:
        return Response({'error': 'Dozwolone formaty: MP4, WebM (Firefox/Chrome).'}, status=400)
    if f.size > _VIDEO_MAX_SIZE:
        return Response({'error': 'Maksymalny rozmiar pliku to 500 MB.'}, status=400)
    import uuid
    filename = f'{uuid.uuid4().hex}.{ext or "mp4"}'
    save_dir  = os.path.join(settings.MEDIA_ROOT, 'videos', course_id)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    with open(save_path, 'wb') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    video_url = request.build_absolute_uri(f'{settings.MEDIA_URL}videos/{course_id}/{filename}')
    return Response({'url': video_url})


@api_view(['POST'])
@permission_classes([IsCreatorOrAdmin])
def course_thumbnail_upload(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    if course.creator_id != str(request.user.id) and request.user.role != 'ADMIN':
        return Response({'error': 'Brak uprawnień.'}, status=403)
    if 'file' not in request.FILES:
        return Response({'error': 'Brak pliku (pole: file).'}, status=400)
    f = request.FILES['file']
    if f.content_type not in _THUMB_ALLOWED:
        return Response({'error': 'Dozwolone formaty: JPG, PNG, WebP.'}, status=400)
    if f.size > 5 * 1024 * 1024:
        return Response({'error': 'Maksymalny rozmiar pliku to 5 MB.'}, status=400)
    ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else 'jpg'
    filename = f'thumb_{course_id}.{ext}'
    save_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    thumbnail_url = request.build_absolute_uri(f'{settings.MEDIA_URL}thumbnails/{filename}')
    course.thumbnail_url = thumbnail_url
    course.updated_at = datetime.datetime.utcnow()
    course.save()
    return Response({'thumbnail_url': thumbnail_url})


@api_view(['PATCH'])
@permission_classes([IsCreatorOrAdmin])
def material_reorder(request, course_id):
    # body: [{id, order}, ...]
    items = request.data
    if not isinstance(items, list):
        return Response({'error': 'Oczekiwana lista [{id, order}].'}, status=400)
    for item in items:
        try:
            m = Material.objects.get(id=item['id'], course_id=course_id)
            m.order = int(item['order'])
            m.save()
        except Exception:
            pass
    materials = Material.objects(course_id=course_id).order_by('order')
    return Response([m.to_dict() for m in materials])
