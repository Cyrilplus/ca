from __future__ import unicode_literals

from django.db import models

import datetime

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name

    def as_json(self):
        return {'name': self.name}


class StatusOption(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def as_json(self):
        return {'pk': self.pk, 'name': self.name}


class TeamStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusOption, on_delete=models.CASCADE)
    notes = models.TextField(default='')
    date = models.DateField(default=datetime.date.today)

    def as_json(self):
        return {
            'pk': self.pk,
            'user': self.user.name,
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
