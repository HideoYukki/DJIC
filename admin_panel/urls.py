from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.logs_list),
    path('logs/export/', views.logs_export),
    path('settings/', views.settings_view),
]
