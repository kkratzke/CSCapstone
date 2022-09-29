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

def create_account(uname, email, first, last, pass1, pass2):
    message = ""
    foundUser = True
    try:
        m = MyUser.objects.get(username__iexact=uname)
    except:
        foundUser = False

    if foundUser:
        message = "Username already taken"

    if pass1 != pass2:
        message = "Passwords do not match"

    if message == "":
        newUser = MyUser(username=uname, password=hashlib.sha256(pass1.encode('utf-8')).hexdigest(),
                   first_name=first, last_name=last, email=email)
        newUser.save()

    return message