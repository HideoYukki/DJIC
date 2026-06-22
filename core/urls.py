from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/auth/', include('users.urls_auth')),
    path('api/users/', include('users.urls_users')),
    path('api/', include('courses.urls')),
    path('api/', include('quizzes.urls')),
    path('api/', include('progress.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/admin/', include('admin_panel.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
