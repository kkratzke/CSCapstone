import json
from math import floor, ceil
from django.core.exceptions import PermissionDenied
from App.functions import view_from_database, from_str_to_table_model, create_fields_list, to_dict, getNewName, \
    remove_record, clear_field
from django.shortcuts import render, redirect
from django.views import View
from App.models import *
from django.conf import settings
from django.http import HttpResponse, Http404
import hashlib
import os
from django.apps import apps
from .functions import create_account, login, edit_profile, getNewName
from App.confirmation_status import ConfirmationStatus
from django.db.models import Count


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

            return render(request, "MyCampaigns.html", {"first_half": lst, "login": request.session['login'],
                                                        "role": request.session['role']})

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

                return render(request, "Homescreen.html", {"login": request.session['login'],
                                                           "role": request.session['role']})

        if request.method == 'POST' and "search_page" in request.POST:
            return render(request, "Search.html", {'campaigns': [], "login": request.session['login'],
                                                   "role": request.session['role']})

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

            return render(request, "Search.html", {'campaigns': newList, "login": request.session['login'],
                                                   "role": request.session['role']})

        if request.method == 'POST' and "go_home" in request.POST:
            index = Campaign.objects.all()[:3]
            return render(request, "Homescreen.html", {"campaign_index": index, "login": request.session['login'],
                                                       "role": request.session['role']})

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
                          {"campaign": campaign, 'first_half': lst, 'login': request.session['login'],
                           "role": request.session['role']})

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

            return render(request, "MyCampaigns.html", {"first_half": lst, 'login': request.session['login'],
                                                        "role": request.session['role']})

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
                return render(request, "Homescreen.html", {"login": request.session['login'],
                                                           "role": request.session['role']})


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

        if "selected-table" in request.POST:
            table_model = from_str_to_table_model(request.POST['selected-table'])
        else:
            table_model = from_str_to_table_model(request.session['selected_table'])

        table_meta = table_model._meta
        record_key = table_meta.pk
        if "delete-record" in request.POST or "clear-record" in request.POST:
            confirmation_value = ConfirmationStatus.DELETE.name if "delete-record" in request.POST \
                else ConfirmationStatus.CLEAR.name
            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "primary_key_values": request.session['primary_key_values'],
                                                         "table_selected": True,
                                                         "allow_deletion": request.session['fields_list'][0][2],
                                                         "selected_record": request.session['selected_record'],
                                                         "table_model": request.session["selected_table"],
                                                         "fields_list": request.session['fields_list'],
                                                         "ask_for_confirmation": confirmation_value})
        elif "confirm" in request.POST:  # Changes should be saved to database
            keyword_middle_part = "__" + record_key.to_fields[0] if record_key.related_model is not None else ""
            data_record = table_model.objects.get(**{record_key.name + keyword_middle_part + "__iexact":
                                                  request.session['selected_record']})
            admin_record = MyUser.objects.get(username__exact=request.session['login'])
            return_messages = []
            if request.POST["confirm"] == "Delete":
                return_messages.append(remove_record(admin_record, data_record))
                confirm_signal = ConfirmationStatus.CONFIRM_REMOVE.name
            elif request.POST["confirm"] == "Clear":
                image_fields = [field.name for field in table_meta.fields if isinstance(field, models.ImageField)]
                for field in image_fields:
                    return_messages.append(clear_field(admin_record, data_record, field))
                confirm_signal = ConfirmationStatus.CONFIRM_REMOVE.name
            else:
                for field_name, change in request.session['changes_list']:
                    print(field_name, change)
                    if isinstance(table_meta.get_field(field_name), models.ImageField):
                        clear_field(admin_record, data_record, field_name)
                    else:
                        if field_name == "password":
                            change = hashlib.sha256(change.encode("utf-8")).hexdigest()
                        setattr(data_record, field_name, change)
                confirm_signal = ConfirmationStatus.CONFIRM_EDIT.name

            request.session.pop('fields_list')
            edited_record_key = request.session.pop('selected_record')
            data_record.save()

            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "primary_key_values": request.session['primary_key_values'],
                                                         "selected_record": edited_record_key,
                                                         "fields_list": [],
                                                         "record_type": request.session['selected_table'],
                                                         "ask_for_confirmation": confirm_signal,
                                                         "result_messages": return_messages})
        elif "save-changes" in request.POST:  # Changes are being asked to save to database
            keyword_middle_part = "__" + record_key.to_fields[0] if record_key.related_model is not None else ""
            data_record = table_model.objects.get(**{record_key.name + keyword_middle_part + "__iexact":
                                                  request.session['selected_record']})

            data_from_database = create_fields_list(data_record)
            warn_about_changes = ConfirmationStatus.NO_MESSAGE
            changes_list = []
            for fieldTuple in data_from_database:
                field_name, _, field_trait_int, value_from_database = fieldTuple

                add_to_changes_list = False
                if field_trait_int == -1 and value_from_database != request.POST[field_name] and \
                   (field_name != "password" or len(request.POST['password']) > 4):
                    setattr(data_record, field_name, request.POST[field_name])
                    changes_list.append((field_name, getattr(data_record, field_name)))
                    add_to_changes_list = True
                elif field_trait_int == 0 and request.POST.get(f'clear-{field_name}', "No") == "Yes":
                    getattr(data_record, field_name).delete(False)
                    changes_list.append((field_name, ""))
                    add_to_changes_list = True

                if add_to_changes_list:
                    warn_about_changes = ConfirmationStatus.EDITED

            request.session['changes_list'] = changes_list
            request.session['fields_list'] = create_fields_list(data_record)

            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "primary_key_values": request.session['primary_key_values'],
                                                         "table_selected": True,
                                                         "allow_deletion": request.session['fields_list'][0][2],
                                                         "selected_record": request.session['selected_record'],
                                                         "table_model": request.session["selected_table"],
                                                         "fields_list": request.session['fields_list'],
                                                         "changes_list": request.session['changes_list'],
                                                         "ask_for_confirmation": warn_about_changes.name})

        elif "selected-record" in request.POST or "cancel-changes" in request.POST:  # Record to be edited from table has been selected
            if "selected-record" in request.POST:
                request.session['selected_record'] = str(request.POST['selected-record'])
                keyword_middle_part = "__" + record_key.to_fields[0] if record_key.related_model is not None else ""

                data_record = table_model.objects.get(**{record_key.name + keyword_middle_part + "__iexact":
                                                         request.POST['selected-record']})

                request.session['fields_list'] = create_fields_list(data_record)

            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "primary_key_values": request.session['primary_key_values'],
                                                         "selected_record": request.session['selected_record'],
                                                         "table_selected": True,
                                                         "allow_deletion": request.session['fields_list'][0][2],
                                                         "table_model": request.session["selected_table"],
                                                         "fields_list": request.session['fields_list'],
                                                         "ask_for_confirmation": ConfirmationStatus.NO_MESSAGE.name})
        else:  # Table to edit has been selected
            request.session['selected_table'] = request.POST['selected-table']

            primary_key_values = []
            for record in view_from_database(table_model):
                if isinstance(record_key, models.ForeignKey):
                    data_holder = getattr(record, record_key.name)
                    fk_field = table_meta.get_field(record_key.name).to_fields[0]
                    actual_value = getattr(data_holder, fk_field)
                else:
                    actual_value = record.pk
                primary_key_values.append(str(actual_value))

            request.session['primary_key_values'] = primary_key_values
            return render(request, "EditDatabase.html", {"login": request.session['login'],
                                                         "role": request.session['role'],
                                                         "tables": [model.__name__ for model
                                                                    in apps.get_app_config("App").get_models()],
                                                         "primary_key_values": primary_key_values,
                                                         "table_selected": request.session.get("selected_table", None) is not None,
                                                         "table_model": request.session["selected_table"],
                                                         "selected_record": "",
                                                         "ask_for_confirmation": ConfirmationStatus.NO_MESSAGE.name})


