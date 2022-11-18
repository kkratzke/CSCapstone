from django.contrib import admin
from App.models import *
# Register your models here.

admin.site.register(MyUser)
admin.site.register(Campaign)
admin.site.register(UserPictures)
admin.site.register(CampaignPictures)

