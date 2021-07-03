from datetime import date
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import DurationField

class Licence(models.Model):
    license_no = models.EmailField(null=False, blank=False)
    client_id = models.TextField(null=False, blank=False, default="NA")
    client_secret = models.TextField(null=False, blank=False, default="NA")
    installation_url = models.TextField(null=False, blank=False, default="NA")
    refresh_token = models.TextField(null=False, blank=False, default="NA")
    count = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return self.license_no


class Subject(models.Model):
    name = models.CharField(max_length=50,null=False, blank=False)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField(max_length=50,null=False, blank=False)
    last_name = models.CharField(max_length=50,null=False, blank=False)
    mobile = models.TextField(null=False, blank=False)
    mail = models.EmailField(null=False, blank=False)
    subjects = models.ManyToManyField(Subject)
    zoom_user_id = models.TextField(default="NA", null=False, blank=False)

    def __str__(self):
        return self.first_name + " " +self.last_name + " - " + self.mail


class Batch(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    creation_date = models.DateField(null=False, blank=False, default=date.today)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    duration = models.IntegerField(null=False, blank=False)
    Sunday = models.BooleanField(null=False, blank=False, default=False)
    Sunday_time = models.TimeField(null=True, blank=True)
    Monday = models.BooleanField(null=False, blank=False, default=False)
    Monday_time = models.TimeField(null=True, blank=True)
    Tuesday = models.BooleanField(null=False, blank=False, default=False)
    Tuesday_time = models.TimeField(null=True, blank=True)
    Wednesday = models.BooleanField(null=False, blank=False, default=False)
    Wednesday_time = models.TimeField(null=True, blank=True)
    Thursday = models.BooleanField(null=False, blank=False, default=False)
    Thursday_time = models.TimeField(null=True, blank=True)
    Friday = models.BooleanField(null=False, blank=False, default=False)
    Friday_time = models.TimeField(null=True, blank=True)
    Saturday = models.BooleanField(null=False, blank=False, default=False)
    Saturday_time = models.TimeField(null=True, blank=True)
    start_url = models.TextField(null=False, blank=False, default="NA")
    join_url = models.TextField(null=False, blank=False, default="NA")
    zoom_meeting_id = models.TextField(null=False, blank=False, default="NA")

    def __str__(self):
        return self.subject.name + " - " + self.teacher.first_name + " - " + self.start_date.strftime('%m/%d/%Y') + " to " + self.end_date.strftime('%m/%d/%Y')
