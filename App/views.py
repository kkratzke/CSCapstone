from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import View
from App.models import *
from .models import MyUser
import datetime
import hashlib


class Homescreen(View):

    def get(self, request):
        return render(request, "Homescreen.html", {})

    def post(self, request):
        if request.method == 'POST' and 'login_button' in request.POST:
            return redirect("/login", request)

        if request.method == 'POST' and 'create_button' in request.POST:
            return redirect("/createAccount", request)

        # print("hello")
class Login(View):
    def get(self, request):
        return render(request, "Login.html", {})

    def post(self, request):
        print("hello")
        uname = request.POST['uname']
        password = request.POST['psw']
        noSuchUser = False
        badPass = False
        try:
            m = MyUser.objects.get(username__iexact=uname)
            if m.password != password:
                badPass = True
        except:
            noSuchUser = True

        if (noSuchUser or badPass):
            return render(request, "Login.html", {"message": "Incorrect Login credentials"})
        else:
            return redirect("/landing", request)


class CreateAccount(View):
    def get(self, request):
        return render(request, "CreateAccount.html", {})

    def post(self, request):

        return redirect("/landing/", request)

class Landing(View):
    def get(self, request):
        return render(request, "Landing.html", {})

    def post(selfself, request):
        return redirect("/", request)