def mapping(s):
    if s == 'Medical':
        return 0
    if s == 'Memorial':
        return 1
    if s == 'Emergency':
        return 2
    if s == 'Education':
        return 3
    if s == 'Other':
        return 4

class ExplorePage(View):
    def get(self, request):
        return render(request, "Explore.html" )

    def post(self, request):
        if request.method == 'POST' and "filter" in request.POST:
            types = [int(request.POST.get('med', 0)), int(request.POST.get('mem', 0)), int(request.POST.get('emer', 0)),
                     int(request.POST.get('edu', 0)), int(request.POST.get('other', 0))]
            campaigns = Campaign.objects.annotate(subs=Count('subscribers'))
            campaigns_copy = Campaign.objects.all()
            camps = []
            if int(request.POST.get('new_old', 0)) == 1:
                campaigns = campaigns.order_by('-datetime_started').values()
            elif int(request.POST.get('old_new', 0)) == 1:
                campaigns = campaigns.order_by('datetime_started').values()
            elif int(request.POST.get('popular', 0)) == 1:
                campaigns = campaigns.order_by('subs').values()

            for c in campaigns:
                if types[mapping(c['campaign_type'])] == 1:
                    cd = c['campaign_code']
                    for i in campaigns_copy:
                        if i.campaign_code == cd:
                            camps.append(i)

            print(camps)
            return render(request, "Explore.html", {'login': request.session['login'], 'campaigns': camps,
                                                    "role": request.session['role']})

        if request.method == 'POST' and "start_search" in request.POST:
            search = request.POST['search']
            newList = []
            try:
                search = int(search)
                newList = Campaign.objects.filter(campaign_code__exact=search)

            except:
                search = search.lower()
                tempList = Campaign.objects.all()
                for c in tempList:
                    if str(c.campaign_description).lower().__contains__(search) or str(c.campaign_name).lower().__contains__(search):
                        newList.append(c)

            return render(request, "Explore.html", {'campaigns': newList, "login": request.session['login'],
                                                   "role": request.session['role']})

        
        
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
        return render(request, "Search.html", {'campaigns': [], "login": request.session['login'],
                                               "role": request.session['role']})


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


