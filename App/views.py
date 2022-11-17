from math import floor,ceil

import App.views
from django.core.exceptions import PermissionDenied
from App.functions import view_from_database, from_str_to_table_model
from django.shortcuts import render, redirect
from django.views import View
from App.models import *
from django.conf import settings
from .uploads import getNewName
from django.contrib import messages
import hashlib
import os
from django.apps import apps

from .functions import create_account, login, edit_profile


class Homescreen(View):
    def get(self, request):
        index = Campaign.objects.all()[:3]
        return render(request, "Homescreen.html", {"campaign_index": index, 'login': request.session.get("login", None),
                                                   "role": request.session.get("role", None)})

    def post(self, request):
        if request.method == 'POST' and 'login_page' in request.POST:
            return render(request, "Login.html")

        if request.method == 'POST' and 'logout' in request.POST:
            request.session.clear()
            return redirect('/', request)

        if request.method == 'POST' and 'create_account_page' in request.POST:
            return render(request, "CreateAccount.html")

        if request.method == 'POST' and "login_button" in request.POST:
            if not login(request.POST['uname'], request.POST['psw']):
                return render(request, "Login.html", {"message": "Incorrect Login credentials"})
            else:
                request.session['login'] = request.POST['uname']
                request.session['role'] = MyUser.objects.get(username=request.POST['uname']).role
                return render(request, "Homescreen.html", {"login": request.session['login'],
                                                           "role": request.session['role']})

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
            length = len(lst)
            lst1 = []
            lst2 = []
            for i in range(ceil(length/2) ):
                lst1.append(lst[i])

            for i in range(ceil(length/2) , length):
                lst2.append(lst[i])
            print(lst1)
            print(lst2)
            return render(request, "MyCampaigns.html", {"first_half": lst1, 'second_half': lst2, "login": request.session['login']})

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
            length = len(lst)
            lst1 = []
            lst2 = []
            for i in range(floor(length / 2) + 1):
                lst1.append(lst[i])

            for i in range(floor(length / 2) + 1, length):
                lst2.append(lst[i])
            print(lst1)
            print(lst2)
            return render(request, "MyCampaigns.html", {"first_half": lst1, 'second_half': lst2})

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

        # if request.method == "POST" and "selected-table" in request.POST:
        #     request.session['table_model'] = request.POST['selected-table']
        #     return TableView().get(request)


class Landing(View):
    def get(self, request):
        return render(request, "Landing.html", {})

    def post(self, request):
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

    def post(self, request):
        return redirect("/", request)


class ViewDatabase(View):
    def get(self, request):
        if request.session['role'] != "Admin":
            raise PermissionDenied()

        return render(request, "ViewDatabase.html", {"login": request.session['login'],
                                                     "role": request.session['role'],
                                                     "tables": [model.verbose_name for model
                                                                in apps.get_app_config("App").get_models()],
                                                     "table_selected": False})

    def post(self, request):
        if request.session['login'] is None or request.session['role'] != "Admin":
            raise PermissionDenied()

        table_data = []

        if "selected-table" in request.POST:  # New table was selected
            request.session['table_model'] = request.POST['selected-table']
            table_model = from_str_to_table_model(request.session['table_model'])
            request.session['fields_list'] = []
            request.session['table_columns'] = []

            if table_model is not None:
                table_meta = table_model._meta
                request.session['table_columns'] = [f.name for f in table_meta.fields]

                for field in request.session['table_columns']:
                    if field != table_meta.pk.name:
                        choices_for_field = table_meta.get_field(field).choices
                        if choices_for_field is None:
                            request.session['fields_list'].append((field, None))
                        else:
                            choices_for_field = [t[0] for t in choices_for_field]
                            request.session['fields_list'].append((field, choices_for_field))
        else:  # Query was made on selected table
            keyword_dict: dict[str, str] = {}
            table_model = from_str_to_table_model(request.session['table_model'])

            for field_tuple in request.session['fields_list']:
                field_name = field_tuple[0]
                if request.POST[field_name] != "":
                    if field_name == "password":
                        keyword_dict.update({'password': hashlib.sha256(request.POST['password'].encode('utf-8'))
                                            .hexdigest()})
                    else:
                        keyword_dict.update({field_name + "__iexact": request.POST[field_name]})

            query_result = view_from_database(table_model, **keyword_dict)
            table_meta = table_model._meta
            foreign_keys = [fk.name for fk in table_meta.fields if isinstance(fk, models.ForeignKey)]

            for record in query_result:
                record_data_list = []

                for field in request.session['table_columns']:
                    data_holder = getattr(record, field)

                    if field in foreign_keys:
                        fk_field = table_meta.get_field(field).to_fields[0]
                        next_data_value = getattr(data_holder, fk_field)
                    else:
                        next_data_value = data_holder

                    record_data_list.append(next_data_value)
                table_data.append(record_data_list)

        return render(request, "ViewDatabase.html", {"login": request.session['login'],
                                                     "role": request.session['role'],
                                                     "tables": [model.__name__ for model
                                                                in apps.get_app_config("App").get_models()],
                                                     "fields_list": request.session['fields_list'],
                                                     "table_columns": request.session['table_columns'],
                                                     "table_model": request.session['table_model'],
                                                     "table_data": table_data, "table_selected": True})

