from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django_redis import get_redis_connection
import hashlib



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
        r = get_redis_connection("default")
        user = r.hgetall(f"user:{request.POST['username']}")
        if user is not None:
            if user[b"password"].decode() == hashlib.sha512(request.POST['password'].encode()).hexdigest():
                return render(request, 'home.html')
            else:
                return render(request, 'login.html', {"error": "Invalid credentials"})
        else:
            return render(request, 'login.html', {"error": "Invalid credentials"})

    return render(request, 'login.html')


@csrf_protect
def register(request):
    if request.method == 'POST':
        r = get_redis_connection("default")
        user = {
            "username": request.POST['username'],
            "password": hashlib.sha512(request.POST['password'].encode()).hexdigest(),
            "account_type": request.POST['accountType']
        }
        password_conf = request.POST['passwordConf']
        if (user["password"] == hashlib.sha512(password_conf.encode()).hexdigest() and user["username"] != '') and (user["password"] != '' and r.get(user["username"]) is None):
            r.hset(f"user:{user['username']}", mapping=user)
            return render(request, 'login.html', {"success": "User created successfully, you can now login", "user": user["username"]})
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