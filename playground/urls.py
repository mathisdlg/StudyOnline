from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.courses, name='courses'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('courses_inscriptions/<str:course_id>', views.courses_inscriptions, name='courses_inscriptions'),
    path('create_course/', views.create_course, name='create_course'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('courses_unregister/<str:course_id>', views.courses_unregister, name='courses_unregister'),
    path('update_course/<str:course_id>', views.update_course, name='update_course'),
    path('delete_course/<str:course_id>', views.delete_course, name='delete_course'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('search/', views.search_page, name='search'),
]