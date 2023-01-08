import json
from django.contrib.auth.models import User
from django.test import TestCase

from hob.models import UserAccount
from .models import UserAccount, Hobby
from datetime import datetime
from django.urls import reverse
from django.test import Client
# Create your tests here.


class SignupTestCase(TestCase):
    def setUp(self):
        self.username = "tester",
        self.password = "123Qwerty123",
        self.email = "test1232@example.com",
        self.firstname = "usere",
        self.lastname = "egyui",
        self.date_of_birth = datetime.now().strftime("%Y-%m-%d"),
        self.city = "London",

        self.data = {
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
            'first_name': self.firstname, 
            'last_name': self.lastname,
            "date_of_birth": self.date_of_birth,
            "city": self.city,
        }


    def test_register_success(self):
        '''checks whether the user can be successfully created'''

        c = Client()
        r = c.post(reverse("register"), data = self.data)
        self.assertEqual(r.status_code, 302)

    
    def test_register_without_email(self):
        '''checks whether the user supplied an email address'''

        d = self.data
        d["email"] = ""
        response = self.client.post(reverse('register'), data = d)
        self.assertEqual(response.status_code, 400)

    def test_register_unmatching_password(self):
        '''checks whether the user can be successfully created'''
        
        data = self.data
        data["password2"] = "E239rfQ6"
        response = self.client.post(reverse('register'), data = data)
        self.assertEqual(response.status_code, 400)

class LoginTestCase(TestCase):
    def setUp(self):
        self.email = "dummy@example.com",
        self.password = "Password",
        self.data = {
            "email": self.email,
            "password": self.password
        },
        self.login_url = reverse('login')
        user = UserAccount.objects.create(email = self.email, first_name = "test", last_name = "case", date_of_birth = datetime.now())
        user.set_password("Password")
        user.save()

    def test_user_creation(self):
        '''checks if the user is created from the setup'''
        count = UserAccount.objects.all().count()
        self.assertEqual(count, 1)
    

    def test_login_success(self):
        '''checks whether user can successfully login'''

        user = UserAccount.objects.filter(email = self.email).first()
        user.save()

        c = Client()
        login = c.login(username = self.email, password = "Password")
        self.assertTrue(login)

    def test_login_invalid_email(self):
        '''checks whether a user if user cant login when an invalid email is inputted'''

        c = Client()
        login = c.login(username = "abv", password = "Password")
        self.assertFalse(login)

    
    def test_login_with_wrong_password(self):
        '''checks login when given an incorrect password'''
        c = Client()
        login = c.login(username = self.email, password = "123")
        self.assertFalse(login)


class TestProfile(TestCase):

    def setUp(self):
        self.email = "dummy@example.com"
        self.firstname = "test"
        self.lastname = "case"
        self.date_of_birth = datetime.now().strftime("%Y-%m-%d")

        self.profile_url = reverse('profile')
        self.login_url = reverse("login")
        self.update_dob = reverse("update-user-details")

        #create a hobby
        hobby = Hobby.objects.create(name = "gym", description = "workout")
        hobby.save()

        #create a user
        user = UserAccount.objects.create(email = "dummy@example.com", first_name = "test", last_name = "case", date_of_birth = self.date_of_birth)
        user.set_password("Password")
        user.save()
        user.hobbies.add(hobby)
        hobby.refresh_from_db()

    def test_edit_date_of_birth_from_profile(self):
        '''checks whether date of birth updates'''

        user = UserAccount.objects.get(pk = 1)
        user.save()
        c = Client()
        response = c.post(self.login_url, data = {'email': 'dummy@example.com', 'password': "Password"}, follow=True)
        r = c.get(self.profile_url, follow=True)
        new_dob = str(datetime.fromtimestamp(1420113331).strftime("%Y-%m-%d"))
       
        response = c.put(self.update_dob, data = json.dumps({
                            'firstname': self.firstname,
                            'lastname': self.lastname,
                            'username': "test",
                            'city': "London",
                            'email': "dummy@example.com",
                            'dob': new_dob,
        }))
        user.refresh_from_db()
        
        self.assertEquals(user.date_of_birth.strftime("%Y-%m-%d"), new_dob)
        

    def test_edit_hobby_from_profile(self):
    
        user = UserAccount.objects.get(pk = 1)
        user.save()
        c = Client()
        response = c.post(self.login_url, data = {'email': 'dummy@example.com', 'password': "Password"}, follow=True)
        delete_url = reverse("remove-user-hobby", kwargs={"id": user.id})
        r = c.get(self.profile_url, follow=True)
        
        del_response = c.delete(delete_url)
        self.assertFalse(user.hobbies.all().exists())