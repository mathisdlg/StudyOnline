from django.shortcuts import render
from django.http import HttpResponse


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


def login(request):
    return render(request, 'login.html')


def register(request):
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