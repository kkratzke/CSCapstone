"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from App.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('AdminPage/', AdminHome.as_view(), name='AdminMain'),
    path('Classes/', Classes.as_view(), name='Classes'),
    path('Create/', AccountCreation.as_view(), name='CreateAccount'),
    path('AllUsers/', AllUsers.as_view(), name='AllUsers'),
    url(r'^AllUsers/(?P<username>[a-zA-Z0-9]+.*)', AllUsers.as_view(), kwargs=None, name="AllUsers"),
    path('Main/', Users.as_view(), name='Main'),
    path('UserEdit/', UserEdit.as_view(), name='Edit'),
    path('UserClasses/', UserClasses.as_view(), name='UserClasses'),
    path('CourseCreation/', CreateCourse.as_view(), name='CreateCourse'),
    path('EditCourse/', EditCourse.as_view(), name='EditCourse'),
    url(r'^EditCourse/(?P<course>[a-zA-Z0-9]+.*)', EditCourse.as_view(), kwargs=None, name="EditCourse"),
    path('DeleteCourse/', DeleteCourse.as_view(), name='DeleteCourse'),
    url(r'^DeleteCourse/(?P<delete>[a-zA-Z0-9]+.*)', DeleteCourse.as_view(), kwargs=None, name="DeleteCourse"),
    path('ViewSections/', ViewSections.as_view(), name='ViewSections'),
    url(r'^ViewSections/(?P<course>[a-zA-Z0-9]+.*)', ViewSections.as_view(), kwargs=None, name="ViewSections"),
    path('DeleteSection/', DeleteSection.as_view(), name='DeleteSection'),
    url(r'^DeleteSection/(?P<delete_section>[a-zA-Z0-9]+.*)', DeleteSection.as_view(), kwargs=None, name="DeleteSection"),
    path('AddSection/', AddSection.as_view(), name='AddSection'),
]
