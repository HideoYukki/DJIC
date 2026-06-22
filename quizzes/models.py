import datetime
from mongoengine import (
    Document, StringField, DateTimeField, IntField,
    ListField, EmbeddedDocument, EmbeddedDocumentField,
    BooleanField, FloatField,
)


class QuizOption(EmbeddedDocument):
    id = StringField(required=True)
    text = StringField(required=True)


class QuizQuestion(EmbeddedDocument):
    id = StringField(required=True)
    text = StringField(required=True)
    options = ListField(EmbeddedDocumentField(QuizOption))
    correct_option_id = StringField(required=True)
    points = IntField(default=1)


class Quiz(Document):
    course_id = StringField(required=True)
    material_id = StringField()
    title = StringField(required=True)
    time_limit_seconds = IntField(default=300)
    questions = ListField(EmbeddedDocumentField(QuizQuestion))
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'quizzes'}

    def to_dict(self, include_answers=False):
        questions_data = []
        for q in self.questions:
            q_dict = {
                'id': q.id,
                'text': q.text,
                'options': [{'id': o.id, 'text': o.text} for o in q.options],
                'points': q.points,
            }
            if include_answers:
                q_dict['correct_option_id'] = q.correct_option_id
            questions_data.append(q_dict)
        return {
            'id': str(self.id),
            'course_id': self.course_id,
            'material_id': self.material_id,
            'title': self.title,
            'time_limit_seconds': self.time_limit_seconds,
            'questions': questions_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class QuizResult(Document):
    user_id = StringField(required=True)
    quiz_id = StringField(required=True)
    course_id = StringField(required=True)
    score = IntField(default=0)
    max_score = IntField(default=0)
    passed = BooleanField(default=False)
    xp_earned = IntField(default=0)
    answers = ListField(StringField())  # list of selected option_ids
    completed_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {'collection': 'quiz_results'}

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'course_id': self.course_id,
            'score': self.score,
            'max_score': self.max_score,
            'passed': self.passed,
            'xp_earned': self.xp_earned,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
