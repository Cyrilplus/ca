#!/usr/bin/env python
from pyral import Rally
from sets import Set
from rally.models import *
import random


def migrate_from_rally():
    apikey = '_y5GuRbLvQKq80xgF7yKQB1YYydNb2EURouvzUAbOXs4'
    # workspace = 'CABU'
    # project = 'DOCSIS-SJ'
    rally = Rally(apikey=apikey)
    workspaces = rally.getWorkspaces()
    rally.setWorkspace('CABU')
    rally.setProject('CRDC L2 CM Provision')
    # for wksp in workspaces:
    #     print "%s %s" % (wksp.oid, wksp.Name)
    #     projects = rally.getProjects(workspace=wksp.Name)
    #     for proj in projects:
    #         print "    %12.12s  %s" % (proj.oid, proj.Name)

    response = rally.get('Task', fetch=True,
                         query="(Owner != null) AND (Iteration != null)")
    users = Set()
    for task in response:
        # print r.FormattedID + "     " + r.Name
        # print "%s  %s  %s" % (task.FormattedID, task.Iteration.Name,
        # task.Owner.Name)
        users.add(task.Owner.Name)

    for username in users:
        user = User()
        user.name = username
        user.save()

    print 'migrate complete'


def create_all_user_status(date=datetime.date.today()):
    users = User.objects.all().order_by('name')
    status_options = StatusOption.objects.all()
    status_num = len(status_options)
    for user in users:
        teamStatus = TeamStatus()
        teamStatus.user = user
        teamStatus.status = status_options[random.randrange(status_num)]
        teamStatus.date = date
        teamStatus.save()

    print 'created complete'


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


def create_history_rows():
    today = datetime.datetime.today()
    for i in xrange(0, 12):
        date = today + datetime.timedelta(days=-i)
        create_all_user_status(date)
    print "created complete"
