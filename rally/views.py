from django.shortcuts import render
from models import *
import datetime
import json
from django.http import HttpResponse
from django.db.models import Count

from django.views.decorators.csrf import csrf_exempt


# Create your views here.


def index(request):
    response = render(request, 'rally/index.html')
    if 'workspace_pk' not in request.COOKIES:
        workspace = Workspace.objects.all()[0]
        project = Project.objects.all().filter(workspace=workspace)[0]
        response.set_cookie('workspace_pk', workspace.pk)
        response.set_cookie('workspace_name', workspace.name)
        response.set_cookie('project_pk', project.pk)
        response.set_cookie('project_name', project.name)
    elif 'project_pk' not in request.COOKIES:
        workspace = Workspace.objects.all().filter(pk=request.COOKIES['workspace_pk'])[0]
        project = Project.objects.all().filter(workspace=workspace)[0]
        response.set_cookie('project_pk', project.pk)
        response.set_cookie('project_name', project.name)
    else:
        workspace = Workspace.objects.all().filter(pk=request.COOKIES['workspace_pk'])[0]
        try:
            Project.objects.all().filter(pk=request.COOKIES['project_pk'], workspace=workspace)[0]
        except Project.DoesNotExist:
            project = Project.objects.all().filter(workspace=workspace)[0]
            response.set_cookie('project_pk', project.pk)
            response.set_cookie('project_name', project.name)
    return response


def manage(request):
    response = render(request, 'rally/team_daily.html')
    if 'workspace_pk' not in request.COOKIES:
        workspace = Workspace.objects.all()[0]
        project = Project.objects.all().filter(workspace=workspace)[0]
        response.set_cookie('workspace_pk', workspace.pk)
        response.set_cookie('workspace_name', workspace.name)
        response.set_cookie('project_pk', project.pk)
        response.set_cookie('project_name', project.name)
    elif 'project_pk' not in request.COOKIES:
        workspace = Workspace.objects.all().filter(pk=request.COOKIES['workspace_pk'])[0]
        project = Project.objects.all().filter(workspace=workspace)[0]
        response.set_cookie('project_pk', project.pk)
        response.set_cookie('project_name', project.name)
    else:
        workspace = Workspace.objects.all().filter(pk=request.COOKIES['workspace_pk'])[0]
        try:
            Project.objects.all().filter(pk=request.COOKIES['project_pk'], workspace=workspace)[0]
        except Project.DoesNotExist:
            project = Project.objects.all().filter(workspace=workspace)[0]
            response.set_cookie('project_pk', project.pk)
            response.set_cookie('project_name', project.name)
    return response


@csrf_exempt
def team_status_by_date(request):
    project_pk = 1
    if 'project_pk' in request.COOKIES:
        project_pk = request.COOKIES['project_pk']
    project = Project.objects.get(pk=project_pk)
    date = datetime.datetime.today()
    if request.POST['date'] == 'yesterday':
        date += datetime.timedelta(days=-1)
    team_status_list = TeamStatus.objects.all().filter(date=date, member__project=project)
    result = dict()
    if len(team_status_list) == 0 or team_status_list is None:
        result['success'] = False
    else:
        result['success'] = True
        result['team_status'] = [item.as_json() for item in team_status_list]
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def total_status(request):
    workspace_pk = request.COOKIES['workspace_pk']
    project_pk = request.COOKIES['project_pk']
    workspace = Workspace.objects.get(pk=workspace_pk)
    project = Project.objects.get(pk=project_pk, workspace=workspace)
    date = datetime.datetime.today()
    thumb_up = StatusOption.objects.get(name='Thumb up')
    if request.POST['date'] == 'yesterday':
        date += datetime.timedelta(days=-1)
    team_status_thumb_up = TeamStatus.objects.all().filter(date=date, status=thumb_up, member__project=project)
    team_status_thumb_down = TeamStatus.objects.all().filter(
        date=date, member__project=project).exclude(status=thumb_up)
    result = dict()
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
    workspace_pk = request.COOKIES['workspace_pk']
    project_pk = request.COOKIES['project_pk']
    workspace = Workspace.objects.get(pk=workspace_pk)
    project = Project.objects.get(pk=project_pk, workspace=workspace)
    team_status = TeamStatus.objects.get(pk=request.POST['pk'], member__project=project)
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
    workspace_pk = request.COOKIES['workspace_pk']
    project_pk = request.COOKIES['project_pk']
    workspace = Workspace.objects.get(pk=workspace_pk)
    project = Project.objects.get(pk=project_pk, workspace=workspace)
    start = datetime.datetime.strptime(request.POST['start'], '%Y-%m-%d')
    end = datetime.datetime.strptime(request.POST['end'], '%Y-%m-%d')
    thumb_up = StatusOption.objects.get(name='Thumb up')
    date_span = TeamStatus.objects.values('date').filter(date__gte=start, date__lte=end,
                                                         member__project=project).annotate(
        dcount=Count('date')).order_by('date')
    statistic = []
    for date in date_span:
        statistic_up = TeamStatus.objects.values('date').filter(status=thumb_up, date=date['date'],
                                                                member__project=project).annotate(
            dcount=Count('date'))
        statistic_down = TeamStatus.objects.values('date').filter(date=date['date'], member__project=project).exclude(
            status=thumb_up).annotate(
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
    workspace_pk = request.COOKIES['workspace_pk']
    project_pk = request.COOKIES['project_pk']
    workspace = Workspace.objects.get(pk=workspace_pk)
    project = Project.objects.get(pk=project_pk, workspace=workspace)
    start = datetime.datetime.strptime(request.POST['start'], '%Y-%m-%d')
    end = datetime.datetime.strptime(request.POST['end'], '%Y-%m-%d')
    thumb_up = StatusOption.objects.get(name='Thumb up')
    date_span = TeamStatus.objects.values(
        'date').filter(date__gte=start, date__lte=end, member__project=project).annotate(dcount=Count('date')).order_by(
        'date')
    status_options = StatusOption.objects.all().exclude(name='Thumb up')
    statistic = []
    for date in date_span:
        thumb_down_of_days = TeamStatus.objects.values('status__name', 'date').filter(
            date=date['date'], member__project=project).exclude(status=thumb_up).annotate(dcount=Count('status__name'))
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


@csrf_exempt
def workspaces_info(request):
    workspaces = Workspace.objects.all()
    result = dict()
    if len(workspaces) == 0 or workspaces is None:
        result['success'] = False
    else:
        result['success'] = True
        result['workspaces'] = [item.as_json() for item in workspaces]
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def projects_by_workspace(request):
    workspace = Workspace.objects.get(pk=request.COOKIES['workspace_pk'])
    projects = Project.objects.all().filter(workspace=workspace)
    result = dict()
    if len(projects) == 0 or projects is None:
        result['success'] = False
    else:
        result['success'] = True
        result['projects'] = [item.as_json() for item in projects]
    return HttpResponse(json.dumps(result), content_type='application/json')
