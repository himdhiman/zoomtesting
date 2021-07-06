from django.db.models.base import Model
from django.http.response import HttpResponseRedirect, HttpResponse, JsonResponse
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
    if l_obj.count > 0:
        l_obj.count -= 1
        l_obj.save()
        access_token = get_access_token(l_obj.id)
        data = requests.patch(f"https://api.zoom.us/v2/users/{user_id}", headers = {
                'content-type' : 'application/json',
                "Authorization": f"Bearer {access_token}"
            }, data=json.dumps(payload))
        return HttpResponseRedirect(batch_obj.start_url)

    else:
        return JsonResponse({"error" : "Insufficient Licence"})


@csrf_exempt
def end_meeting(request):
    if(request.method == "POST"):
        print(request.body)
        data = request.body
        data = data.decode("utf-8")
        data = json.loads(data)
        print(data)
        m_id = data["payload"]["object"]["id"]
        m_obj = models.Batch.objects.get(zoom_meeting_id=m_id)
        u_id = m_obj.teacher.zoom_user_id
        payload = {
            "type": 1
        }
        l_obj = models.Licence.objects.all()[0]
        l_obj.count += 1
        l_obj.save()
        access_token = get_access_token(l_obj.id)
        data = requests.patch(f"https://api.zoom.us/v2/users/{u_id}", headers = {
            'content-type' : 'application/json',
            "Authorization": f"Bearer {access_token}"
        }, data=json.dumps(payload))
        return HttpResponse(status=200)
    return