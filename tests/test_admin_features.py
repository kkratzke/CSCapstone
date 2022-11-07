from django.test import TestCase
from App.functions import *
from App.models import *
from django.db import *


class AdminDeleteFeatures(TestCase):
    def setUp(self):
        self.connector = db_connection()
        self.user1 = MyUser(username="user1", first_name="John", last_name="Doe", email="jdoe1@unknown.com",
                            password="jsbak39")
        self.user1.save()
        self.campaign1 = Campaign(campaign_code=1, campaign_name="Test Campaign 1", campaign_owner=self.user1)
        self.campaign1.save()
        UserPictures(id=self.user1, user_pic='App/static/images/profile-user.png',
                     profile_banner='App/static/images/community-1.jpg').save()
        CampaignPictures(campaign_code=self.campaign1, campaign_pic="App/static/images/media/campaign_pic/10008.png",
                         bg_pic='App/static/images/community-1.jpg').save()

    def test_delete_user(self):
        expected_message = "User account for user1 has been deleted"
        self.assertEqual(delete_user(self.user1.id), expected_message)

    def test_delete_campaign(self):
        expected_message = "Campaign \"Test Campaign 1\" has been deleted"
        self.assertEqual(delete_campaign(self.campaign1.campaign_code), expected_message)

    def test_delete_user_pic(self):
        delete_user_pic(self.user1.id)
        self.assertEqual(UserPictures.objects.get(id=self.user1).user_pic.name, "")

    def test_delete_profile_banner(self):
        delete_profile_banner(self.user1.id)
        self.assertEqual(UserPictures.objects.get(id=self.user1).profile_banner.name, "")

    def test_delete_campaign_pic(self):
        delete_campaign_pic(self.campaign1.campaign_code)
        self.assertEqual(CampaignPictures.objects.get(campaign_code=self.campaign1).campaign_pic.name, "")

    def test_delete_bg_pic(self):
        delete_bg_pic(self.campaign1.campaign_code)
        self.assertEqual(CampaignPictures.objects.get(campaign_code=self.campaign1.campaign_code).bg_pic.name, "")

    def test_delete_all_campaign_pictures_single_user(self):
        delete_campaign_pic(self.campaign1.campaign_code)
        delete_bg_pic(self.campaign1.campaign_code)
        self.assertEqual(CampaignPictures.objects.get(campaign_code=self.campaign1).campaign_pic.name, "")

    def test_delete_all_user_pictures_single_user(self):
        delete_user_pic(self.user1.id)
        delete_profile_banner(self.user1.id)
        self.assertEqual(UserPictures.objects.get(id=self.user1).profile_banner.name, "")

    def tearDown(self):
        self.connector.close()


class AdminViewFeatures(TestCase):
    def setUp(self):
        self.connector = db_connection()
        self.user1 = MyUser(username="user1", first_name="John", last_name="Doe", email="jdoe1@unknown.com",
                            password="jsbak39")
        self.user1.save()
        self.user2 = MyUser(username="user2", first_name="Jane", last_name="Doe", email="jane.doe@unknown.com",
                            password="gjnwoi2939")
        self.user2.save()
        self.campaign1 = Campaign(campaign_code=1, campaign_name="Test Campaign 1", campaign_owner=self.user1)
        self.campaign1.save()
        self.campaign2 = Campaign(campaign_code=2, campaign_name="Test Campaign 2", campaign_owner=self.user2)
        self.campaign2.save()
        UserPictures(id=self.user1, user_pic='App/static/images/profile-user.png',
                     profile_banner='App/static/images/community-1.jpg').save()
        UserPictures(id=self.user2, user_pic='App/static/images/profile-user.png',
                     profile_banner='App/static/images/community-1.jpg').save()
        CampaignPictures(campaign_code=self.campaign1, campaign_pic="App/static/images/media/campaign_pic/10008.png",
                         bg_pic='App/static/images/community-1.jpg').save()
        CampaignPictures(campaign_code=self.campaign2, campaign_pic="App/static/images/media/campaign_pic/10010.png",
                         bg_pic='App/static/images/community-1.jpg').save()

    def test_view_all_users(self):
        self.assertEqual(len(view_from_database(MyUser)), 2)

    def test_view_specific_user(self):
        self.assertEqual(len(view_from_database(MyUser, id=self.user1.id)), 1)

    def test_view_all_campaigns(self):
        self.assertEqual(len(view_from_database(Campaign)), 2)

    def test_view_specific_campaign(self):
        self.assertEqual(len(view_from_database(Campaign, campaign_code=self.campaign1.campaign_code)), 1)

    def test_view_user_pictures_table(self):
        self.assertEqual(len(view_from_database(UserPictures)), 2)

    def test_view_campaign_pictures_table(self):
        self.assertEqual(len(view_from_database(CampaignPictures)), 2)

    def tearDown(self):
        self.connector.close()

