from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from series import views
from series.models import Contact

class Authenticator():
    def __init__(self):
        self.user = None
        self.client = None

    def create_user(self):
        u = User()
        u.username = "test_user"
        u.set_password("test1")
        u.email = "test@test.com"
        u.save()
        

# class SeriesRegistrationTests(TestCase):
#     
#     def test_register(self):
#         response = self.client.get(reverse("registration_register"))
#         self.assertContains(response, "Create an account with Readsr", status_code=200)
# 
#         response = self.client.post(reverse("registration_register"), {'username': 'myname', 'first_name': 'first name', 'last_name': 'last name', 'email': 'tester@fakeemail.com', 'password': 'mypassword'})
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "We've sent an e-mail to the address you registered. Please follow the instructions inside it, and your account will be activated in no time.")
# 
#     def login_valid_user(self):
#         self.client = Client()
#         self.client.login(username="myname", password="mypassword")

class SeriesTests(TestCase):
    
    def setUp(self):
        user = User.objects.create_user('test', 'william.bert@gmail.com', 'testpassword')
        user.first_name = "Test"
        user.last_name = "User"
        user.save()        
        
    def test_usercreated(self):
        user = User.objects.get(username='test')
        self.assertEqual(user.email, "william.bert@gmail.com")
        contact = Contact.objects.get(user=user)
        self.assertEqual(contact.first_name, "Test")
        self.assertEqual(contact.last_name, "User")
 
    def test_about_page(self):
        response = self.client.get(reverse("about"))
        self.assertEquals(response.status_code, 200)
 
    def test_index_views(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
    
        self.client.get(reverse("index"), data={ "start_date": "08-15-2011", "end_date": "09-15-2011", "list_view": "True" })
