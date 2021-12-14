from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from datetime import date


class Hobby(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.name, self.description}"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'api': reverse('remove-user-hobby', kwargs={'id': self.id})
        }

    def to_dict_id(self):
        return {
            'id': self.id,
        }

class UserAccount(AbstractUser):
    email = models.EmailField(verbose_name="email", max_length=100, unique=True)
    city = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    hobbies = models.ManyToManyField(Hobby, blank=True)
    friends = models.ManyToManyField("UserAccount", blank=True)
    #profile_picture = models.ImageField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.first_name + " " +self.last_name +" ("+self.username+")"

    def to_dictionary_full_info(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'firstname': self.first_name,
            'lastname': self.last_name,
            'dob': self.date_of_birth,
            'city': self.city,
            'hobbies': [
                hobby.to_dict()
                for hobby in self.hobbies.all()
            ],
            'friends': [
                friend.friends_dictionary()
                for friend in self.friends.all()
            ]
        }

    def to_dictionary_user_hobbies(self):
        return {
            'id': self.id,
            'hobbies': [
                hobby.to_dict_id()
                for hobby in self.hobbies.all()
            ],
        }
    
    def to_dictionary_users_hobbies(self):
        return {
            'hobbies': [
                hobby.to_dict_id()
                for hobby in self.hobbies.all()
            ],
        }

    def simple_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'city': self.city,
            'dob': self.date_of_birth,
            'api': reverse('send-request', kwargs={'id': self.id}),
        }

    def friends_dictionary(self):
        return {
            'id': self.id,
            'username': self.username,
            'firstname': self.first_name,
            'lastname': self.last_name,
            'api': reverse('manage-request', kwargs={'id': self.id}),
        }
    
    def friends_request_dictionary(self):
        return {
            'id': self.id,
            'username': self.username,
            'firstname': self.first_name,
            'lastname': self.last_name,
        }

class FriendRequest(models.Model):
    from_user = models.ForeignKey(UserAccount, related_name="sender", on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserAccount, related_name="receiver", on_delete=models.CASCADE)
    date_sent = models.DateField(default=date.today)

    def __str__(self):
        return "From "+self.from_user.username+" to "+self.to_user.username

    def requests_to_dictionary(self):
        return {
            'from': self.from_user.friends_dictionary(),
            'sent': self.date_sent,
        }
