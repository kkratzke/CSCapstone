import mysql.connector

import App
from App.models import *
from CSCapstone.settings import AWS_STORAGE_BUCKET_NAME, DATABASES
import hashlib
import boto3

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


def delete_user(id_number):
    try:
        user_to_delete = MyUser.objects.get(id=id_number)
    except MyUser.DoesNotExist:
        return f"User ID # {id_number} does not exist"
    else:
        user_to_delete.delete()
        return f"User account for {user_to_delete.username} has been deleted"


def delete_campaign(code_number):
    try:
        campaign_to_delete = Campaign.objects.get(campaign_code=code_number)
    except Campaign.DoesNotExist:
        return f"Campaign {code_number} doesn't exist"
    else:
        campaign_to_delete.delete()
        return f"Campaign \"{campaign_to_delete.campaign_name}\" has been deleted"


def delete_campaign_pic(code_number):
    CampaignPictures.objects.get(campaign_code__campaign_code=code_number).campaign_pic.delete()


def delete_bg_pic(code_number):
    CampaignPictures.objects.get(campaign_code__campaign_code=code_number).bg_pic.delete()


def delete_user_pic(id_number):
    UserPictures.objects.get(id_id=id_number).user_pic.delete()


def delete_profile_banner(id_number):
    UserPictures.objects.get(id_id=id_number).profile_banner.delete()


def view_from_database(table_model: App.models, **kwargs):
    if len(kwargs) == 0:
        return table_model.objects.all()
    else:
        return table_model.objects.filter(**kwargs)


