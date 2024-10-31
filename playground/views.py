from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django_redis import get_redis_connection
from django.shortcuts import redirect, reverse
from django.contrib import messages
import hashlib
import uuid


ACCOUNT_TYPE = ["Prof", "Student"]



def is_authenticated(cookies):
    r = get_redis_connection("default")
    cookies_token = cookies.get("user_token")
    cookies_username = cookies.get("username")
    if cookies_username is not None and cookies_token is not None:
        token = r.get(f"user_token:{cookies_username}").decode()
        if token is not None:
            return (cookies_token == token)
    return False


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


def home(request):
    return render(request, 'home.html')


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
    if is_authenticated(request.COOKIES):
        messages.add_message(request, messages.SUCCESS, "You are already logged in")
        return redirect(reverse('home'))

    if request.method == 'POST':
        r = get_redis_connection("default")
        user = {
            "username": request.POST['username'],
            "password": hashlib.sha512(request.POST['password'].encode()).hexdigest(),
            "account_type": request.POST['accountType'] if request.POST['accountType'] in ACCOUNT_TYPE else "Student",
        }
        password_conf = request.POST['passwordConf']
        if (user["password"] == hashlib.sha512(password_conf.encode()).hexdigest() and user["username"] != '') and (user["password"] != '' and r.get(user["username"]) is None):
            r.hset(f"user:{user['username']}", mapping=user)
            
            user_token = uuid.uuid4()
            r.set(f"user_token:{user['username']}", str(user_token))

            user = r.hgetall(f"user:{user['username']}")
            response = redirect(reverse('home'))
            response = set_cookie(response, str(user_token), user)
            messages.add_message(request, messages.SUCCESS, "User created successfully")
            return response
        else:
            return render(request, 'register.html', {"error": "Invalid credentials"})

    return render(request, 'register.html')


def profile(request):
    if not is_authenticated(request.COOKIES):
        messages.add_message(request, messages.ERROR, "You are not logged in")
        return redirect(reverse('login'))
    r = get_redis_connection("default")
    user = r.hgetall(f"user:{request.COOKIES.get('username')}")
    user["username"] = user[b"username"].decode()
    user["account_type"] = user[b"account_type"].decode()

    courses_registred = []
    if user["account_type"] == "Prof":
        courses = []
        for key in r.scan_iter(match="course:*"):
            course = r.hgetall(key)
            course["name"] = course[b"name"].decode()
            course["description"] = course[b"description"].decode()
            course["level"] = course[b"level"].decode()
            course["professor"] = course[b"professor"].decode()
            course["places"] = course[b"places"].decode()
            course["students"] = [student.decode() for student in r.lrange(f"registered_student:{course[b'students'].decode()}", 0, -1)]
            course["remaining_places"] = int(course["places"]) - len(course["students"])
            if request.COOKIES.get('username') == course["professor"]:
                courses.append(course)
            if request.COOKIES.get('username') in course["students"]:
                courses_registred.append(course)
        user["courses"] = courses
    else:
        courses = []
        for key in r.scan_iter(match="course:*"):
            course = r.hgetall(key)
            course["name"] = course[b"name"].decode()
            course["description"] = course[b"description"].decode()
            course["level"] = course[b"level"].decode()
            course["professor"] = course[b"professor"].decode()
            course["places"] = course[b"places"].decode()
            course["students"] = [student.decode() for student in r.lrange(f"registered_student:{course[b'students'].decode()}", 0, -1)]
            course["remaining_places"] = int(course["places"]) - len(course["students"])
            if request.COOKIES.get('username') in course["students"]:
                courses_registred.append(course)
    user["courses_registred"] = courses_registred
    
    return render(request, 'profile.html', {"user": user})


def update_profile(request):
    if not is_authenticated(request.COOKIES):
        messages.add_message(request, messages.ERROR, "You are not logged in")
        return redirect(reverse('login'))

    r = get_redis_connection("default")
    user = r.hgetall(f"user:{request.COOKIES.get('username')}")
    user["username"] = user[b"username"].decode()
    user["account_type"] = user[b"account_type"].decode()
    
    if request.method == 'POST':
        new_username = request.POST['username']
        if new_username == user["username"]:
            ...
        elif new_username != '' and r.hgetall(f"user:{new_username}") == {}:
            user["username"] = request.POST['username']
        else:
            messages.add_message(request, messages.ERROR, "Invalid/Already used username")
            return render(request, 'update_profile.html', {"user": user})

        if request.POST['account_type'] in ACCOUNT_TYPE:
            user["account_type"] = request.POST['account_type']
        else:
            messages.add_message(request, messages.ERROR, "Invalid account type")
            return render(request, 'update_profile.html', {"user": user})

        password = hashlib.sha512(request.POST['password'].encode()).hexdigest()
        if user[b"password"].decode() == password:
            r.delete(f"user:{user['username']}")
            r.hset(f"user:{user['username']}", mapping=user)
            messages.add_message(request, messages.SUCCESS, "User updated successfully")
            return redirect(reverse('profile'))
        else:
            messages.add_message(request, messages.ERROR, "Invalid password")
            return render(request, 'update_profile.html', {"user": user})
    
    return render(request, 'update_profile.html', {"user": user})


