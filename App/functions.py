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
    reload_content = [email, first, last, "", ""]
    message = ""

    try:
        user = MyUser(owner)
        message = user.username
        if email == "":
            emailIn = user.email
        elif valid_email_format(email) == "Valid":
            emailIn = email
        else:
            message = valid_email_format(email)
            reload_content[0] = ''

        if first == "":
            firstIn = user.first_name
        else:
            firstIn = first

        if last == "":
            lastIn = user.last_name
        else:
            lastIn = last

        if pass1 == "" and pass2 == "":
            pass2In = user.password
        elif user.password != hashlib.sha256(pass1.encode("utf-8")).hexdigest():
            message = "invalid password"

        if message == "":
            user.email = emailIn
            user.first_name = firstIn
            user.last_name = lastIn
            user.password = hashlib.sha256(pass2In.encode("utf-8")).hexdigest()
            user.save()
        else:
            return message, reload_content
    except:
        return message, reload_content

