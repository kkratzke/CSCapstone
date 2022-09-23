from django.shortcuts import render, redirect
from django.views import View
from App.models import *
from .models import MyUser
import datetime
import hashlib


class Homescreen(View):

    def get(self, request):
        return render(request, "Homescreen.html", {})

    def post(self, request):
        if request.method == 'POST' and 'login_page' in request.POST:
            return render(request, "Login.html")

        if request.method == 'POST' and 'create_account_page' in request.POST:
            return render(request, "CreateAccount.html")

        if request.method == 'POST' and "login_button" in request.POST:
            uname = request.POST['uname']
            password = request.POST['psw']
            noSuchUser = False
            badPass = False
            try:
                m = MyUser.objects.get(username__iexact=uname)
                if m.password != hashlib.sha256(password.encode("utf-8")).hexdigest():
                    badPass = True
            except:
                noSuchUser = True

            if (noSuchUser or badPass):
                return render(request, "Login.html", {"message": "Incorrect Login credentials"})
            else:
                return redirect("/landing/", request)

        if request.method == 'POST' and "create_account_button" in request.POST:
            uname = request.POST['uname']
            email = request.POST['email']
            first = request.POST['first_name']
            last = request.POST['last_name']
            password = request.POST['password']
            password2 = request.POST['password2']
            message = ""
            foundUser = True
            try:
                m = MyUser.objects.get(username__iexact=uname)
            except:
                foundUser = False

            if foundUser:
                message = "Username already taken"

            if password != password2:
                message = "Passwords do not match"

            if message != "":
                return render(request, "CreateAccount.html", {"message": message})
            else:
                x = MyUser(username=uname, password=hashlib.sha256(password.encode('utf-8')).hexdigest(),
                           first_name=first, last_name=last, email=email)
                x.save()
                return redirect("/landing/", request)


class Landing(View):
    def get(self, request):
        return render(request, "Landing.html", {})

    def post(selfself, request):
        return redirect("/", request)
