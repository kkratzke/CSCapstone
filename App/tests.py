from django.test import TestCase, Client
from App.functions import *
from App.models import *


# Create your tests here.
class TestLoginFunction(TestCase):
    def setUp(self):
        self.connector = db_connection()
        self.user1 = MyUser.objects.create(email='user1@uwm.edu', password='password1', first_name='joe',
                                           last_name='johnson', role='User', username='user1')
        self.user1.save()

        self.user2 = MyUser.objects.create(email='user2@uwm.edu', password='password2', first_name='joe',
                                           last_name='johnson', role='User', username='user2')
        self.user2.save()

        password = 'password3'

        self.user3 = MyUser.objects.create(email='user3@uwm.edu',
                                           password=hashlib.sha256(password.encode("utf-8")).hexdigest(),
                                           first_name='joe', last_name='johnson', role='User', username='user3')
        self.user3.save()

    def test_login_no_username_no_password(self):
        self.assertFalse(login('user4', 'pass'))

    def test_login_no_username_existing_password(self):
        self.assertFalse(login('user5', 'password1'))

    def test_login_username_no_password(self):
        self.assertFalse(login('user1', 'password5'))

    def test_login_username_existing_password(self):
        self.assertFalse(login('user2', 'password3'))

    def test_login_success(self):
        self.assertTrue(login('user3', 'password3'))

    def tearDown(self):
        self.connector.close()


class TestDBConnection(TestCase):
    def setUp(self):
        self.connector = db_connection()

    def test_connect_to_db(self):
        self.assertTrue(self.connector.is_connected())

    def test_add_user(self):
        new_user = MyUser(username='testUser1',
                          first_name='John',
                          last_name='Smith',
                          email='jsmith@test.com',
                          role=ROLES[1][0],
                          password=hashlib.sha256('testerNum1'.encode("utf-8")).hexdigest())
        new_user.save()
        self.assertTrue(MyUser.objects.filter(username='testUser1'))

    def tearDown(self):
        self.connector.close()


class UploadPictures(TestCase):
    def setUp(self):
        self.connector = db_connection()
        self.user1 = MyUser.objects.create(email='user1@uwm.edu', password='password1', first_name='joe',
                                           last_name='johnson', role='User', username='user1')
        self.user1.save()
        self.testCampaign = Campaign(campaign_code=1, campaign_name="TestCampaign", campaign_owner=self.user1)
        self.testCampaign.save()

    def test_upload_user_pic(self):
        image_to_upload = "App/testPics/testUserPic1.jpeg"
        pic_pkg = UserPictures(username=self.user1, user_pic=image_to_upload)
        pic_pkg.save()
        self.assertTrue(UserPictures.objects.filter(username=self.user1))

    def test_upload_bg_pic(self):
        image_to_upload = "App/testPics/testBGPic.jpeg"
        pic_pkg = CampaignPictures(campaign_code=self.testCampaign, bg_pic=image_to_upload)
        pic_pkg.save()
        self.assertTrue(CampaignPictures.objects.get(campaign_code=self.testCampaign).bg_pic is not None)

    def test_upload_campaign_pic(self):
        image_to_upload = "App/testPics/testCampaignPic.png"
        pic_pkg = CampaignPictures(campaign_code=self.testCampaign, campaign_pic=image_to_upload)
        pic_pkg.save()
        self.assertTrue(CampaignPictures.objects.filter(campaign_code=self.testCampaign))

    # def test_upload_non_image(self):
    #     not_an_image = "App/Templates/Homescreen.html"
    #     pic_pkg = UserPictures(id=self.user1, user_pic=not_an_image)
    #     pic_pkg.save()
    #     self.assertTrue(UserPictures.objects.get(id=self.user1).user_pic is None)

    # def test_upload_pic_not_registered(self):
    #     non_user = MyUser(username='user2')
    #     image_to_upload = "App/testPics/testUserPic2.jpeg"
    #     pic_pkg = UserPictures(id=non_user, user_pic=image_to_upload)
    #     pic_pkg.save()
    #     self.assertFalse(UserPictures.objects.filter(id=non_user))

    def tearDown(self):
        self.connector.close()

