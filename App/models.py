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
    username = models.CharField(max_length=20, default=None, unique=True)
    last_name = models.CharField(max_length=20, default=None)
    first_name = models.CharField(max_length=20, default=None)
    email = models.CharField(max_length=30, default=None)
    role = models.CharField(max_length=10, choices=ROLES, default="User")
    password = models.CharField(max_length=64, default=None)

    def str(self):
        return self.username


class Campaign(models.Model):
    campaign_code = models.PositiveBigIntegerField(primary_key=True, db_column="campaign_code")
    campaign_name = models.CharField(max_length=150)
    campaign_type = models.CharField(max_length=15, choices=TYPES, default="Other")
    campaign_status = models.CharField(max_length=15, choices=STATUS, default="On going")
    campaign_owner = models.ForeignKey(to=MyUser, to_field='username', on_delete=models.CASCADE,
                                       db_column="campaign_owner")
    campaign_description = models.CharField(max_length=500, blank=True)

    def str(self):
        return self.campaignName

