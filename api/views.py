from django.db.models.base import Model
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
import requests
import base64
import json
from api import models
from django.views.decorators.csrf import csrf_exempt 

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def home(request):
    return render(request, "home.html")

def encode_base64(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


@csrf_exempt
def add_licence(request):
    if(request.method == "POST"):
        mail = request.POST['licnce_no']
        clientid = request.POST['clientid']
        clientsecret = request.POST['clientsecret']
        installationurl = request.POST['installationurl']
        l_obj = models.Licence(
            license_no=mail,
            client_id=clientid,
            client_secret=clientsecret,
            installation_url=installationurl
        )
        l_obj.save()
        print(l_obj.id)
        return HttpResponseRedirect(installationurl + "&state=" + str(l_obj.id))
    return render(request, "addlicence.html")


def zoom_callback(request):
    code = request.GET["code"]
    l_id = request.GET["state"]
    print(l_id)
    post_url = f"https://zoom.us/oauth/token?grant_type=authorization_code&code={code}&redirect_uri=https://testserverzoom.herokuapp.com/callback/"
    l_obj = models.Licence.objects.get(id=l_id)
    data = requests.post(post_url, headers={
        "Authorization" : "Basic" + encode_base64(l_obj.client_id + ":" + l_obj.client_secret)
    })
    print(data.json())
    setattr(l_obj, "refresh_token", data.json()["refresh_token"])
    l_obj.save()
    return HttpResponseRedirect("/temp_zoom/")

def get_access_token(l_id):
    l_obj = models.Licence.objects.get(id=l_id)
    post_url = f"https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token={l_obj.refresh_token}"
    data = requests.post(post_url, headers={
        "Authorization" : "Basic" + encode_base64(l_obj.client_id + ":" + l_obj.client_secret)
    })
    setattr(l_obj, "refresh_token", data.json()["refresh_token"])
    l_obj.save()
    return data.json()["access_token"]

def created_licence(request):
    return render(request, "createdlicence.html")


@csrf_exempt
def create_teacher(request):
    if(request.method == "POST"):
        teacher_obj = models.Teacher(
            first_name=request.POST["teachernamefirst"], 
            last_name=request.POST["teachernamelast"],
            mobile=request.POST["phoneno"], 
            mail=request.POST["mailid"]
        )
        teacher_obj.save()
        teacher_obj.subjects.add(models.Subject.objects.get(name=request.POST["subjects"]))
        teacher_obj.save()
        l_obj = models.Licence.objects.all()[0]
        access_token = get_access_token(l_obj.id)
        payload = {
        "action": "custCreate",
        "user_info": {
            "email": request.POST["mailid"],
            "type": 1,
            "first_name": request.POST["teachernamefirst"],
            "last_name": request.POST["teachernamelast"]
            }
        }
        data = requests.post("https://api.zoom.us/v2/users", headers = {
            'content-type' : 'application/json',
            "Authorization": f"Bearer {access_token}"
        }, data=json.dumps(payload))
        print(data.json())
        setattr(teacher_obj, "zoom_user_id", data.json()["id"])
        teacher_obj.save()
    qs_subject = models.Subject.objects.all()
    return render(request, "createteacher.html", {"qs_subject" : qs_subject})

@csrf_exempt
def create_subject(request):
    if(request.method == "POST"):
        sub_obj = models.Subject(name = request.POST["subjectname"])
        sub_obj.save()
    return render(request, "addsubject.html")

@csrf_exempt
def add_subject(request):
    # return HttpResponseRedirect("http://localhost:8000/createsubject/")
    return HttpResponseRedirect("https://testserverzoom.herokuapp.com/createsubject/")


@csrf_exempt
def create_batch(request):
    prefix = "startTime"
    if(request.method == "POST"):
        print(request.POST)
        teacher_obj = models.Teacher.objects.get(mail=request.POST["Teacher"])
        subject_obj = teacher_obj.subjects.all()
        bat_obj = models.Batch(
            teacher=teacher_obj, subject = subject_obj[0],
            start_date = request.POST["startdate"], 
            end_date = request.POST["enddate"],
            duration = request.POST["duration"]
        )
        bat_obj.save()
        for i in days:
            if i in request.POST:
                setattr(bat_obj, i, True)
                temp = i+"_time"
                setattr(bat_obj, temp, request.POST[prefix+i])
        bat_obj.save()
        l_obj = models.Licence.objects.all()[0]
        access_token = get_access_token(l_obj.id)
        payload = {
            "topic": bat_obj.subject.name,
            "type": 3,
        }
        user_id = teacher_obj.zoom_user_id
        data = requests.post(f"https://api.zoom.us/v2/users/{user_id}/meetings", headers = {
            'content-type' : 'application/json',
            "Authorization": f"Bearer {access_token}"
        }, data=json.dumps(payload))
        setattr(bat_obj, "start_url", data.json()["start_url"])
        setattr(bat_obj, "join_url", data.json()["join_url"])
        setattr(bat_obj, "zoom_meeting_id", data.json()["id"])
        bat_obj.save()

        print(data.json())
    qs_teacher = models.Teacher.objects.all()
    return render(request, "createbatch.html", {"qs_teacher":qs_teacher})

def get_batch(request):
    qs = models.Batch.objects.all()
    return render(request, "getbatch.html", {"qs" : qs})

@csrf_exempt
def start_meeting(request, id):
    batch_obj = models.Batch.objects.get(id=id)
    teacher_obj = models.Teacher.objects.get(id=batch_obj.teacher.id)
    payload = {
        "type": 2
    }
    user_id = teacher_obj.zoom_user_id
    l_obj = models.Licence.objects.all()[0]
    access_token = get_access_token(l_obj.id)
    data = requests.patch(f"https://api.zoom.us/v2/users/{user_id}", headers = {
            'content-type' : 'application/json',
            "Authorization": f"Bearer {access_token}"
        }, data=json.dumps(payload))
    return HttpResponseRedirect(batch_obj.start_url)

@csrf_exempt
def end_meeting(request):
    if(request.method == "POST"):
        print("Hello Himanshu")
        print(request.headers)
        print(request.POST)
        return HttpResponse(status=200)
    return


# def modify_time(time):
#     time = time.split(":")
#     time = time[0] + time[1]
#     return int(time)

# def next_date(date):
#     date = date.split("-")
#     x = datetime.datetime(int(date[0]), int(date[1]), int(date[2])) + datetime.timedelta(days=1)
#     year = str(x.year)
#     month = str(x.month)
#     day = str(x.day)
#     if len(month) == 1:
#         month = "0" + month
#     if len(day) == 1:
#         day = "0" + day
#     return year + "-" + month + "-" + day


# def helper_view(data_date, start_time, end_time):
#     start_time_int = modify_time(start_time)
#     end_time_int = modify_time(end_time)
#     licences = set()
#     if(start_time_int > end_time_int):
#         curr_day = data_date
#         next_day = next_date(data_date)
#         start1 = start_time_int
#         end1 = 2359
#         start2 = 0
#         end2 = end_time_int
#         qs1 = []
#         qs2 = []
#         try:
#             qs1 = models.Date.objects.get(date_encoded=curr_day).meetings.all()
#         except:
#             pass

#         try:
#             qs2 = models.Date.objects.get(date_encoded=next_day).meetings.all()
#         except:
#             pass

#         for x in qs1:
#             t1 = modify_time(x.start_time.strftime("%H:%M"))
#             t2 = modify_time(x.end_time.strftime("%H:%M"))
#             if((start1 >= t1 and start1 <= t2) or (end1 >= t1 and end1 <= t2)):
#                 licences.add(x.licence.license_no)

#         for x in qs2:
#             t1 = modify_time(x.start_time.strftime("%H:%M"))
#             t2 = modify_time(x.end_time.strftime("%H:%M"))
#             if((start2 >= t1 and start2 <= t2) or (end2 >= t1 and end2 <= t2)):
#                 licences.add(x.licence.license_no)

#     else:
#         qs = []
#         try:
#             qs = models.Date.objects.get(date_encoded=data_date).meetings.all()
#         except:
#             pass
#         for x in qs:
#             t1 = modify_time(x.start_time.strftime("%H:%M"))
#             t2 = modify_time(x.end_time.strftime("%H:%M"))
#             if((start_time_int >= t1 and start_time_int <= t2) or (end_time_int >= t1 and end_time_int <= t2)):
#                 print(t1, start_time_int, t2, end_time_int)
#                 licences.add(x.licence.license_no)

#     print(licences)

#     licences_all = models.Licence.objects.all()
#     for x in licences_all:
#         if x.license_no not in licences:
#             return x.license_no

#     return ""


# @csrf_exempt
# def index(request):
#     if(request.method == "POST"):
#         scheduling_licence = helper_view(request.POST["classDate"], request.POST["startTime"], request.POST["endTime"])
#         if(scheduling_licence == ""):
#             print("No Licence Available")
#         else:
#             print(scheduling_licence)
#             start_time_int = modify_time(request.POST["startTime"])
#             end_time_int = modify_time(request.POST["endTime"])
#             class_date = request.POST["classDate"].split("-")
#             m_id = ""
#             if(start_time_int > end_time_int):
#                 meeting_object1 = models.Meeting(
#                     meeting_date = request.POST["classDate"],
#                     start_time = request.POST["startTime"],
#                     end_time = "23:59",
#                     cancelled = False,
#                     start_url = "NA",
#                     join_url = "NA",
#                     subject = models.Subject.objects.get(name=request.POST["subjects"]),
#                     teacher = models.Teacher.objects.get(name=request.POST["teachers"]),
#                     licence = models.Licence.objects.get(license_no=scheduling_licence)
#                 )
#                 meeting_object1.save()
#                 meeting_object2 = models.Meeting(
#                     meeting_date = request.POST["classDate"],
#                     start_time = "00:01",
#                     end_time = request.POST["endTime"],
#                     cancelled = False,
#                     start_url = "NA",
#                     join_url = "NA",
#                     subject = models.Subject.objects.get(name=request.POST["subjects"]),
#                     teacher = models.Teacher.objects.get(name=request.POST["teachers"]),
#                     licence = models.Licence.objects.get(license_no=scheduling_licence)
#                 )
#                 meeting_object2.save()
#                 m_id = str(meeting_object1.id) + "+" + str(meeting_object2.id)
#                 qs1 = []
#                 qs2 = []
#                 try:
#                     qs1 = models.Date.objects.filter(date_encoded=request.POST["classDate"])
#                 except:
#                     pass

#                 try:
#                     qs2 = models.Date.objects.filter(date_encoded=next_date(request.POST["classDate"]))
#                 except:
#                     pass

#                 if(len(qs1) == 0):
#                     date_object1 = models.Date(
#                         date_encoded=datetime.date(int(class_date[0]), int(class_date[1]), int(class_date[2]))
#                     )
#                     date_object1.save()
#                     date_object1.meetings.add(meeting_object1)
#                 else:
#                     date_object1 = qs1[0]
#                     date_object1.meetings.add(meeting_object1)

#                 if(len(qs2) == 0):
#                     date_object2 = models.Date(
#                         date_encoded=datetime.date(int(class_date[0]), int(class_date[1]), int(class_date[2])) + datetime.timedelta(days=1)
#                     )
#                     date_object2.save()
#                     date_object2.meetings.add(meeting_object2)
#                 else:
#                     date_object2 = qs2[0]
#                     date_object2.meetings.add(meeting_object2)
#             else:
#                 qs = models.Date.objects.filter(date_encoded=request.POST["classDate"])
#                 meeting_object = models.Meeting(
#                     meeting_date = request.POST["classDate"],
#                     start_time = request.POST["startTime"],
#                     end_time = request.POST["endTime"],
#                     cancelled = False,
#                     start_url = "NA",
#                     join_url = "NA",
#                     subject = models.Subject.objects.get(name=request.POST["subjects"]),
#                     teacher = models.Teacher.objects.get(name=request.POST["teachers"]),
#                     licence = models.Licence.objects.get(license_no=scheduling_licence)
#                 )
#                 meeting_object.save()
#                 m_id = str(meeting_object.id)
#                 if len(qs) == 0:
#                     date_object = models.Date(
#                         date_encoded=datetime.date(int(class_date[0]), int(class_date[1]), int(class_date[2])),
#                     )
#                     date_object.save()
#                     date_object.meetings.add(meeting_object)
#                 else:
#                     date_object = qs[0]
#                     date_object.meetings.add(meeting_object)
#             obj = models.Licence.objects.get(license_no = scheduling_licence)
#             if(obj.access_token == "NA"):
#                 return redirect(obj.installation_url + "&state=" + m_id)
#             else:
#                 zoom_helper(m_id)
#                 return HttpResponseRedirect("/temp_zoom/")

#     qs_teacher = models.Teacher.objects.all()
#     qs_subject = models.Subject.objects.all()
#     return render(request, "index.html", {"qs_teacher": qs_teacher, "qs_subject" : qs_subject})


# def zoom_helper(m_id):
#     meeting_id = [int(x) for x in m_id.split(" ")]
#     if(len(meeting_id) == 1):
#         meeting_object = models.Meeting.objects.get(id=meeting_id[0])
#         start_time_int = modify_time(meeting_object.start_time.strftime("%H:%M"))
#         end_time_int = modify_time(meeting_object.end_time.strftime("%H:%M"))
#         meeting_date = meeting_object.meeting_date
#     else:
#         meeting_object1 = models.Meeting.objects.get(id=meeting_id[0])
#         meeting_object2 = models.Meeting.objects.get(id=meeting_id[1])
#         start_time_int = modify_time(meeting_object1.start_time.strftime("%H:%M"))
#         end_time_int = modify_time(meeting_object2.end_time.strftime("%H:%M"))
#         meeting_date = meeting_object1.meeting_date

#     meeting_year = str(meeting_date.year)
#     meeting_month = str(meeting_date.month)
#     meeting_day = str(meeting_date.day)
#     if len(meeting_day) == 1:
#         meeting_day = "0" + meeting_day
#     if len(meeting_month) == 1:
#         meeting_month = "0" + meeting_month
    
    
#     meeting_date = [meeting_year, meeting_month, meeting_day]
#     if(len(meeting_id) == 1):
#         start_time = meeting_object.start_time.strftime("%H:%M")
#         start_time = start_time.split(":")
#         end_time = meeting_object.end_time.strftime("%H:%M")
#         end_time = end_time.split(":")
#     else:
#         start_time = meeting_object1.start_time.strftime("%H:%M")
#         start_time = start_time.split(":")
#         end_time = meeting_object2.end_time.strftime("%H:%M")
#         end_time = end_time.split(":")

#     if(start_time_int > end_time_int):
#         next_day = next_date(meeting_year + "-" + meeting_month + "-" + meeting_day)
#         next_day = next_day.split("-")
#         date_time_object_start = datetime.datetime(int(meeting_date[0]), int(meeting_date[1]), int(meeting_date[2]), int(start_time[0]), int(start_time[1]))
#         date_time_object_end = datetime.datetime(int(next_day[0]), int(next_day[1]), int(next_day[2]), int(end_time[0]), int(end_time[1]))
#         duration = date_time_object_end-date_time_object_start
#     else:
#         date_time_object_start = datetime.datetime(int(meeting_date[0]), int(meeting_date[1]), int(meeting_date[2]), int(start_time[0]), int(start_time[1]))
#         date_time_object_end = datetime.datetime(int(meeting_date[0]), int(meeting_date[1]), int(meeting_date[2]), int(end_time[0]), int(end_time[1]))
#         duration = date_time_object_end-date_time_object_start

#     seconds = duration.total_seconds()
#     hours = seconds // 3600
#     minutes = (seconds % 3600) // 60
#     payload = {
#         "topic" : meeting_object.subject.name if len(meeting_id) == 1 else meeting_object1.subject.name,
#         "type" : 2,
#         "start_time" : str(meeting_object.meeting_date)+"T"+str(meeting_object.start_time) if len(meeting_id) == 1 else str(meeting_object1.meeting_date)+"T"+str(meeting_object1.start_time),
#         "duration" : (hours)*60 + minutes,
#     }
#     access_token = meeting_object.licence.access_token if len(meeting_id) == 1 else meeting_object1.licence.access_token
#     data = requests.post("https://api.zoom.us/v2/users/me/meetings", headers = {
#         'content-type' : 'application/json',
#         "Authorization": f"Bearer {access_token}"
#     }, data=json.dumps(payload))
#     print(data.json())
#     if(len(meeting_id) == 1):
#         meeting_object.start_url = data.json()["start_url"]
#         meeting_object.join_url = data.json()["join_url"]
#         meeting_object.save()
#     else:
#         meeting_object1.start_url = data.json()["start_url"]
#         meeting_object1.join_url = data.json()["join_url"]
#         meeting_object2.start_url = data.json()["start_url"]
#         meeting_object2.join_url = data.json()["join_url"]
#         meeting_object1.save()
#         meeting_object2.save()

#     print(data.json()["join_url"], data.json()["start_url"])

#     return

# def zoom_callback(request):
#     code = request.GET["code"]
#     meeting_id = request.GET["state"]
#     meeting_id = [int(x) for x in meeting_id.split(" ")]
#     post_url = f"https://zoom.us/oauth/token?grant_type=authorization_code&code={code}&redirect_uri=http://127.0.0.1:8000/callback/"
#     if(len(meeting_id) == 1):
#         meeting_object = models.Meeting.objects.get(id=meeting_id[0])
#         start_time_int = modify_time(meeting_object.start_time.strftime("%H:%M"))
#         end_time_int = modify_time(meeting_object.end_time.strftime("%H:%M"))
#         meeting_date = meeting_object.meeting_date
#     else:
#         meeting_object1 = models.Meeting.objects.get(id=meeting_id[0])
#         meeting_object2 = models.Meeting.objects.get(id=meeting_id[1])
#         start_time_int = modify_time(meeting_object1.start_time.strftime("%H:%M"))
#         end_time_int = modify_time(meeting_object2.end_time.strftime("%H:%M"))
#         meeting_date = meeting_object1.meeting_date

#     meeting_year = str(meeting_date.year)
#     meeting_month = str(meeting_date.month)
#     meeting_day = str(meeting_date.day)
#     if len(meeting_day) == 1:
#         meeting_day = "0" + meeting_day
#     if len(meeting_month) == 1:
#         meeting_month = "0" + meeting_month
    
    
#     meeting_date = [meeting_year, meeting_month, meeting_day]
#     if(len(meeting_id) == 1):
#         l_obj = models.Licence.objects.get(id = meeting_object.licence.id)
#         data = requests.post(post_url, headers={
#             "Authorization" : "Basic" + encode_base64(l_obj.client_id + ":" + l_obj.client_secret)
#         })
#         start_time = meeting_object.start_time.strftime("%H:%M")
#         start_time = start_time.split(":")
#         end_time = meeting_object.end_time.strftime("%H:%M")
#         end_time = end_time.split(":")
#     else:
#         l_obj = models.Licence.objects.get(id = meeting_object1.licence.id)
#         data = requests.post(post_url, headers={
#             "Authorization" : "Basic" + encode_base64(l_obj.client_id + ":" + l_obj.client_secret)
#         })
#         start_time = meeting_object1.start_time.strftime("%H:%M")
#         start_time = start_time.split(":")
#         end_time = meeting_object2.end_time.strftime("%H:%M")
#         end_time = end_time.split(":")

#     if(start_time_int > end_time_int):
#         next_day = next_date(meeting_year + "-" + meeting_month + "-" + meeting_day)
#         next_day = next_day.split("-")
#         date_time_object_start = datetime.datetime(int(meeting_date[0]), int(meeting_date[1]), int(meeting_date[2]), int(start_time[0]), int(start_time[1]))
#         date_time_object_end = datetime.datetime(int(next_day[0]), int(next_day[1]), int(next_day[2]), int(end_time[0]), int(end_time[1]))
#         duration = date_time_object_end-date_time_object_start
#     else:
#         date_time_object_start = datetime.datetime(int(meeting_date[0]), int(meeting_date[1]), int(meeting_date[2]), int(start_time[0]), int(start_time[1]))
#         date_time_object_end = datetime.datetime(int(meeting_date[0]), int(meeting_date[1]), int(meeting_date[2]), int(end_time[0]), int(end_time[1]))
#         duration = date_time_object_end-date_time_object_start

#     seconds = duration.total_seconds()
#     hours = seconds // 3600
#     minutes = (seconds % 3600) // 60
#     request.session["zoom_access_token"] = data.json()["access_token"]
#     print(data.json()["access_token"])
#     payload = {
#         "topic" : meeting_object.subject.name if len(meeting_id) == 1 else meeting_object1.subject.name,
#         "type" : 2,
#         "start_time" : str(meeting_object.meeting_date)+"T"+str(meeting_object.start_time) if len(meeting_id) == 1 else str(meeting_object1.meeting_date)+"T"+str(meeting_object1.start_time),
#         "duration" : (hours)*60 + minutes,
#     }
#     data = requests.post("https://api.zoom.us/v2/users/me/meetings", headers = {
#         'content-type' : 'application/json',
#         "Authorization": f"Bearer {request.session['zoom_access_token']}"
#     }, data=json.dumps(payload))
#     print(data.json())
#     if(len(meeting_id) == 1):
#         meeting_object.start_url = data.json()["start_url"]
#         meeting_object.join_url = data.json()["join_url"]
#         meeting_object.save()
#         l_obj = models.Licence.objects.get(id = meeting_object.licence.id)
#         l_obj.access_token = request.session['zoom_access_token']
#         l_obj.save()
#     else:
#         meeting_object1.start_url = data.json()["start_url"]
#         meeting_object1.join_url = data.json()["join_url"]
#         meeting_object2.start_url = data.json()["start_url"]
#         meeting_object2.join_url = data.json()["join_url"]
#         meeting_object1.save()
#         meeting_object2.save()
#         l_obj = models.Licence.objects.get(id = meeting_object1.licence.id)
#         l_obj.access_token = request.session['zoom_access_token']
#         l_obj.save()

#     print(data.json()["join_url"], data.json()["start_url"])

#     return HttpResponseRedirect("/temp_zoom/")