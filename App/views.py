from math import floor,ceil

from django.shortcuts import render, redirect
from django.views import View
from App.models import *
from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib import messages
import datetime
import hashlib
import os

from .functions import create_account, login, edit_profile, getNewName


class Homescreen(View):

    def get(self, request):
        index = Campaign.objects.all()[:3]
        return render(request, "Homescreen.html", {"campaign_index": index, 'login': request.session.get("login", None), "role": request.session.get("role", None)})

    def post(self, request):
        if request.method == 'POST' and 'login_page' in request.POST:
            return render(request, "Login.html")

        if request.method == 'POST' and 'logout' in request.POST:
            request.session['login'] = None
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
            lst = Campaign.objects.filter(campaign_owner__username__iexact=request.session['login'])
            return render(request, "MyCampaigns.html", {"first_half": lst, "login": request.session['login']})

        if request.method == 'POST' and "create_campaign" in request.POST:
            logged_in = request.session['login']
            if logged_in is None:
                # need to deny access to creating a campaign
                return render(request, "CreateCampaign.html", {"message": "Must be logged in to create campaigns"})
            else:
                campaignName = request.POST['campaign_name']
                type = request.POST['type']
                desc = request.POST['description']
                highest_code_campaign = Campaign.objects.filter(campaign_code__gte=10000)
                val = 10000
                for x in highest_code_campaign:
                    if x.campaign_code > val:
                        val = x.campaign_code
                highest_code = val + 1
                owner = MyUser.objects.filter(username__iexact=request.session['login']).first()
                image = request.FILES.get('image')
                newCampaign = Campaign(campaign_name=campaignName, campaign_type=type, campaign_code=highest_code,
                                       campaign_owner=owner, campaign_description=desc)
                file = image
                new_name = getNewName('image', newCampaign.campaign_code)
                where = '%s/campaign_pic/%s' % (settings.MEDIA_ROOT, new_name)

                content = file.chunks()
                with open(where, 'wb') as f:
                    for i in content:
                        f.write(i)

                newCampaignPictures = CampaignPictures(campaign_code=newCampaign, campaign_pic=new_name)

                newCampaign.save()
                newCampaignPictures.save()

                return render(request, "Homescreen.html", {"login": request.session['login']})

        if request.method == 'POST' and "search_page" in request.POST:
            return render(request, "Search.html", {'campaigns': [], "login": request.session['login']})

        if request.method == 'POST' and "campaign_search" in request.POST:
            search_type = request.POST['search_type']
            info = request.POST['search_info']
            newList = []
            if search_type == 'by_code':
                info = int(info)
                newList = Campaign.objects.filter(campaign_code__exact=info)
            else:
                info = str(info)
                info = info.lower()
                if search_type == 'by_desc':
                    tempList = Campaign.objects.all()
                    for c in tempList:
                        if str(c.campaign_description).lower().__contains__(info):
                            newList.append(c)
                else:  # search_type == 'by_title':
                    tempList = Campaign.objects.all()
                    for c in tempList:
                        if str(c.campaign_name).lower().__contains__(info):
                            newList.append(c)

            return render(request, "Search.html", {'campaigns': newList, "login": request.session['login']})

        if request.method == 'POST' and "go_home" in request.POST:
            index = Campaign.objects.all()[:3]
            return render(request, "Homescreen.html", {"campaign_index": index, "login": request.session['login']})

        if request.method == 'POST' and "view_campaign" in request.POST:
            path = '/ViewCampaign/' + str(request.POST['campaign_code'])
            return redirect(path, request)

        if request.method == 'POST' and "subscribe" in request.POST:
            this_user = MyUser.objects.get(username__iexact=request.session['login'])
            cd = request.POST['campaign_code']
            path = '/ViewCampaign/' + str(cd)
            campaign = Campaign.objects.get(campaign_code__exact=cd)
            campaign.subscribers.add(this_user)
            campaign.save()
            return redirect(path, request)

        if request.method == 'POST' and "unsubscribe" in request.POST:
            this_user = MyUser.objects.get(username__iexact=request.session['login'])
            cd = request.POST['campaign_code']
            path = '/ViewCampaign/' + str(cd)
            campaign = Campaign.objects.get(campaign_code__exact=cd)
            campaign.subscribers.remove(this_user)
            campaign.save()
            return redirect(path, request)

        if request.method == 'POST' and 'edit_campaign_page' in request.POST:
            cd = request.POST['campaign_to_view']
            campaign = Campaign.objects.get(campaign_code__exact=cd)
            types = ['Medical', 'Memorial', 'Emergency', 'Education', 'Other']
            statuses = ['On going', 'Suspended', 'Canceled', 'End']

            return render(request, "EditCampaign.html",
                          {"campaign": campaign, 'login': request.session['login'], 'types': types, 'statuses': statuses})

        if request.method == 'POST' and 'edit_campaign' in request.POST:
            cd = request.POST['campaign_code']
            campaign = Campaign.objects.get(campaign_code__exact=cd)

            nm = request.POST['name']
            desc = request.POST['description']
            status = request.POST['status']
            camp_type = request.POST['type']

            campaign.campaign_name = nm
            campaign.campaign_description = desc
            campaign.campaign_status = status
            campaign.campaign_type = camp_type

            campaign.save()

            lst = Campaign.objects.filter(campaign_owner__username__iexact=request.session['login'])

            return render(request, "MyCampaigns.html",
                          {"campaign": campaign, 'first_half': lst, 'login': request.session['login']})

        if request.method == 'POST' and "delete_campaign" in request.POST:
            cd = request.POST['removal']
            #campaign = Campaign.objects.get(id__iexact=campaignId)
            campaign = Campaign.objects.filter(campaign_code__exact=cd).first()
            campaignPic = CampaignPictures.objects.filter(campaign_code__exact=cd).first()

            if campaignPic is not None:
               campaignPic.delete()
               file = str(campaign.campaign_code) + ".png"
               location = '%s/campaign_pic' % (settings.MEDIA_ROOT)
               path = os.path.join(location, file)
               if os.access(path, os.F_OK):
                  os.remove(path)

            campaign.delete()

            lst = Campaign.objects.filter(campaign_owner__username__iexact=request.session['login'])

            return render(request, "MyCampaigns.html", {"first_half": lst, 'login': request.session['login']})


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
            ProfileImage = request.FILES.get('ProfileImage')
            file = ProfileImage
            new_name = getNewName('image', owner.username)
            where = '%s/user_pic/%s' % (settings.MEDIA_ROOT, new_name)
            if file is not None:
              content = file.chunks()
              with open(where, 'wb') as f:
                for i in content:
                    f.write(i)
              newUserPictures = UserPictures(username=owner, user_pic=new_name)
              newUserPictures.save()

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

