import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Enrollment, Progress, Achievement, BADGE_CATALOGUE
from courses.models import Course, Material


def _grant_achievement(user_id, badge_id):
    if not Achievement.objects(user_id=user_id, badge_id=badge_id).first():
        badge_info = BADGE_CATALOGUE.get(badge_id, {})
        Achievement(user_id=user_id, badge_id=badge_id, xp_value=badge_info.get('xp', 0)).save()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def enrollments(request):
    user_id = str(request.user.id)

    if request.method == 'GET':
        enrolled = Enrollment.objects(user_id=user_id)
        items = []
        for e in enrolled:
            d = e.to_dict()
            try:
                course = Course.objects.get(id=e.course_id)
                from courses.views import _resolve_creator_name, _count_students
                course_dict = course.to_dict()
                course_dict['creator_name'] = _resolve_creator_name(course.creator_id)
                course_dict['students_count'] = _count_students(str(course.id))
                d['course'] = course_dict
            except Exception:
                d['course'] = None
            prog = Progress.objects(user_id=user_id, course_id=e.course_id).first()
            d['progress'] = prog.to_dict() if prog else None
            items.append(d)
        return Response({'count': len(items), 'results': items})

    course_id = request.data.get('course_id')
    if not course_id:
        return Response({'error': 'Pole course_id jest wymagane.'}, status=400)

    try:
        Course.objects.get(id=course_id, status='ACTIVE')
    except Exception:
        return Response({'error': 'Kurs nie istnieje lub nie jest aktywny.'}, status=404)

    if Enrollment.objects(user_id=user_id, course_id=course_id).first():
        return Response({'error': 'Już jesteś zapisany na ten kurs.'}, status=400)

    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    enrollment.save()

    if Enrollment.objects(user_id=user_id).count() == 1:
        _grant_achievement(user_id, 'first_enrollment')

    return Response(enrollment.to_dict(), status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unenroll(request, course_id):
    user_id = str(request.user.id)
    enrollment = Enrollment.objects(user_id=user_id, course_id=course_id).first()
    if not enrollment:
        return Response({'error': 'Nie jesteś zapisany na ten kurs.'}, status=404)
    enrollment.delete()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_list(request):
    user_id = str(request.user.id)
    items = [p.to_dict() for p in Progress.objects(user_id=user_id)]
    return Response({'count': len(items), 'results': items})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_detail(request, course_id):
    user_id = str(request.user.id)
    prog = Progress.objects(user_id=user_id, course_id=course_id).first()
    if not prog:
        return Response({'user_id': user_id, 'course_id': course_id, 'completed_material_ids': [], 'xp_earned': 0})
    return Response(prog.to_dict())


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_material(request, course_id):
    user_id = str(request.user.id)
    material_id = request.data.get('material_id')
    if not material_id:
        return Response({'error': 'Pole material_id jest wymagane.'}, status=400)

    if not Enrollment.objects(user_id=user_id, course_id=course_id).first():
        return Response({'error': 'Nie jesteś zapisany na ten kurs.'}, status=403)

    prog = Progress.objects(user_id=user_id, course_id=course_id).first()
    if not prog:
        prog = Progress(user_id=user_id, course_id=course_id)

    if material_id not in prog.completed_material_ids:
        prog.completed_material_ids.append(material_id)
        try:
            material = Material.objects.get(id=material_id)
            if material.type in ('VIDEO', 'TEXT'):
                prog.xp_earned += 10
        except Exception:
            pass

    prog.last_activity_at = datetime.datetime.utcnow()
    prog._mark_as_changed('completed_material_ids')
    prog.save()

    total_materials = Material.objects(course_id=course_id).count()
    if total_materials > 0 and len(prog.completed_material_ids) >= total_materials:
        enrollment = Enrollment.objects(user_id=user_id, course_id=course_id).first()
        if enrollment and not enrollment.completed_at:
            enrollment.completed_at = datetime.datetime.utcnow()
            enrollment.save()
            _grant_achievement(user_id, 'first_completion')

    total_xp = sum(p.xp_earned for p in Progress.objects(user_id=user_id))
    if total_xp >= 100:
        _grant_achievement(user_id, 'xp_100')
    if total_xp >= 500:
        _grant_achievement(user_id, 'xp_500')

    return Response(prog.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def achievements(request):
    user_id = str(request.user.id)
    earned_map = {a.badge_id: a for a in Achievement.objects(user_id=user_id)}
    total_xp = sum(a.xp_value for a in earned_map.values())

    results = []
    for badge_id, badge_info in BADGE_CATALOGUE.items():
        a = earned_map.get(badge_id)
        results.append({
            'badge_id': badge_id,
            'badge_name': badge_info.get('name', badge_id),
            'badge_description': badge_info.get('description', ''),
            'xp_value': badge_info.get('xp', 0),
            'earned_at': a.earned_at.isoformat() if a else None,
        })

    return Response({'count': len(results), 'total_xp': total_xp, 'results': results})
