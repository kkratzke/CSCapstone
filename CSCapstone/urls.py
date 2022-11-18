"""CSCapstone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from App.views import Homescreen, Landing, LogIn, CreateAccount, PageJump, upload_handle, ExplorePage, campaign_view,SearchPage,SubscriptionPage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Homescreen.as_view(), name='Homescreen'),
    path('landing/', Landing.as_view(), name='Landing'),
    path('login/', LogIn.as_view(), name='LogIn'),
    path('createaccount/', CreateAccount.as_view(), name="create_account_page"),
    path('explore/', ExplorePage.as_view(), name='explore'),
    path('subscription/', SubscriptionPage.as_view(), name='subscription'),
    path('pagejump/', PageJump.as_view(), name='PageJump'),
    path('ViewCampaign/<int:slug>/', campaign_view),
    path('search/', SearchPage.as_view(), name='search')
]