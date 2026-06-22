from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user),
    path('verify/<str:token>/', views.verify_email),
    path('login/', views.login_user),
    path('logout/', views.logout_user),
    path('token/refresh/', views.token_refresh),
    path('forgot-password/', views.forgot_password),
    path('reset-password/', views.reset_password),
]
