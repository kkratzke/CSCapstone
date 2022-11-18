from math import floor, ceil
from enum import Enum
from django.core.exceptions import PermissionDenied
from App.functions import view_from_database, from_str_to_table_model, create_fields_list, to_dict
from django.shortcuts import render, redirect
from django.views import View
from App.models import *
from django.conf import settings
from .uploads import getNewName
from django.http import HttpResponse, Http404
from django.contrib import messages
import datetime
import hashlib
import os
from django.apps import apps

from .functions import create_account, login, edit_profile, getNewName


class Homescreen(View):
    def get(self, request):
        index = Campaign.objects.all()[:3]

        if "login" not in request.session:
            request.session['login'] = None
        if "role" not in request.session:
            request.session['role'] = None

        return render(request, "Homescreen.html", {"campaign_index": index, 'login': request.session["login"],
                                                   "role": request.session["role"]})

    def post(self, request):
        if request.method == 'POST' and 'login_page' in request.POST:
            return render(request, "Login.html")

        if request.method == 'POST' and 'logout' in request.POST:
            request.session.clear()
            request.session['login'] = None
            request.session['role'] = None
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
            # campaign = Campaign.objects.get(id__iexact=campaignId)
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
            raise PermissionDenied

        return render(request, "ViewDatabase.html", {"login": request.session['login'],
                                                     "role": request.session['role'],
                                                     "tables": [model.__name__ for model
                                                                in apps.get_app_config("App").get_models()],
                                                     "table_selected": False})

    def post(self, request):
        if request.session['login'] is None or request.session['role'] != "Admin":
            raise PermissionDenied

        table_data = []

        if "selected-table" in request.POST:  # New table was selected
            request.session['table_model'] = request.POST['selected-table']
            table_model = from_str_to_table_model(request.session['table_model'])
            request.session['fields_list'] = []
            request.session['table_columns'] = []

            if table_model is not None:
                table_meta = table_model._meta
                request.session['table_columns'] = [f.name for f in table_meta.fields if f.name != "password"]

                for field in [f.name for f in table_meta.fields]:
                    choices_for_field = table_meta.get_field(field).choices
                    if choices_for_field is None:
                        request.session['fields_list'].append((field, None))
                    else:
                        choices_for_field = [t[0] for t in choices_for_field]
                        request.session['fields_list'].append((field, choices_for_field))
        else:  # Query was made on selected table
            keyword_dict: dict[str, str] = {}
            table_model = from_str_to_table_model(request.session['table_model'])
            table_meta = table_model._meta
            foreign_keys = [fk.name for fk in table_meta.fields if isinstance(fk, models.ForeignKey)]

            for field_tuple in request.session['fields_list']:
                field_name = field_tuple[0]
                if request.POST[field_name] != "":
                    if field_name == "password":
                        keyword_dict.update({'password': hashlib.sha256(request.POST['password'].encode('utf-8'))
                                            .hexdigest()})
                    else:
                        keyword_string_middle = "__" + table_meta.get_field(field_name).to_fields[0] \
                            if field_name in foreign_keys else ""
                        keyword_dict.update({field_name + keyword_string_middle + "__iexact": request.POST[field_name]})

            query_result = view_from_database(table_model, **keyword_dict)

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
                                                     "table_data": table_data, "table_selected": True,
                                                     "search_made": table_meta.pk.name in request.POST,
                                                     "no_results": len(table_data) == 0})


