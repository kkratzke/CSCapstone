from django.db import models

# Create your models here.
ROLES = (
    ("Admin", "Admin"),
    ("User", "User"),
)

TYPES = (
    ("Medical", "Medical"),
    ("Memorial", "Memorial"),
    ("Emergency", "Emergency"),
    ("Education", "Education"),
    ("Other", "Other"),
)

STATUS = (
    ("On going", "On going"),
    ("Suspended", "Suspended"),
    ("Canceled", "Canceled"),
    ("End", "End"),
)


class MyUser(models.Model):
    username = models.CharField(max_length=20, default=None)
    last_name = models.CharField(max_length=20, default=None)
    first_name = models.CharField(max_length=20, default=None)
    email = models.CharField(max_length=30, default=None)
    role = models.CharField(max_length=10, choices=ROLES, default="User")
    password = models.CharField(max_length=64, default=None)

    def str(self):
        return self.username


class Campaign(models.Model):
    campaignName = models.CharField(max_length=150)
    type = models.CharField(max_length=15, choices=TYPES, default="Other")
    campaignCode = models.IntegerField(default=None)
    status = models.CharField(max_length=15, choices=STATUS, default="On going")
    owner = models.CharField(max_length=20)
    image = models.FileField(upload_to='campaign', default=None)

    def str(self):
        return self.campaignName


class Img(models.Model):
    img_url = models.ImageField(upload_to='users', default=None)
