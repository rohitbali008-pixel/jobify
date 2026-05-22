from django.urls import path
from . import views

urlpatterns = [
    # path('create/',  views.create_jobs, name= 'createjobs'),
    path('register/',views.register, name='register'),
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('data/',  views.show_user, name= 'show_student'),
    path('profile/', views.user_profile, name='user_profile'),
    path('add/', views.add_employee , name ='add_employee'),
    path('jobs/', views.vacancy, name='vacancy'),
    path('cards/',views.cards, name='cards'),
    path('abc/',views.eligbility, name='eligibilty')
]