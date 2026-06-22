import io
import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.permissions import IsCreatorOrAdmin, IsAdminRole
from courses.models import Course, Material
from progress.models import Enrollment, Progress, Achievement
from users.models import MongoUser
from users.views import decrypt_data


def _require_course_owner(request, course):
    if request.user.role != 'ADMIN' and str(course.creator_id) != str(request.user.id):
        return Response({'error': 'Brak dostępu do tego kursu.'}, status=403)
    return None


@api_view(['GET'])
@permission_classes([IsCreatorOrAdmin])
def course_analytics(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    err = _require_course_owner(request, course)
    if err:
        return err

    enrollments = Enrollment.objects(course_id=course_id)
    total_enrolled = enrollments.count()
    total_completed = enrollments.filter(completed_at__ne=None).count()
    completion_rate = round(total_completed / total_enrolled * 100, 1) if total_enrolled > 0 else 0

    material_count = Material.objects(course_id=course_id).count()
    progress_records = list(Progress.objects(course_id=course_id))
    avg_progress = 0
    if progress_records and material_count > 0:
        avg_progress = round(
            sum(len(p.completed_material_ids) for p in progress_records) / len(progress_records) / material_count * 100,
            1,
        )

    return Response({
        'course_id': course_id,
        'title': course.title,
        'total_enrolled': total_enrolled,
        'total_completed': total_completed,
        'completion_rate': completion_rate,
        'avg_progress_percent': avg_progress,
        'total_materials': material_count,
    })


@api_view(['GET'])
@permission_classes([IsCreatorOrAdmin])
def course_students(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    err = _require_course_owner(request, course)
    if err:
        return err
    enrollments = Enrollment.objects(course_id=course_id)
    results = []
    for e in enrollments:
        try:
            user = MongoUser.objects.get(id=e.user_id)
            try:
                name = decrypt_data(user.name) if user.name else ''
                email = decrypt_data(user.email)
            except Exception:
                name = ''
                email = ''
            prog = Progress.objects(user_id=e.user_id, course_id=course_id).first()
            material_count = Material.objects(course_id=course_id).count()
            completed = len(prog.completed_material_ids) if prog else 0
            progress_pct = round(completed / material_count * 100, 1) if material_count > 0 else 0
            results.append({
                'user_id': e.user_id,
                'name': name,
                'email': email,
                'enrolled_at': e.enrolled_at.isoformat() if e.enrolled_at else None,
                'completed_at': e.completed_at.isoformat() if e.completed_at else None,
                'progress_percent': progress_pct,
                'xp_earned': prog.xp_earned if prog else 0,
            })
        except Exception:
            pass

    return Response({'count': len(results), 'results': results})


@api_view(['GET'])
@permission_classes([IsCreatorOrAdmin])
def course_report(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    err = _require_course_owner(request, course)
    if err:
        return err

    materials = list(Material.objects(course_id=course_id).order_by('order'))
    enrollments = list(Enrollment.objects(course_id=course_id))
    students_data = []

    for e in enrollments:
        try:
            user = MongoUser.objects.get(id=e.user_id)
            try:
                name = decrypt_data(user.name) if user.name else ''
            except Exception:
                name = ''
            prog = Progress.objects(user_id=e.user_id, course_id=course_id).first()
            completed_ids = prog.completed_material_ids if prog else []
            material_progress = [
                {'material_id': str(m.id), 'title': m.title, 'completed': str(m.id) in completed_ids}
                for m in materials
            ]
            students_data.append({
                'user_id': e.user_id,
                'name': name,
                'enrolled_at': e.enrolled_at.isoformat() if e.enrolled_at else None,
                'completed_at': e.completed_at.isoformat() if e.completed_at else None,
                'material_progress': material_progress,
                'xp_earned': prog.xp_earned if prog else 0,
            })
        except Exception:
            pass

    return Response({
        'course_id': course_id,
        'title': course.title,
        'students': students_data,
    })


@api_view(['GET'])
@permission_classes([IsCreatorOrAdmin])
def creator_summary(request):
    user_id = str(request.user.id)
    courses = list(Course.objects(creator_id=user_id))
    course_ids = [str(c.id) for c in courses]

    total_students = 0
    for cid in course_ids:
        total_students += Enrollment.objects(course_id=cid).count()

    return Response({
        'total_courses': len(courses),
        'active_courses': sum(1 for c in courses if c.status == 'ACTIVE'),
        'draft_courses': sum(1 for c in courses if c.status == 'DRAFT'),
        'total_students': total_students,
    })


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_summary(request):
    return Response({
        'total_users': MongoUser.objects.count(),
        'total_courses': Course.objects.count(),
        'active_courses': Course.objects(status='ACTIVE').count(),
        'pending_review': Course.objects(status='REVIEW').count(),
        'total_enrollments': Enrollment.objects.count(),
    })


@api_view(['GET'])
@permission_classes([IsCreatorOrAdmin])
def course_views_per_day(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    err = _require_course_owner(request, course)
    if err:
        return err
    try:
        period = int(request.query_params.get('period', '14').rstrip('d'))
    except ValueError:
        period = 14
    today = datetime.datetime.utcnow().date()
    since = today - datetime.timedelta(days=period - 1)

    enrollments = Enrollment.objects(
        course_id=course_id,
        enrolled_at__gte=datetime.datetime.combine(since, datetime.time.min),
    )
    day_counts = {}
    for e in enrollments:
        if e.enrolled_at:
            day = e.enrolled_at.date().isoformat()
            day_counts[day] = day_counts.get(day, 0) + 1

    days = [
        {'date': (since + datetime.timedelta(days=i)).isoformat(),
         'count': day_counts.get((since + datetime.timedelta(days=i)).isoformat(), 0)}
        for i in range(period)
    ]
    return Response({'days': days})


@api_view(['GET'])
@permission_classes([IsCreatorOrAdmin])
def course_dropouts(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    err = _require_course_owner(request, course)
    if err:
        return err
    materials = list(Material.objects(course_id=course_id).order_by('order'))
    enrolled_count = Enrollment.objects(course_id=course_id).count()
    all_progress = list(Progress.objects(course_id=course_id))

    results = []
    for m in materials:
        mid = str(m.id)
        completions = sum(1 for p in all_progress if mid in p.completed_material_ids)
        dropout_rate = round((enrolled_count - completions) / enrolled_count * 100, 1) if enrolled_count > 0 else 0
        results.append({
            'material_id': mid,
            'material_title': m.title,
            'completions': completions,
            'enrolled': enrolled_count,
            'dropout_rate': dropout_rate,
        })

    results.sort(key=lambda x: x['dropout_rate'], reverse=True)
    return Response({'count': len(results), 'results': results})


@api_view(['GET'])
@permission_classes([IsCreatorOrAdmin])
def course_report_pdf(request, course_id):
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
    except ImportError:
        return Response({'error': 'Biblioteka reportlab nie jest zainstalowana.'}, status=501)

    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return Response({'error': 'Kurs nie istnieje.'}, status=404)
    err = _require_course_owner(request, course)
    if err:
        return err

    enrolled_count = Enrollment.objects(course_id=course_id).count()
    completed_count = Enrollment.objects(course_id=course_id, completed_at__ne=None).count()
    completion_rate = round(completed_count / enrolled_count * 100, 1) if enrolled_count > 0 else 0
    total_materials = Material.objects(course_id=course_id).count()

    buffer = io.BytesIO()
    c = rl_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 60

    def draw_line(text, bold=False, size=11, offset=18):
        nonlocal y
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
        c.drawString(50, y, text)
        y -= offset
        if y < 60:
            c.showPage()
            y = height - 60

    draw_line(f'Raport kursu: {course.title}', bold=True, size=16, offset=30)
    draw_line(f'Wygenerowano: {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}', size=9, offset=24)
    draw_line('Statystyki kursu', bold=True, size=13, offset=22)
    draw_line(f'Zapisanych uczniów: {enrolled_count}')
    draw_line(f'Ukończyło kurs: {completed_count}')
    draw_line(f'Wskaźnik ukończenia: {completion_rate}%')
    draw_line(f'Liczba materiałów: {total_materials}')
    y -= 10

    all_progress = list(Progress.objects(course_id=course_id))
    materials = list(Material.objects(course_id=course_id).order_by('order'))
    if materials:
        draw_line('Postęp per materiał', bold=True, size=13, offset=22)
        for m in materials:
            mid = str(m.id)
            completions = sum(1 for p in all_progress if mid in p.completed_material_ids)
            pct = round(completions / enrolled_count * 100) if enrolled_count > 0 else 0
            draw_line(f'  {m.title[:60]}: {completions}/{enrolled_count} ({pct}%)', size=10)

    c.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="raport_{course_id}.pdf"'
    return response
