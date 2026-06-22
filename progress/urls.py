from django.urls import path
from . import views

urlpatterns = [
    path('enrollments/', views.enrollments),
    path('enrollments/<str:course_id>/', views.unenroll),
    path('progress/', views.progress_list),
    path('progress/<str:course_id>/', views.progress_detail),
    path('progress/<str:course_id>/complete/', views.complete_material),
    path('achievements/', views.achievements),
]