class ExplorePage(View):
    def get(self, request):
        return render(request, "Explore.html")
class SubscriptionPage(View):
    def get(self, request):
        return render(request, "Subscriptions.html")
class AccountPage(View):
    def get(self, request):
        return render(request, "Profile.html")
class PaymentPage(View):
    def get(self, request):
        return render(request, "Payment.html")
#class ExplorePage(View):
#    def get(self, request):
#        return render(request, "Explore.html")
class SearchPage(View):
    def get(self, request):
        return render(request, "Search.html", {'campaigns': [], "login": request.session['login']})

class PicUpload(View):
    def get(self, request):
        return render(request, "PicUpload.html", {})

    def post(selfself, request):
        if request.method == 'POST':
            img = Img(img_url=request.FILES.get('img'))
            img.save()
        return render(request, 'PicUpload.html')


def upload_handle(request):
    file = request.FILES['image']

    new_name = getNewName('img_url')

    where = '%s/users/%s' % (settings.MEDIA_ROOT, new_name)

    content = file.chunks()
    with open(where, 'wb') as f:
        for i in content:
            f.write(i)
    return HttpResponse('ok')


def campaign_view(request, slug=None):
    if slug is not None:
        try:
            campaign = Campaign.objects.filter(campaign_code__exact=slug).first()
        except:
            raise Http404
    print(campaign)

    this_user = MyUser.objects.get(username__iexact=request.session['login'])

    found = False
    for i in campaign.subscribers.all():
        if i == this_user:
            found = True
    return render(request, "ViewCampaign.html", {'num_subs': campaign.subscribers.count, "campaign": campaign, "is_subscribed":found, "login": request.session['login']})

