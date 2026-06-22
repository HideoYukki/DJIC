from django.urls import path
from . import views

urlpatterns = [
    # Static paths must come BEFORE <str:course_id> patterns to avoid shadowing
    path('courses/', views.course_list),
    path('courses/creator/', views.creator_courses),
    path('courses/new/', views.course_create),
    path('admin/courses/', views.admin_courses),

    path('courses/<str:course_id>/', views.course_detail),
    path('courses/<str:course_id>/edit/', views.course_update_delete),
    path('courses/<str:course_id>/publish/', views.course_publish),
    path('courses/<str:course_id>/thumbnail/', views.course_thumbnail_upload),
    path('courses/<str:course_id>/approve/', views.course_approve),
    path('courses/<str:course_id>/reject/', views.course_reject),

    path('courses/<str:course_id>/materials/', views.material_list),
    path('courses/<str:course_id>/materials/new/', views.material_create),
    path('courses/<str:course_id>/materials/reorder/', views.material_reorder),
    path('courses/<str:course_id>/materials/upload-video/', views.material_video_upload),
    path('courses/<str:course_id>/materials/<str:material_id>/', views.material_detail),
]
