from django.shortcuts import render
from models import *
import datetime
import json
from django.http import HttpResponse
from django.db.models import Count

from django.views.decorators.csrf import csrf_exempt


# Create your views here.


def index(request):
    return render(request, 'rally/index.html')


def manage(request):
    return render(request, 'rally/manage.html')


@csrf_exempt
def team_status_by_date(request):
    date = datetime.datetime.today()
    if request.POST['date'] == 'yesterday':
        date += datetime.timedelta(days=-1)
    team_status_list = TeamStatus.objects.all().filter(date=date)
    result = {}
    if len(team_status_list) == 0 or team_status_list is None:
        result['success'] = False
    else:
        result['success'] = True
        result['team_status'] = [item.as_json() for item in team_status_list]
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def total_status(request):
    date = datetime.datetime.today()
    thumb_up = StatusOption.objects.get(name='Thumb up')
    if request.POST['date'] == 'yesterday':
        date += datetime.timedelta(days=-1)
    team_status_thumb_up = TeamStatus.objects.all().filter(date=date, status=thumb_up)
    team_status_thumb_down = TeamStatus.objects.all().filter(
        date=date).exclude(status=thumb_up)
    result = {}
    if team_status_thumb_up is None or team_status_thumb_down is None:
        result['success'] = False
    else:
        result['success'] = True
        result['thumb_up'] = len(team_status_thumb_up)
        result['thumb_down'] = len(team_status_thumb_down)
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def options(request):
    option_list = StatusOption.objects.all()
    result = {}
    if options is None:
        result['success'] = False
    else:
        result['success'] = True
        result['options'] = [item.as_json() for item in option_list]
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def modified_field(request):
    team_status = TeamStatus.objects.get(pk=request.POST['pk'])
    field = request.POST['field']
    data = request.POST['data']
    if field == 'status':
        status = StatusOption.objects.get(pk=data)
        team_status.status = status
    elif field == 'notes':
        team_status.notes = data
    team_status.save()
    result = dict()
    result['success'] = True
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def statistic_of_days(request):
    start = datetime.datetime.strptime(request.POST['start'], '%Y-%m-%d')
    end = datetime.datetime.strptime(request.POST['end'], '%Y-%m-%d')
    thumb_up = StatusOption.objects.get(name='Thumb up')
    date_span = TeamStatus.objects.values('date').filter(date__gte=start, date__lte=end).annotate(
        dcount=Count('date')).order_by('date')
    statistic = []
    for date in date_span:
        statistic_up = TeamStatus.objects.values('date').filter(status=thumb_up, date=date['date']).annotate(
            dcount=Count('date'))
        statistic_down = TeamStatus.objects.values('date').filter(date=date['date']).exclude(status=thumb_up).annotate(
            dcount=Count('date'))
        row = dict()
        row['date'] = date['date'].isoformat()
        if statistic_up is None or len(statistic_up) == 0:
            row['up'] = 0
        else:
            row['up'] = statistic_up[0]['dcount']
        if statistic_down is None or len(statistic_down) == 0:
            row['down'] = 0
        else:
            row['down'] = statistic_down[0]['dcount']
        statistic.append(row)
    result = dict()
    result['success'] = True
    result['statistic'] = statistic

    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def thumb_down_statistic(request):
    start = datetime.datetime.strptime(request.POST['start'], '%Y-%m-%d')
    end = datetime.datetime.strptime(request.POST['end'], '%Y-%m-%d')
    thumb_up = StatusOption.objects.get(name='Thumb up')
    date_span = TeamStatus.objects.values(
        'date').filter(date__gte=start, date__lte=end).annotate(dcount=Count('date')).order_by('date')
    status_options = StatusOption.objects.all().exclude(name='Thumb up')
    statistic = []
    for date in date_span:
        thumb_down_of_days = TeamStatus.objects.values('status__name', 'date').filter(
            date=date['date']).exclude(status=thumb_up).annotate(dcount=Count('status__name'))
        row = dict()
        row['date'] = date['date'].isoformat()
        for option in status_options:
            row[option.name] = 0
        for item in thumb_down_of_days:
            row[item['status__name']] = item['dcount']
        statistic.append(row)

    result = dict()
    result['success'] = True
    result['thumbdownstatistic'] = statistic
    return HttpResponse(json.dumps(result), content_type='application/json')
