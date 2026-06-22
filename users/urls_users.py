from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.me),
    path('me/avatar/', views.upload_avatar),
    path('me/password/', views.change_password),
    path('', views.admin_users_list),
    path('<str:user_id>/', views.admin_user_detail),
]
