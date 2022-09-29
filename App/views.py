from django.shortcuts import render, redirect
from django.views import View
from App.models import *
from .models import MyUser
import datetime
import hashlib
from .functions import *


class Homescreen(View):

    def get(self, request):
        return render(request, "Homescreen.html", {})

    def post(self, request):
        if request.method == 'POST' and 'login_page' in request.POST:
            return render(request, "Login.html")

        if request.method == 'POST' and 'create_account_page' in request.POST:
            return render(request, "CreateAccount.html")

        if request.method == 'POST' and "login_button" in request.POST:
            if not login(request.POST['uname'],request.POST['psw']):
                return render(request, "Login.html", {"message": "Incorrect Login credentials"})
            else:
                return redirect("/landing/", request)

        if request.method == 'POST' and "create_account_button" in request.POST:
            message = create_account(request.POST['uname'], request.POST['email'], request.POST['first_name'],
                           request.POST['last_name'], request.POST['password'], request.POST['password2'])

            if message != "":
                return render(request, "CreateAccount.html", {"message": message})
            else:
                return redirect("/landing/", request)


class Landing(View):
    def get(self, request):
        return render(request, "Landing.html", {})

    def post(selfself, request):
        return redirect("/", request)
