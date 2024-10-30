from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django_redis import get_redis_connection
from django.shortcuts import redirect, reverse
from django.contrib import messages
import hashlib
import uuid

def is_authenticated(cookies):
    r = get_redis_connection("default")
    if cookies.get("user_token") is not None:
        return (cookies.get("user_token") == r.get(f"user_token:{cookies.get('username')}").decode())


def set_cookie(response, user_token, user):
    response.set_cookie("user_token", user_token)
    response.set_cookie("username", user[b"username"].decode())
    return response

def delete_cookie(request, response):
    r = get_redis_connection("default")
    r.delete(f"user_token:{request.COOKIES.get('username')}")
    response.delete_cookie("user_token")
    response.delete_cookie("username")
    return response


def home(request): # Check courses by category like prog, web dev, etc...
    return render(request, 'home.html')


def courses(request):
    return render(request, 'courses.html', {"courses": courses})


@csrf_protect
def login(request):
    if is_authenticated(request.COOKIES):
        messages.add_message(request, messages.SUCCESS, "You are already logged in")
        return redirect(reverse('home'))

    if request.method == 'POST':
        r = get_redis_connection("default")
        user = r.hgetall(f"user:{request.POST['username']}")
        if user != {}:
            if user[b"password"].decode() == hashlib.sha512(request.POST['password'].encode()).hexdigest():
                user_token = uuid.uuid4()
                r.set(f"user_token:{request.POST['username']}", str(user_token))
                response = redirect(reverse('home'))
                response = set_cookie(response, user_token, user)
                messages.add_message(request, messages.SUCCESS, "You are logged in")
                return response
            else:
                messages.add_message(request, messages.ERROR, "Invalid credentials")
                return render(request, 'login.html')
        else:
            messages.add_message(request, messages.ERROR, "Invalid credentials")
            return render(request, 'login.html')

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
            
            user_token = uuid.uuid4()
            r.set(f"user_token:{user['username']}", user_token)

            response = redirect(reverse('home'))
            response = set_cookie(response, user_token, user)
            messages.add_message(request, messages.SUCCESS, "User created successfully")
            return response
        else:
            return render(request, 'register.html', {"error": "Invalid credentials"})

    return render(request, 'register.html')


def profile(request):
    return render(request, 'profile.html')


def logout(request):
    if is_authenticated(request.COOKIES):
        response = redirect(reverse('home'))
        response = delete_cookie(request, response)
        messages.add_message(request, messages.SUCCESS, "You are logged out")
        return response
    messages.add_message(request, messages.ERROR, "You are not logged in")
    return redirect(reverse('home'))


def courses_inscriptions(request, course_id: int):
    if request.user.is_authenticated:
        return render(request, 'courses_inscriptions.html')
    else:
        messages.add_message(request, messages.ERROR, "You are not logged in")
        return redirect(reverse('login'))