"""ca URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from rally import views as rally_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^rally/projects-by-workspace', rally_views.projects_by_workspace),
    url(r'^rally/workspaces', rally_views.workspaces_info),
    url(r'^rally/thumbdownstatistic', rally_views.thumb_down_statistic),
    url(r'^rally/statisticofdays', rally_views.statistic_of_days),
    url(r'^rally/teamstatus', rally_views.team_status_by_date),
    url(r'^rally/modifiedfield', rally_views.modified_field),
    url(r'^rally/options', rally_views.options),
    url(r'^rally/totalstatus', rally_views.total_status),
    url(r'^rally/project-manage', rally_views.project_manage, name='project-manage'),
    url(r'^rally/team_daily', rally_views.team_daily, name='team_daily'),
    url(r'^rally/', rally_views.index),
    url(r'^$', rally_views.index, name='home'),
]
