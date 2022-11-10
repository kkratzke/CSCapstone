from .views import *
import hashlib


def login(uname, password):
    noSuchUser = False
    badPass = False
    try:
        m = MyUser.objects.get(username__iexact=uname)
        if m.password != hashlib.sha256(password.encode("utf-8")).hexdigest():
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
        if(pass1 == pass2 and pass1 != ""):
            user.password = passIn
        user.save()

    return message

def getNewName(file_type, name):

    new_name = str(name) + '.png'

    return new_name
