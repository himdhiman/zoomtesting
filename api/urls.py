from django.urls import path
from api import views

urlpatterns = [
    path("", views.home, name='home'),
    path("addlicence/", views.add_licence, name='addlicence'),
    path("createteacher/", views.create_teacher, name='createteacher'),
    path("addsubject/", views.add_subject, name='addsubject'),
    path("createsubject/", views.create_subject, name='createsubject'),
    path("createbatch/", views.create_batch, name='createbatch'),
    path("getbatch/", views.get_batch, name='getbatch'),
    path("callback/", views.zoom_callback),
    path("startmeet/<int:id>/", views.start_meeting, name="startmeet"),
    path("temp_zoom/", views.created_licence)
]