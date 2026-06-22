import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Quiz, QuizQuestion, QuizOption, QuizResult
from users.permissions import IsCreatorOrAdmin


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_detail(request, course_id, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, course_id=course_id)
    except Exception:
        return Response({'error': 'Quiz nie istnieje.'}, status=404)
    include_answers = getattr(request.user, 'role', '') in ('CREATOR', 'ADMIN')
    return Response(quiz.to_dict(include_answers=include_answers))


@api_view(['POST'])
@permission_classes([IsCreatorOrAdmin])
def quiz_create(request, course_id):
    data = request.data
    if not data.get('title'):
        return Response({'error': 'Pole title jest wymagane.'}, status=400)
    quiz = Quiz(
        course_id=course_id,
        material_id=data.get('material_id'),
        title=data['title'],
        time_limit_seconds=data.get('time_limit_seconds', 300),
    )
    quiz.save()
    return Response(quiz.to_dict(), status=201)


@api_view(['PUT'])
@permission_classes([IsCreatorOrAdmin])
def quiz_update(request, course_id, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, course_id=course_id)
    except Exception:
        return Response({'error': 'Quiz nie istnieje.'}, status=404)

    data = request.data
    if 'title' in data:
        quiz.title = data['title']
    if 'time_limit_seconds' in data:
        quiz.time_limit_seconds = int(data['time_limit_seconds'])

    if 'questions' in data:
        new_questions = []
        for q_data in data['questions']:
            options = []
            for o_data in q_data.get('options', []):
                options.append(QuizOption(
                    id=o_data.get('id', str(uuid.uuid4())),
                    text=o_data['text'],
                ))
            new_questions.append(QuizQuestion(
                id=q_data.get('id', str(uuid.uuid4())),
                text=q_data['text'],
                options=options,
                correct_option_id=q_data.get('correct_option_id', ''),
                points=q_data.get('points', 1),
            ))
        quiz.questions = new_questions

    quiz._mark_as_changed('questions')
    quiz.save()
    return Response(quiz.to_dict(include_answers=True))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_submit(request, course_id, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, course_id=course_id)
    except Exception:
        return Response({'error': 'Quiz nie istnieje.'}, status=404)

    answers = request.data.get('answers', {})
    user_id = str(request.user.id)

    score = 0
    max_score = sum(q.points for q in quiz.questions)
    correct_answers = {}

    for question in quiz.questions:
        correct_answers[question.id] = question.correct_option_id
        selected = answers.get(question.id)
        if selected == question.correct_option_id:
            score += question.points

    passed = max_score > 0 and score / max_score >= 0.6
    xp_earned = int(50 * (score / max_score)) if max_score > 0 else 0

    result = QuizResult.objects(user_id=user_id, quiz_id=quiz_id).first()
    if not result:
        result = QuizResult(user_id=user_id, quiz_id=quiz_id, course_id=course_id)

    result.score = score
    result.max_score = max_score
    result.passed = passed
    result.xp_earned = xp_earned
    import datetime
    result.completed_at = datetime.datetime.utcnow()
    result.save()

    return Response({
        'score': score,
        'max_score': max_score,
        'passed': passed,
        'xp_earned': xp_earned,
        'correct_answers': correct_answers,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_result(request, course_id, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, course_id=course_id)
    except Exception:
        return Response({'error': 'Quiz nie istnieje.'}, status=404)

    user_id = str(request.user.id)
    result = QuizResult.objects(user_id=user_id, quiz_id=quiz_id).first()
    if not result:
        return Response({'error': 'Brak wyników dla tego quizu.'}, status=404)

    correct_answers = {q.id: q.correct_option_id for q in quiz.questions}

    return Response({
        **result.to_dict(),
        'correct_answers': correct_answers,
    })
