from django.test import TestCase
from App.functions import *
from App.models import *


class AdminDeleteFeatures(TestCase):
    def setUp(self):
        self.connector = db_connection()
        self.user1 = add_test_user("user1", ROLES[1][0], 1)
        self.testAdmin = add_test_user("testAdmin", ROLES[0][0], 2)

    def test_delete_user(self):
        expected_message = "User account for user1 has been deleted"
        self.assertEqual(self.testAdmin['user'].delete_user(self.user1['user']), expected_message)

    def test_delete_campaign(self):
        expected_message = "Campaign \"Test Campaign 1\" has been deleted"
        self.assertEqual(self.testAdmin["user"].delete_campaign(self.user1["campaign"].campaign_code), expected_message)

    def test_delete_user_pic(self):
        expected_message = f"The user picture for {self.user1['user'].username} has been deleted"
        self.assertEqual(self.testAdmin['user'].delete_user_pic(self.user1['user']), expected_message)

    def test_delete_profile_banner(self):
        expected_message = f"The profile banner for {self.user1['user'].username} has been deleted"
        self.assertEqual(self.testAdmin['user'].delete_profile_banner(self.user1['user']), expected_message)

    def test_delete_campaign_pic(self):
        campaign_to_alter = self.user1['campaign']
        expected_message = f"The picture for the campaign \"{campaign_to_alter.campaign_name}\" has been deleted"
        self.assertEqual(campaign_to_alter.delete_campaign_pic(self.testAdmin['user']), expected_message)

    def test_delete_bg_pic(self):
        campaign_to_alter = self.user1['campaign']
        expected_message = f"The background for the campaign \"{campaign_to_alter.campaign_name}\" has been deleted"
        self.assertEqual(campaign_to_alter.delete_bg_pic(self.testAdmin['user']), expected_message)

    def tearDown(self):
        self.connector.close()


class AdminViewFeatures(TestCase):
    def setUp(self):
        self.connector = db_connection()
        self.testAdmin = add_test_user("testAdmin", ROLES[0][0], 1)
        self.user1 = add_test_user("user1", ROLES[1][0], 2)
        self.user2 = add_test_user("user2", ROLES[1][0], 3)

    def test_view_all_users(self):
        self.assertEqual(len(view_from_database(MyUser)), 3)

    def test_view_specific_user(self):
        self.assertEqual(len(view_from_database(MyUser, id=self.user1['user'].id)), 1)

    def test_view_all_campaigns(self):
        self.assertEqual(len(view_from_database(Campaign)), 3)

    def test_view_specific_campaign(self):
        self.assertEqual(len(view_from_database(Campaign, campaign_code=self.user1['campaign'].campaign_code)), 1)

    def test_view_user_pictures_table(self):
        self.assertEqual(len(view_from_database(UserPictures)), 3)

    def test_view_campaign_pictures_table(self):
        self.assertEqual(len(view_from_database(CampaignPictures)), 3)

    def tearDown(self):
        self.connector.close()

