from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    user_id = str(request.user.id)
    items = [n.to_dict() for n in Notification.objects(user_id=user_id).order_by('-created_at')]
    unread_count = Notification.objects(user_id=user_id, is_read=False).count()
    return Response({'count': len(items), 'unread_count': unread_count, 'results': items})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_read(request, notification_id):
    user_id = str(request.user.id)
    try:
        notif = Notification.objects.get(id=notification_id, user_id=user_id)
    except Exception:
        return Response({'error': 'Powiadomienie nie istnieje.'}, status=404)
    notif.is_read = True
    notif.save()
    return Response(notif.to_dict())


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    user_id = str(request.user.id)
    Notification.objects(user_id=user_id, is_read=False).update(set__is_read=True)
    return Response({'message': 'Wszystkie powiadomienia oznaczone jako przeczytane.'})
