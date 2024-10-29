from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
import redis
import hashlib

USER_BD = 0


def home(request): # Check courses by category like prog, web dev, etc...
    return render(request, 'home.html')


def courses(request):
    courses = [
        {
            "id": 1,
            "name": "Python",
            "category": "Programming",
            "url": "https://www.edx.org/learn/python"
        },
        {
            "id": 2,
            "name": "Django",
            "category": "Web development",
            "url": "https://www.edx.org/learn/django"
        },
        {
            "id": 3,
            "name": "Flask",
            "category": "Web development",
            "url": "https://www.edx.org/learn/flask"
        }
    ]
    return render(request, 'courses.html', {"courses": courses})


@csrf_protect
def login(request):
    if request.method == 'POST':
        r = redis.Redis(host='localhost', port=6379, db=0)
        user = r.get(request.POST['username'])
        if user is not None:
            if user.decode() == hashlib.sha256(request.POST['password'].encode()).hexdigest():
                return render(request, 'home.html')
        else:
            return render(request, 'login.html', {"error": "Invalid credentials"})

    return render(request, 'login.html')


@csrf_protect
def register(request):
    if request.method == 'POST':
        r = redis.Redis(host='localhost', port=6379, db=0)
        username = r.get(request.POST['username'])
        password = r.get(request.POST['password'])
        password_conf = r.get(request.POST['passwordConf'])
        account_type = r.get(request.POST['accountType'])
        if (password == password_conf and username != '') and (password != '' and r.get(username) is None):
            r.set(username, {'role': account_type, 'password': hashlib.sha256(password.encode()).hexdigest()})
            return render(request, 'login.html', {"success": "User created successfully, you can now login", "user": username})
        else:
            return render(request, 'register.html', {"error": "Invalid credentials"})

    return render(request, 'register.html')


def profile(request):
    return render(request, 'profile.html')


def logout(request):
    return render(request, 'home.html')


def courses_inscriptions(request, course_id: int):
    if request.user.is_authenticated:
        return render(request, 'courses_inscriptions.html')
    else:
        return render(request, 'login.html')