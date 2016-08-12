from rally.models import *

import time
import thread


def create_new_records():

    thumb_up = StatusOption.objects.get(name='Thumb up')
    members = TeamMember.objects.all()
    for member in members:
        team_status = TeamStatus(member=member, status=thumb_up)
        team_status.save()


def run():
    to_team_status = TeamStatus.objects.all().filter(date=datetime.datetime.today())
    if len(to_team_status) == 0 or to_team_status is None:
        create_new_records()
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    tomorrow_at_zero = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day)
    sleep_time = tomorrow_at_zero - datetime.datetime.today()
    time.sleep(sleep_time.total_seconds())
    while True:
        create_new_records()
        time.sleep(60 * 60 * 24)


def auto_create_new_records_everyday():
    thread.start_new_thread(run, ())
