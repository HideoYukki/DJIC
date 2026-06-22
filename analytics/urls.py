from django.urls import path
from . import views

urlpatterns = [
    path('courses/<str:course_id>/', views.course_analytics),
    path('courses/<str:course_id>/students/', views.course_students),
    path('courses/<str:course_id>/views/', views.course_views_per_day),
    path('courses/<str:course_id>/dropouts/', views.course_dropouts),
    path('courses/<str:course_id>/report/', views.course_report),
    path('courses/<str:course_id>/report/pdf/', views.course_report_pdf),
    path('creator/summary/', views.creator_summary),
    path('admin/summary/', views.admin_summary),
]
