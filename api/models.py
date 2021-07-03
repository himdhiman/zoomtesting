from datetime import date
from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import AbstractUser 





class Licence(models.Model):
    license_no = models.EmailField(null=False, blank=False)
    client_id = models.TextField(null=False, blank=False, default="NA")
    client_secret = models.TextField(null=False, blank=False, default="NA")
    installation_url = models.TextField(null=False, blank=False, default="NA")
    refresh_token = models.TextField(null=False, blank=False, default="NA")
    count = models.IntegerField(null=False, blank=False, default=0)

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




class User(AbstractUser):
    public_name = models.CharField(max_length=100, null=True, blank=True)
    user_type = models.CharField(max_length=100, null=True, blank=True)
    phone_no = models.CharField(max_length=100, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    head_line = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    academics = models.TextField(blank=True, null=True)
    teaching_interests = models.TextField(blank=True, null=True)
    # course_name = models.ManyToManyField(Course, blank=True)
    batch = models.ManyToManyField(Batch, blank=True)
    facebook_id = models.CharField(max_length=100, blank=True, null=True)
    gmail_id = models.CharField(max_length=100, blank=True, null=True)
    profile_pic = models.ImageField(
        upload_to='profile_pic/', null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    facebook_pic = models.TextField(blank=True, null=True)
    gmail_pic = models.TextField(blank=True, null=True)
    input_text = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes', null=True, blank=True)
    teacher_intro = models.FileField(upload_to='intro_videos', null=True, blank=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    hobbies = models.TextField(blank=True, null=True)
    facebook_link = models.TextField(blank=True, null=True)
    instagram_link = models.TextField(blank=True, null=True)
    youtube_link = models.TextField(blank=True, null=True)
    linkedin_link = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=False)
    accepted_by_admin = models.BooleanField(default=False)
    video_url = models.TextField(blank=True, null=True)
    profile_pic_url = models.TextField(blank=True, null=True)
    application_status = models.BooleanField(default=False)
    number_verify_status = models.BooleanField(default=False)
    rejected_by_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username