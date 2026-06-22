from django.urls import re_path
from notifications import consumers as notif_consumers
from analytics import consumers as analytics_consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', notif_consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/analytics/(?P<course_id>[^/]+)/$', analytics_consumers.AnalyticsConsumer.as_asgi()),
]
