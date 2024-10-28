from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.courses, name='courses'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('courses_inscriptions/<int:course_id>', views.courses_inscriptions, name='courses_inscriptions'),
]