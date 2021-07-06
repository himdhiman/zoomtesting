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



class Category(models.Model):
    category_name = models.CharField(max_length=224, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='logo', null=True, blank=True)
    logo_url = models.TextField(blank=True, null=True)
    enable = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    subcategory_name = models.CharField(max_length=224, null=True, blank=True)
    enable = models.BooleanField(default=True)

    def __str__(self):
        return self.subcategory_name


class Course(models.Model):
    title = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    sub_category_name = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    available_date = models.DateTimeField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    appendix = models.TextField(blank=True, null=True)
    course_type = models.CharField(max_length=100, null=True, blank=True)
    course_description = models.TextField(blank=True, null=True)
    learning_goals = models.TextField(blank=True, null=True)
    home_work = models.TextField(blank=True, null=True)
    assginment = models.TextField(blank=True, null=True)
    parental_guidence = models.TextField(blank=True, null=True)
    assesstment = models.TextField(blank=True, null=True)
    sources = models.TextField(blank=True, null=True)
    course_price = models.IntegerField(blank=True, null=True)
    # actual_price = models.IntegerField(blank=True, null=True)
    logo = models.ImageField(upload_to='logo', null=True, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    max_students = models.IntegerField(blank=True, null=True)
    min_students = models.IntegerField(blank=True, null=True)
    min_age = models.IntegerField(blank=True, null=True)
    max_age = models.IntegerField(blank=True, null=True)
    number_of_classes_week = models.IntegerField(blank=True, null=True)
    number_of_week = models.IntegerField(blank=True, null=True)
    total_classes = models.IntegerField(blank=True, null=True)
    time_hour = models.CharField(max_length=100, null=True, blank=True)
    time_minute = models.CharField(max_length=100, null=True, blank=True)
    outside_work = models.CharField(max_length=224, null=True, blank=True)
    material = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    welcome_post = models.TextField(blank=True, null=True)
    course_video = models.FileField(upload_to='course_videos', null=True, blank=True)
    course_video_url = models.TextField(blank=True, null=True)
    course_logo_url = models.TextField(blank=True, null=True)
    approved_by_admin = models.BooleanField(default=False)
    rejected_by_admin = models.BooleanField(default=False)
    language_of_instruction = models.TextField(blank=True, null=True)
    refund = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Batch(models.Model):
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    batch_name = models.CharField(max_length=224, null=True, blank=True)
    batch_description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    number_of_week = models.IntegerField(blank=True, null=True)
    timing = models.TextField(blank=True, null=True)
    online_link = models.TextField(blank=True, null=True)
    host_link = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    room_name = models.CharField(max_length=50, null=True)
    room_expires = models.DateTimeField(null=True)
    room_id = models.TextField(null=True)

    def __str__(self):
        return self.batch_name





class CustomUser(AbstractUser):
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
    course_name = models.ManyToManyField(Course, blank=True)
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
    zoom_user_id = models.TextField(blank=True, null=True, default="NA")

    def __str__(self):
        return self.username