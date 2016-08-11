#!/usr/bin/env python
from pyral import Rally
from rally.models import *
import random

apikey = '_y5GuRbLvQKq80xgF7yKQB1YYydNb2EURouvzUAbOXs4'


def print_workspace_info_from_rally():
    global apikey
    rally = Rally(apikey=apikey)
    workspaces = rally.getWorkspaces()
    for wksp in workspaces:
        print '%s %s' % (wksp.oid, wksp.Name)
    print '-' * 20 + 'end' + '-' * 20


def migrate_team_member_from_rally(workspace='CABU', project='CRDC L2 CM Provision',
                                   iteration_name='CM-Prov-sprint 4-2016'):
    rally = Rally(apikey=apikey)
    rally.setWorkspace(workspace)
    rally.setProject(project)
    proj = rally.getProject(project)
    wksp = rally.getWorkspace()
    if wksp is None:
        print "Rally doesn;t has this workspace: " + workspace
        return
    if proj is None:
        print "Rally doesn't has this project: " + project
        return
    try:
        db_workspace = Workspace.objects.get(oid=str(wksp.oid))
    except Workspace.DoesNotExist:
        print "The database has no record of the workspace: " + wksp.Name
        db_workspace = Workspace(name=wksp.Name, oid=wksp.oid)
        db_workspace.save()
        print "Create a new workspace to database"
    try:
        db_project = Project.objects.get(oid=str(proj.oid), workspace=db_workspace)
        print 'The database has this project: ' + proj.Name + ", so don't need to create new project to database"
    except Project.DoesNotExist:
        print 'The database has no record of this project: ' + proj.Name
        db_project = Project(oid=proj.oid, name=proj.Name, workspace=db_workspace)
        db_project.save()
        print 'Create new project to database'
    query = '(Owner != null) and (Iteration.Name = "' + iteration_name + '")'
    response = rally.get('Task', fetch=True, query=query)
    users = dict()
    for task in response:
        users[task.Owner.Name] = str(task.Owner.oid)
    for key in users.keys():
        try:
            user_record = User.objects.get(oid=users[key])
        except User.DoesNotExist:
            user_record = User(oid=users[key], name=key)
            user_record.save()
        try:
            TeamMember.objects.get(user=user_record, project=db_project)
        except TeamMember.DoesNotExist:
            team_member = TeamMember(user=user_record, project=db_project)
            team_member.save()


def create_daily_record(workspace_name='CABU', project_name='CRDC L2 CM Provision', date=datetime.datetime.today()):
    workspace = Workspace.objects.get(name=workspace_name)
    project = Project.objects.get(name=project_name, workspace=workspace)
    team_members = TeamMember.objects.all().filter(project=project)
    status_options = StatusOption.objects.all()
    status_num = len(status_options)
    for user in team_members:
        team_status = TeamStatus()
        team_status.member = user
        team_status.status = status_options[random.randrange(status_num)]
        team_status.date = date
        team_status.save()
    print 'add new record to database'


def create_test_recodes(workspace_name='CABU', project_name='CRDC L2 CM Provision'):
    today = datetime.datetime.today()
    for i in xrange(-20, 1):
        date = today + datetime.timedelta(days=i)
        create_daily_record(workspace_name, project_name, date)


def create_status_options():
    options = [
        'Thumb up',
        'Architecture unclear',
        'Interface definition unclear',
        'Verification definition unclear',
        'US unclear',
        'US AC unclear',
        'Interrupted by temporary task',
        'Dependency on testbed',
        'Dependency on developer',
        'CFD Support',
        'Bug-Fix (Unrelated to US)',
        'Technical Skillset',
        'Critical Accidental',
        'Dependency on board',
        'Others',
    ]
    for item in options:
        status = StatusOption(name=item);
        status.save()
