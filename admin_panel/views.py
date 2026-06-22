import csv
import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.permissions import IsAdminRole
from .models import SystemLog, SystemSettings


@api_view(['GET'])
@permission_classes([IsAdminRole])
def logs_list(request):
    qs = SystemLog.objects.all().order_by('-created_at')

    if level := request.query_params.get('level'):
        qs = qs.filter(level=level.upper())
    if source := request.query_params.get('source'):
        qs = qs.filter(source=source)
    if date_str := request.query_params.get('date'):
        try:
            d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            qs = qs.filter(created_at__gte=d, created_at__lt=d + datetime.timedelta(days=1))
        except ValueError:
            pass

    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 50))
    items = list(qs)
    start = (page - 1) * page_size
    end = start + page_size
    results = [log.to_dict() for log in items[start:end]]

    return Response({'count': len(items), 'results': results})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAdminRole])
def settings_view(request):
    if request.method == 'GET':
        all_settings = {s.key: s.value for s in SystemSettings.objects.all()}
        defaults = {
            'maintenance_mode': 'false',
            'registration_enabled': 'true',
            'max_courses_per_creator': '50',
        }
        defaults.update(all_settings)
        return Response(defaults)

    for key, value in request.data.items():
        setting = SystemSettings.objects(key=key).first()
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.datetime.utcnow()
            setting.save()
        else:
            SystemSettings(key=key, value=str(value)).save()

    all_settings = {s.key: s.value for s in SystemSettings.objects.all()}
    return Response(all_settings)


@api_view(['GET'])
@permission_classes([IsAdminRole])
def logs_export(request):
    qs = SystemLog.objects.all().order_by('-created_at')
    if level := request.query_params.get('level'):
        qs = qs.filter(level=level.upper())

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="system_logs.csv"'
    response.write('﻿')  # BOM dla zgodności z Excelem

    writer = csv.writer(response)
    writer.writerow(['Data', 'Poziom', 'Źródło', 'Wiadomość'])
    for log in qs:
        writer.writerow([
            log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
            log.level or '',
            log.source or '',
            log.message or '',
        ])
    return response
