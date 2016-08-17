from django.shortcuts import render
import json
from django.http import HttpResponse
from django.db.models import Count

from django.views.decorators.csrf import csrf_exempt
from pyral import Rally
from rally.models import *
from pyral import RallyRESTAPIError
import migrate

apikey = '_y5GuRbLvQKq80xgF7yKQB1YYydNb2EURouvzUAbOXs4'


# Create your views here.

def set_cookies(request, response):
    if 'workspace_pk' not in request.COOKIES:
        workspaces = Workspace.objects.all()
        if len(workspaces) == 0:
            response.set_cookie('workspace_pk', 0)
            return
        workspace = workspaces[0]
        projects = Project.objects.all().filter(workspace=workspace)
        if len(projects) == 0:
            response.set_cookie('project_px', 0)
            return
        project = projects[0]
        response.set_cookie('workspace_pk', workspace.pk)
        response.set_cookie('workspace_name', workspace.name)
        response.set_cookie('project_pk', project.pk)
        response.set_cookie('project_name', project.name)
    elif 'project_pk' not in request.COOKIES:
        workspaces = Workspace.objects.all().filter(pk=request.COOKIES['workspace_pk'])
        if len(workspaces) == 0:
            response.set_cookie('workspace_pk', 0)
            return
        workspace = workspaces[0]
        projects = Project.objects.all().filter(workspace=workspace)
        if len(projects) == 0:
            response.set_cookie('project_pk', 0)
            return
        project = projects[0]
        response.set_cookie('project_pk', project.pk)
        response.set_cookie('project_name', project.name)
    else:
        workspaces = Workspace.objects.all().filter(pk=request.COOKIES['workspace_pk'])
        if len(workspaces) == 0:
            response.set_cookie('workspace_pk', 0)
            return
        workspace = workspaces[0]
        try:
            Project.objects.all().filter(pk=request.COOKIES['project_pk'], workspace=workspace)[0]
        except Project.IndexError:
            projects = Project.objects.all().filter(workspace=workspace)
            if len(projects) == 0:
                response.set_cookie('project_pk', 0)
                return
            project = projects[0]
            response.set_cookie('project_pk', project.pk)
            response.set_cookie('project_name', project.name)


def index(request):
    response = render(request, 'rally/index.html')
    set_cookies(request, response)
    return response


def team_daily(request):
    response = render(request, 'rally/team-daily.html')
    set_cookies(request, response)
    return response


def project_manage(request):
    return render(request, 'rally/project-manage.html')


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


@csrf_exempt
def all_projects(request):
    projects = Project.objects.all().order_by('workspace__name')
    result = dict()
    if len(projects) == 0 or projects is None:
        result['success'] = False
    else:
        json_projects = []
        for project in projects:
            members = TeamMember.objects.all().filter(project=project)
            proj = project.as_json()
            proj['member-size'] = len(members)
            json_projects.append(proj)
        result['success'] = True
        result['projects'] = json_projects
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def workspace_projects_statistic(request):
    workspaces = Project.objects.values('workspace__name').annotate(count=Count('workspace__name'))
    statistic = []
    for item in workspaces:
        row = dict()
        row['count'] = item['count']
        row['workspace'] = item['workspace__name']
        statistic.append(row)
    result = dict()
    result['success'] = True
    result['statistic'] = statistic
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def get_workspaces_from_rally(request):
    result = dict()
    try:
        global apikey
        rally = Rally(apikey=apikey)
        rally_workspaces = rally.getWorkspaces()
        workspaces = []
        for wksp in rally_workspaces:
            item = dict()
            item['name'] = wksp.Name
            item['oid'] = wksp.oid
            workspaces.append(item)
        result['success'] = True
        result['workspaces'] = workspaces
    except RallyRESTAPIError:
        result['success'] = False
        result['message'] = "Can't access rally server"

    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def get_projects_by_workspace_from_rally(request):
    result = dict()
    workspace = request.POST.get('workspace', 'CABU')
    try:
        global apikey
        rally = Rally(apikey=apikey)
        rally.setWorkspace(workspace)
        rally_projects = rally.getProjects(workspace)
        projects = []
        for project in rally_projects:
            item = {
                'name': project.Name,
                'oid': project.oid
            }
            projects.append(item)
        result['success'] = True
        result['projects'] = projects
        result['workspace'] = workspace
    except RallyRESTAPIError:
        result['success'] = False
        result['message'] = "Can't access rally server"

    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def get_iterations_by_project_workspace(request):
    workspace = request.POST.get('workspace', 'CABU')
    project = request.POST.get('project', 'DOCSIS-SJ')
    result = dict()
    try:
        global apikey
        rally = Rally(apikey=apikey)
        rally.setWorkspace(workspace)
        rally.setProject(project)
        query = '(Owner != null) and (Iteration.Name != null )'
        takes = rally.get('Task', fetch=True, query=query)
        iteration_set = set()
        for task in takes:
            iteration_set.add(task.Iteration.Name)
        iterations = []
        for iteration in iteration_set:
            iterations.append(iteration)
        result['success'] = True
        result['iterations'] = iterations
    except RallyRESTAPIError:
        result['success'] = False
        result['message'] = "Can't access rally server"
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def add_project_from_rally(request):
    workspace = request.POST.get('workspace', 'CABU')
    project = request.POST.get('project', 'DOCSIS-SJ')
    iteration = request.POST.get('iteration', '')
    result = dict()
    if migrate.migrate_team_member_from_rally(workspace=workspace, project=project, iteration_name=iteration):
        result['success'] = True
    else:
        result['success'] = False
    return HttpResponse(json.dumps(result), content_type='application/json')
