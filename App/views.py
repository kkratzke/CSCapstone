from django.shortcuts import render, redirect
from django.views import View
from App.models import *
from .models import MyUser, Campaign
import datetime
import hashlib
from .functions import create_account, login, edit_profile


class Homescreen(View):

    def get(self, request):
        request.session['login'] = None
        index = Campaign.objects.all()[:3]
        return render(request, "Homescreen.html", {"campaign_index": index})

    def post(self, request):
        if request.method == 'POST' and 'login_page' in request.POST:
            return render(request, "Login.html")

        if request.method == 'POST' and 'logout' in request.POST:
            return redirect('/', request)

        if request.method == 'POST' and 'create_account_page' in request.POST:
            return render(request, "CreateAccount.html")

        if request.method == 'POST' and "login_button" in request.POST:
            if not login(request.POST['uname'], request.POST['psw']):
                return render(request, "Login.html", {"message": "Incorrect Login credentials"})
            else:
                request.session['login'] = request.POST['uname']
                return render(request, "Homescreen.html", {"login": request.session['login']})

        if request.method == 'POST' and "create_account_button" in request.POST:
            ret = create_account(request.POST['uname'], request.POST['email'], request.POST['first_name'],
                                 request.POST['last_name'], request.POST['password'], request.POST['password2'])
            message = ret[0]
            reload_content = ret[1]
            if message != "":
                return render(request, "CreateAccount.html", {"message": message, "reload_content": reload_content})
            else:
                return redirect("/pagejump/", request)

        if request.method == 'POST' and 'create_campaign_page' in request.POST:
            return render(request, "CreateCampaign.html")
        
        if request.method == 'POST' and 'my_campaigns' in request.POST:
            return render(request, "MyCampaigns.html")

        if request.method == 'POST' and "create_campaign" in request.POST:
            logged_in = request.session['login']
            if logged_in is None:
                # need to deny access to creating a campaign
                return render(request, "CreateCampaign.html", {"message": "Must be logged in to create campaigns"})
            else:
                campaignName = request.POST['campaign_name']
                type = request.POST['type']
                highest_code_campaign = Campaign.objects.all().order_by('-id')[:1].first()
                highest_code = highest_code_campaign.campaignCode + 1
                owner = request.session['login']
                newCampaign = Campaign(campaignName=campaignName, type=type, campaignCode=highest_code, owner=owner)
                newCampaign.save()
                return render(request, "Homescreen.html", {"login": request.session['login']})

        if request.method == 'POST' and 'my_campaigns' in request.POST:
            # make the MyCampaigns html appear - need to pass the logged-in user's campaigns
            my_campaigns = Campaign.objects.get(owner__iexact=request.session['login'])
            return render(request, {'campaigns': my_campaigns})

        if request.method == 'POST' and "delete_campaign" in request.POST:
            campaignId = request.POST['campaignId']
            campaign = Campaign.objects.get(id__iexact=campaignId)
            campaign.delete()

            my_campaigns = Campaign.objects.get(owner__iexact=request.session['login'])

            # make the MyCampaigns html appear again
            return render({'campaigns': my_campaigns})

        if request.method == 'POST' and 'edit_profile_page' in request.POST:
            logged_in = request.session['login']
            if logged_in is None:
                # need to deny access to edit account
                return render(request, "Profile.html", {"message": "Must be logged in to edit profile"})
            else:
                owner = MyUser.objects.get(username__iexact=request.session['login'])
                reload_content = [owner.email, owner.first_name, owner.last_name, "", ""]
                return render(request, "Profile.html", {"reload_content": reload_content})

        if request.method == 'POST' and "edit_profile_button" in request.POST:
            owner = MyUser.objects.get(username__iexact=request.session['login'])
            message = edit_profile(request.POST['email'], request.POST['first_name'], request.POST['last_name'],
                                   request.POST['password'], request.POST['password2'], request.session['login'])
            reload_content = [owner.email, owner.first_name, owner.last_name, "", ""]
            if message != "":
                return render(request, "Profile.html", {"message": message, "reload_content": reload_content})
            else:
                return render(request, "Homescreen.html", {"login": request.session['login']})


class Landing(View):
    def get(self, request):
        return render(request, "Landing.html", {})

    def post(selfself, request):
        return redirect("/", request)
class LogIn(View):
    def get(self, request):
        return render(request, "Login.html", {})
    def post(self, request):
        if request.method == 'POST' and 'create_account_page' in request.POST:
            return redirect("/createaccount/")
class CreateAccount(View):
    def get(self, request):
        return render(request, "CreateAccount.html")


class PageJump(View):
    def get(self, request):
        return render(request, "PageJump.html", {})

    def post(selfself, request):
        return redirect("/", request)
