from django.db import models

# Create your models here.
ROLES = (
    ("Admin", "Admin"),
    ("User", "User")
)


class MyUser(models.Model):
    username = models.CharField(max_length=20, default=None)
    last_name = models.CharField(max_length=20, default=None)
    first_name = models.CharField(max_length=20, default=None)
    email = models.CharField(max_length=30, default=None)
    password = models.CharField(max_length=64, default=None)
    role = models.CharField(max_length=10, choices=ROLES)

    def str(self):
        return self.username


class Campaign(models.Model):
    campaignName = models.CharField(max_length=20)
    campaignCode = models.CharField(max_length=20)
    owner = models.CharField(max_length=20)

    def str(self):
        return self.campaignName

