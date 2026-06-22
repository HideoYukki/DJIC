from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list),
    path('<str:notification_id>/read/', views.mark_read),
    path('read-all/', views.mark_all_read),
]
