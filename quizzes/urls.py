from django.urls import path
from . import views

urlpatterns = [
    path('courses/<str:course_id>/quizzes/', views.quiz_create),
    path('courses/<str:course_id>/quizzes/<str:quiz_id>/', views.quiz_detail),
    path('courses/<str:course_id>/quizzes/<str:quiz_id>/edit/', views.quiz_update),
    path('courses/<str:course_id>/quizzes/<str:quiz_id>/submit/', views.quiz_submit),
    path('courses/<str:course_id>/quizzes/<str:quiz_id>/result/', views.quiz_result),
]
