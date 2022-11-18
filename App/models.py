from django.db import models

from CSCapstone.settings import AWS_STORAGE_BUCKET_NAME
from django.core.validators import validate_image_file_extension

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

    def delete_user(self, user_to_delete: "MyUser"):
        if self.permission_to_delete_user(user_to_delete):
            try:
                user_to_delete.delete()
            except MyUser.DoesNotExist:
                return f"User ID # {user_to_delete.id} does not exist"
            else:
                return f"User account for {user_to_delete.username} has been deleted"
        else:
            return f"You don't have permission to delete this user's account"

    def delete_user_pic(self, deletee: "MyUser"):
        if self.permission_to_delete_user(deletee):
            UserPictures.objects.get(id=deletee).user_pic.delete()
            return f"The user picture for {deletee.username} has been deleted"
        else:
            return "You don't have permission to delete this user's picture"

    def delete_profile_banner(self, deletee: "MyUser"):
        if self.permission_to_delete_user(deletee):
            UserPictures.objects.get(id=deletee).profile_banner.delete()
            return f"The profile banner for {deletee.username} has been deleted"
        else:
            return "You don't have permission to delete this user's profile banner"

    def delete_campaign(self, code_number):
        if self.permission_to_delete_campaign(code_number):
            try:
                campaign_to_delete = Campaign.objects.get(campaign_code=code_number)
            except Campaign.DoesNotExist:
                return f"Campaign {code_number} doesn't exist"
            else:
                campaign_to_delete.delete()
                return f"Campaign \"{campaign_to_delete.campaign_name}\" has been deleted"
        else:
            return "You don't have permission to delete this campaign"

    def permission_to_delete_user(self, user_to_delete: "MyUser") -> bool:
        return (self.role == ROLES[0][0] and user_to_delete.role != ROLES[0][0]) or \
               (self.role == ROLES[1][0] and user_to_delete == self)

    def permission_to_delete_campaign(self, code_of_campaign: int) -> bool:
        try:
            campaign_to_delete = Campaign.objects.get(campaign_code=code_of_campaign)
        except Campaign.DoesNotExist:
            return False
        else:
            return self.role == ROLES[0][0] or campaign_to_delete.campaign_owner == self


class Campaign(models.Model):
    campaign_code = models.PositiveBigIntegerField(primary_key=True, db_column="campaign_code")
    campaign_name = models.CharField(max_length=150)
    campaign_type = models.CharField(max_length=15, choices=TYPES, default="Other")
    campaign_status = models.CharField(max_length=15, choices=STATUS, default="On going")
    campaign_owner = models.ForeignKey(to=MyUser, to_field='username', on_delete=models.CASCADE,
                                       db_column="campaign_owner")
    campaign_description = models.CharField(max_length=500, blank=True)
    subscribers = models.ManyToManyField(MyUser, related_name="subscribers")

    subscribers = models.ManyToManyField(MyUser, related_name="subscribers")

    def str(self):
        return self.campaign_name

    def delete_campaign_pic(self, deleter: MyUser):
        if deleter.permission_to_delete_campaign(self.campaign_code):
            CampaignPictures.objects.get(campaign_code=self).campaign_pic.delete()
            return f"The picture for the campaign \"{self.campaign_name}\" has been deleted"
        else:
            return "You don't have permission to delete this campaign picture"

    def delete_bg_pic(self, deleter: MyUser):
        if deleter.permission_to_delete_campaign(self.campaign_code):
            CampaignPictures.objects.get(campaign_code=self).bg_pic.delete()
            return f"The background for the campaign \"{self.campaign_name}\" has been deleted"
        else:
            return "You don't have the permission to delete this campaign's background"


class UserPictures(models.Model):
    username = models.OneToOneField(to=MyUser, to_field='username', on_delete=models.CASCADE, primary_key=True,
                                    db_column="username", default=None)
    user_pic = models.ImageField(upload_to="user_pic/", default=None, validators=[validate_image_file_extension])
    profile_banner = models.ImageField(upload_to="profile_banner/", default=None,
                                       validators=[validate_image_file_extension])


# Pictures used for campaign pages
class CampaignPictures(models.Model):
    campaign_code = models.OneToOneField(Campaign, on_delete=models.CASCADE, primary_key=True, db_column="campaign_code")
    bg_pic = models.ImageField(upload_to="backgrounds/", default=None, validators=[validate_image_file_extension])
    campaign_pic = models.ImageField(upload_to="campaign_pic/",
                                     default=None, validators=[validate_image_file_extension])
