from itertools import chain

import mysql.connector
from App.models import *
from CSCapstone.settings import AWS_STORAGE_BUCKET_NAME, DATABASES
import hashlib
import boto3
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

    elif(valid_email != "Valid"):
        message = valid_email
        reload_content[1] = ''

    elif pass1 != pass2:
        message = "Passwords do not match"
        reload_content[4] = reload_content[5] = ''

    elif message == "":
        newUser = MyUser(username=uname, password=hashlib.sha256(pass1.encode('utf-8')).hexdigest(),
                         first_name=first, last_name=last, email=email)
        newUser.save()
        UserPictures(id=newUser).save()

    return (message, reload_content)


def edit_profile(email, first, last, pass1, pass2, owner, userPic, userBanner):
    message = ""
    user = MyUser.objects.get(username__iexact=owner)
    user_media = UserPictures.objects.get(id=user)

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
        user.password = passIn
        user.save()
        user_media.user_pic = userPic
        user_media.user_pic.name = user_media.user_pic.name
        user_media.profile_banner = userBanner
        user_media.save()
        # pic_name = user_media.user_pic.name
        # banner_name = user_media.profile_banner.name
        # if pic_name != "" or banner_name != "":
        #     session = boto3.Session(
        #         aws_access_key_id='AWS_ACCESS_KEY_ID',
        #         aws_secret_access_key='AWS_SECRET_ACCESS_KEY',
        #     )
        #     s3 = session.resource("s3")
        #     if pic_name != "":
        #         user_media.user_pic.name = AWS_STORAGE_BUCKET_NAME + "user_pic/" + pic_name
        #         s3.meta.client.upload_file(Filename=pic_name, Bucket=AWS_STORAGE_BUCKET_NAME, Key="user_pic/" + pic_name)
        #         # s3.Bucket(AWS_STORAGE_BUCKET_NAME).upload_file(pic_name, "user_pic/" + pic_name)
        #     if banner_name != "":
        #         user_media.profile_banner.name = AWS_STORAGE_BUCKET_NAME + "profile_banner/" + banner_name
        #         s3.meta.client.upload_file(Filename=pic_name, Bucket=AWS_STORAGE_BUCKET_NAME,
        #                                    Key="profile_banner/" + banner_name)
        #         # s3.Bucket(AWS_STORAGE_BUCKET_NAME).upload_file(banner_name, "profile_banner/" + banner_name)
        #     user_media.save()

    return message


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


def create_fields_list(db_table: "App.models") -> list:
    fields_list = []
    table_meta = db_table._meta

    for field in [f.name for f in table_meta.fields]:
        choices_for_field = table_meta.get_field(field).choices
        if choices_for_field is None:
            fields_list.append((field, None))
        else:
            choices_for_field = [t[0] for t in choices_for_field]
            fields_list.append((field, choices_for_field))

    return fields_list


def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data