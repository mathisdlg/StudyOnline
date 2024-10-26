from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def say_hello(request):
    courses = [
        {
            "name": "Python",
            "url": "https://www.edx.org/learn/python"
        }
    ]
    return render(request, 'hello.html', {"name": "giga chad", "courses": courses})