def logout(request):
    response = redirect(reverse('home'))
    if is_authenticated(request.COOKIES):
        messages.add_message(request, messages.SUCCESS, "You are logged out")
    else:
        messages.add_message(request, messages.ERROR, "You are not logged in")
    response = delete_cookie(request, response)
    return response


def create_course(request):
    r = get_redis_connection("default")
    cookies = request.COOKIES
    if r.hgetall(f"user:{cookies.get('username')}")[b"account_type"].decode() == "Prof" and is_authenticated(cookies):
        if request.method == 'POST':
            students_list_uuid = str(uuid.uuid4())
            course = {
                "name": request.POST['name'],
                "description": request.POST['description'],
                "level": request.POST['level'],
                "places": request.POST['places'],
                "professor": cookies.get('username'),
                "students": students_list_uuid,
            }
            if r.hgetall(f"course:{course['name']}") != {}:
                messages.add_message(request, messages.ERROR, "Course already exists")
                return render(request, 'create_course.html')
            
            r.hset(f"course:{course['name']}", mapping=course)

            messages.add_message(request, messages.SUCCESS, "Course created successfully")
            return redirect('courses')

        return render(request, 'create_course.html')
    else:
        messages.add_message(request, messages.ERROR, "You are not logged in has a professor")
        return redirect(reverse('home'))


def courses(request):
    r = get_redis_connection("default")
    courses = []
    for key in r.scan_iter(match="course:*"):
        course = r.hgetall(key)
        course["name"] = course[b"name"].decode()
        course["description"] = course[b"description"].decode()
        course["level"] = course[b"level"].decode()
        course["professor"] = course[b"professor"].decode()
        course["places"] = course[b"places"].decode()
        course["students"] = [student.decode() for student in r.lrange(f"registered_student:{course[b'students'].decode()}", 0, -1)]
        course["remaining_places"] = int(course["places"]) - len(course["students"])
        courses.append(course)
    return render(request, 'courses.html', {"courses": courses})


@csrf_protect
def courses_inscriptions(request, course_id):
    r = get_redis_connection("default")
    if r.hgetall(f"course:{course_id}") != {}:
        if is_authenticated(request.COOKIES):
            course = r.hgetall(f"course:{course_id}")
            course["name"] = course[b"name"].decode()
            course["description"] = course[b"description"].decode()
            course["level"] = course[b"level"].decode()
            course["professor"] = course[b"professor"].decode()
            course["places"] = course[b"places"].decode()
            course["students"] = [student.decode() for student in r.lrange(f"registered_student:{course[b'students'].decode()}", 0, -1)]
            course["remaining_places"] = int(course["places"]) - len(course["students"])

            if request.method == 'POST':
                username = request.COOKIES.get('username')
                if username in course["students"]:
                    messages.add_message(request, messages.INFO, "You are already registered in the course")
                elif course["professor"] == username:
                    messages.add_message(request, messages.ERROR, "You are the professor of the course")
                elif course["remaining_places"] > 0:
                    r.lpush(f"registered_student:{ r.hget(f'course:{course_id}', 'students').decode()}", request.COOKIES.get('username'))
                    messages.add_message(request, messages.SUCCESS, "You are registered in the course")
                else:
                    messages.add_message(request, messages.ERROR, "There are no places left in the course")
                
                return redirect(reverse('courses_inscriptions', args=[course_id]))
            
            return render(request, 'courses_inscriptions.html', {"course": course})
        else:
            messages.add_message(request, messages.ERROR, "You are not logged in")
            return redirect(reverse('login'))
    else:
        messages.add_message(request, messages.ERROR, "Course does not exist")
        return redirect('courses')


def courses_unregister(request, course_id):
    if not is_authenticated(request.COOKIES):
        messages.add_message(request, messages.ERROR, "You are not logged in")
        return redirect(reverse('login'))
    
    r = get_redis_connection("default")
    course = r.hgetall(f"course:{course_id}")
    course["name"] = course[b"name"].decode()
    course["description"] = course[b"description"].decode()
    course["level"] = course[b"level"].decode()
    course["professor"] = course[b"professor"].decode()
    course["places"] = course[b"places"].decode()
    course["students"] = [student.decode() for student in r.lrange(f"registered_student:{course[b'students'].decode()}", 0, -1)]
    course["remaining_places"] = int(course["places"]) - len(course["students"])

    if request.COOKIES.get('username') in course["students"]:
        r.lrem(f"registered_student:{course[b'students'].decode()}", 0, request.COOKIES.get('username'))
        messages.add_message(request, messages.SUCCESS, "You are unregistered in the course")
    else:
        messages.add_message(request, messages.INFO, "You are not registered in the course")
    return redirect(reverse('profile'))