class EditDatabase(View):
    class ConfirmationStatus(Enum):
        MESSAGE_NO_CHANGE = -1,
        NO_MESSAGE = 0,
        MESSAGE_CONFIRM = 1,
        MESSAGE_UPDATE = 2

    def get(self, request):
        if request.session['login'] is None or request.session['role'] != "Admin":
            raise PermissionDenied

        return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                     "role": request.session['role'],
                                                     "tables": [model.__name__ for model
                                                                in apps.get_app_config("App").get_models()]})

    def post(self, request):
        if request.session['login'] is None or request.session['role'] != "Admin":
            raise PermissionDenied

        saved_table_selection = request.POST.get('selected-table', None)
        table_model = from_str_to_table_model(request.session.get('selected_table', saved_table_selection))
        record_key = table_model.pk

        if "confirm-changes" in request.POST:  # Changes should be saved to database
            keyword_middle_part = "__" + record_key._meta.to_fields[0] if isinstance(table_model.pk,
                                                                                       models.ForeignKey) else ""
            data_record = table_model.objects.get({table_model.pk.name + keyword_middle_part + "__iexact":
                                                       request.session['selected_record']})

            for change in request.session['changes_list']:
                data_record.setAttr(change[0], change[1])

            data_record.save()
            request.session['data-record'] = to_dict(data_record).values()
            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "record_keys": request.session['record_keys'],
                                                         "selected_record": request.session['selected_record'],
                                                         "data_record": data_record,
                                                         "fields_list": request.session['fields_list'],
                                                         "ask_for_confirmation": self.ConfirmationStatus.MESSAGE_UPDATE})
        elif "save-changes" in request.POST:  # Changes are being asked to save to database
            keyword_middle_part = "__" + record_key._meta.to_fields[0] if isinstance(table_model.pk,
                                                                                       models.ForeignKey) else ""
            data_record = table_model.objects.get({table_model.pk.name + keyword_middle_part + "__iexact":
                                                       request.session['selected_record']})

            warn_about_changes = self.ConfirmationStatus.MESSAGE_NO_CHANGE
            changes_list = []
            names_of_changes = []
            for fieldTuple in request.session['fields_list']:
                is_pk_or_fk = fieldTuple[2]
                field_name = fieldTuple[0]

                if is_pk_or_fk is False and data_record.getAttr(field_name) != request.POST[field_name]:
                    if field_name == "password" and len(request.POST['password']) > 4:
                        names_of_changes.append(field_name)
                        data_record.setAttr("password", hashlib.sha256(request.POST['password'].encode('utf-8'))
                                            .hexdigest())
                        changes_list.append((field_name, data_record.password))
                        warn_about_changes = self.ConfirmationStatus.MESSAGE_CONFIRM
                    elif field_name != "password":
                        names_of_changes.append(field_name)
                        data_record.setAttr(field_name, request.POST[field_name])
                        changes_list.append((field_name, data_record.getAttr(field_name)))
                        warn_about_changes = self.ConfirmationStatus.MESSAGE_CONFIRM

            request.session['changes_list'] = changes_list
            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "record_keys": request.session['record_keys'],
                                                         "data_record": to_dict(data_record).values(),
                                                         "selected_record": request.session['selected_record'],
                                                         "fields_list": request.session['fields_list'],
                                                         "names_of_changes": names_of_changes,
                                                         "ask_for_confirmation": warn_about_changes})

        elif "selected-record" in request.POST:  # Record to be edited from table has been selected
            request.session['selected_record'] = request.POST['selected-record']
            table_meta = table_model._meta
            keyword_middle_part = "__" + record_key._meta.to_fields[0] if isinstance(table_model.pk,
                                                                                     models.ForeignKey) else ""

            data_record = table_model.objects.get(**{table_meta.pk.name + keyword_middle_part + "__iexact":
                                                     request.POST['selected-record']})

            fields_list = []
            for field in [f.name for f in table_meta.fields]:
                choices_for_field = table_meta.get_field(field).choices
                is_pk_or_fk = table_meta.pk.name == field or isinstance(table_meta.get_field(field), models.ForeignKey)

                if choices_for_field is None:
                    fields_list.append((field, None, is_pk_or_fk))
                else:
                    choices_for_field = [t[0] for t in choices_for_field]
                    fields_list.append((field, choices_for_field, is_pk_or_fk))

            request.session['fields_list'] = fields_list
            request.session['data-record'] = to_dict(data_record).values()
            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "record_keys": request.session['record_keys'],
                                                         "data_record": request.session['data-record'],
                                                         "selected_record": request.session['selected_record'],
                                                         "table_selected": True,
                                                         "table_model": request.session["selected_table"],
                                                         "fields_list": fields_list,
                                                         "ask_for_confirmation": self.ConfirmationStatus.NO_MESSAGE})
        else:  # Table to edit has been selected
            request.session['selected_table'] = request.POST['selected-table']

            record_keys = []
            for record in view_from_database(table_model):
                if isinstance(record_key, models.ForeignKey):
                    data_holder = getattr(record, record_key.name)
                    fk_field = table_model._meta.get_field(record_key.name).to_fields[0]
                    actual_value = getattr(data_holder, fk_field)
                else:
                    actual_value = record.pk
                record_keys.append(actual_value)

            request.session['record_keys'] = record_keys
            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "record_keys": record_keys,
                                                         "table_selected": request.session.get("selected_table", None) is not None,
                                                         "table_model": request.session["selected_table"],
                                                         "ask_for_confirmation": self.ConfirmationStatus.NO_MESSAGE})


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
        
        
# class ExplorePage(View):
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


