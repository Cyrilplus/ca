from __future__ import unicode_literals

from django.db import models

import datetime


# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=70)
    oid = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def as_json(self):
        return {'name': self.name, 'oid': self.oid}


class StatusOption(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def as_json(self):
        return {'pk': self.pk, 'name': self.name}


class Workspace(models.Model):
    name = models.CharField(max_length=100)
    oid = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def as_json(self):
        return {
            'name': self.name,
            'oid': self.oid,
            'pk': self.pk
        }


class Project(models.Model):
    name = models.CharField(max_length=100)
    oid = models.CharField(max_length=50)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def as_json(self):
        return {
            'name': self.name,
            'oid': self.oid,
            'pk': self.pk
        }


class TeamMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + ' in ' + self.project.name

    def as_json(self):
        return {
            'project': self.project.name,
            'user': self.user.name
        }


class TeamStatus(models.Model):
    status = models.ForeignKey(StatusOption, on_delete=models.CASCADE)
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    notes = models.TextField(default='')
    date = models.DateField(default=datetime.date.today)

    def as_json(self):
        return {
            'pk': self.pk,
            'project': self.member.project.name,
            'user': self.member.user.name,
            'status': self.status.name,
            'notes': self.notes,
            'date': self.date.isoformat()
        }


class DownComment(models.Model):
    status = models.ForeignKey(StatusOption, on_delete=models.CASCADE)
    content = models.TextField()

    def as_json(self):
        return {
            'status': self.status.name,
            'content': self.content
        }
