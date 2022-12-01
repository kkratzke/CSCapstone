from itertools import chain

#import mysql.connector
from django.core import serializers

from App.models import *
from CSCapstone.settings import AWS_STORAGE_BUCKET_NAME, DATABASES
import hashlib
from django.apps import apps


def login(uname, password):
    noSuchUser = False
    badPass = False
    try:
        m = MyUser.objects.get(username__iexact=uname)
        if m.password != hashlib.sha256(password.encode('utf-8')).hexdigest():
            badPass = True
    except:
        noSuchUser = True

    if (noSuchUser or badPass):
        return False
    else:
        return True


def valid_email_format(email):
    if "@" not in email:
        return "Email does not contain @."
    elif ' ' in email:
        return "Email should not contain a space."
    else:
        return "Valid"


def create_account(uname, email, first, last, pass1, pass2):
    reload_content = [uname, email, first, last, pass1, pass2]
    message = ""
    foundUser = True
    try:
        m = MyUser.objects.get(username__iexact=uname)
    except:
        foundUser = False

    valid_email = valid_email_format(email)

    if foundUser:
        message = "Username already taken"
        reload_content[0] = ''

    elif (valid_email != "Valid"):
        message = valid_email
        reload_content[1] = ''

    elif pass1 != pass2:
        message = "Passwords do not match"
        reload_content[4] = reload_content[5] = ''

    elif message == "":
        newUser = MyUser(username=uname, password=hashlib.sha256(pass1.encode('utf-8')).hexdigest(),
                         first_name=first, last_name=last, email=email)
        newUser.save()
        UserPictures(username=newUser).save()

    return (message, reload_content)


def edit_profile(email, first, last, pass1, pass2, owner):
    message = ""
    user = MyUser.objects.get(username__iexact=owner)

    if valid_email_format(email) == "Valid":
        emailIn = email
    else:
        message = valid_email_format(email)

    firstIn = first

    lastIn = last

    if pass1 != pass2:
        message = "Passwords do not match"

    passIn = hashlib.sha256(pass1.encode("utf-8")).hexdigest()

    if message == "":
        user.email = emailIn
        user.first_name = firstIn
        user.last_name = lastIn
        if (pass1 == pass2 and pass1 != ""):
            user.password = passIn
        user.save()

    return message


def getNewName(file_type, name):
    new_name = str(name) + '.png'

    return new_name


def db_connection():
    db_settings = DATABASES['default']
    return mysql.connector.connect(host=db_settings['HOST'],
                                   port=db_settings['PORT'],
                                   database=db_settings['NAME'],
                                   username=db_settings['USER'],
                                   password=db_settings['PASSWORD'])


def view_from_database(table_model: "App.models", **kwargs):
    if len(kwargs) == 0:
        return table_model.objects.all()
    else:
        return table_model.objects.filter(**kwargs)


def add_test_user(username: str, role: str, campaignCode: int):
    user_to_return = MyUser(username=username, first_name="John", last_name="Doe",
                            email="jdoe" + str(campaignCode) + "@unknown.com", password="jsbak39", role=role)
    user_to_return.save()
    campaign_to_return = Campaign(campaign_code=campaignCode, campaign_name="Test Campaign " + str(campaignCode),
                                  campaign_owner=user_to_return)
    campaign_to_return.save()
    UserPictures(id=user_to_return, user_pic='App/static/images/profile-user.png',
                 profile_banner='App/static/images/community-1.jpg').save()
    CampaignPictures(campaign_code=campaign_to_return, campaign_pic="App/static/images/media/campaign_pic/10008.png",
                     bg_pic='App/static/images/community-1.jpg').save()
    return {"user": user_to_return, "campaign": campaign_to_return}


def from_str_to_table_model(a_string: str) -> "App.models" or None:
    try:
        model_type_to_return = apps.get_app_config("App").get_model(a_string)
    except LookupError:
        return None
    else:
        return model_type_to_return


def create_fields_list(instance) -> list:
    fields_list = []
    table_meta = instance._meta
    instance_dist = to_dict(instance)

    for field in [f.name for f in table_meta.fields]:
        choices_for_field = table_meta.get_field(field).choices
        field_to_check = table_meta.get_field(field)
        # 2 if primary key doesn't reference another model, 1 if foreign key or primary key that does reference
        # another model, 0 if ImageField, -1 otherwise
        is_pk_or_fk = 2 if table_meta.pk.name == field and table_meta.pk.related_model is None else \
            1 if isinstance(field_to_check, models.ForeignKey) or field_to_check.editable == False else \
            0 if isinstance(field_to_check, models.ImageField) else \
            -1

        if choices_for_field is not None:
            choices_for_field = [t[0] for t in choices_for_field]

        if isinstance(field_to_check, models.DecimalField) or isinstance(field_to_check, models.DateTimeField):
            instance_dist[field] = str(instance_dist[field])

        fields_list.append((field, choices_for_field, is_pk_or_fk, instance_dist[field]))

    return fields_list


def to_dict(instance):
    opts = instance._meta
    serialized_data = serializers.serialize("python", [instance])[0]
    instance_dict = {opts.pk.name: serialized_data['pk']}
    instance_dict.update(serialized_data['fields'])
    return instance_dict


def remove_record(deleter: MyUser, deletee: "App.models") -> str:
    if isinstance(deletee, MyUser):
        return deleter.delete_user(deletee)
    elif isinstance(deletee, Campaign):
        return deleter.delete_campaign(deletee)
    else:
        return "No method exists to delete the given deletee"


def clear_field(deleter: MyUser, deletee: "App.models", field_name: str) -> str:
    if field_name == "user_pic":
        return deleter.delete_user_pic(deletee.username)
    elif field_name == "profile_banner":
        return deleter.delete_profile_banner(deletee.username)
    elif field_name == "campaign pic":
        return deletee.campaign_code.delete_campaign_pic(deleter)
    elif field_name == "bg_pic":
        return deletee.campaign_code.delete_bg_pic(deleter)
    else:
        return f"No method exists to clear {field_name} for the given deletee"

