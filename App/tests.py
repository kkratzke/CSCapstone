import mysql.connector
from django.test import TestCase, Client
from App.models import MyUser
from App.functions import *
import mysql.connector
from CSCapstone.settings import DATABASES


# Create your tests here.


class TestLoginFunction(TestCase):
    def setUp(self):
        # self.client = Client()
        self.settings = DATABASES['default']
        self.connector = mysql.connector.connect(host=self.settings['HOST'],
                                                 port=self.settings['PORT'],
                                                 database=self.settings['NAME'],
                                                 username=self.settings['USER'],
                                                 password=self.settings['PASSWORD'])
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
        self.settings = DATABASES['default']
        self.connector = mysql.connector.connect(host=self.settings['HOST'],
                                                 port=self.settings['PORT'],
                                                 database=self.settings['NAME'],
                                                 username=self.settings['USER'],
                                                 password=self.settings['PASSWORD'])

    def test_connect_to_db(self):
        self.assertTrue(self.connector.is_connected())

    # def test_add_user(self):
    #     new_user = MyUser(username='testUser1',
    #                       first_name='John',
    #                       last_name='Smith',
    #                       email='jsmith@test.com',
    #                       role=ROLES[1],
    #                       password=hashlib.sha256('testerNum1'.encode("utf-8")).hexdigest())

    def tearDown(self):
        self.connector.close()
