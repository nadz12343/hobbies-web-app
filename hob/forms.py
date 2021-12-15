from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from hob.models import UserAccount

class DateInput(forms.DateInput):
    input_type='date'

class RegistrationForm(UserCreationForm):

    '''
    Custom registration form for signing up new users.
    '''

    email = forms.EmailField(max_length=100, help_text='Valid email address needed!')
    date_of_birth = forms.DateField(widget=DateInput)
    city = forms.CharField(max_length=50)

    class Meta:
        model = UserAccount
        fields = ("username", "email", "password1", "password2", "first_name", "last_name", "date_of_birth", "city")

class AuthenticationForm(forms.ModelForm):

    '''
    Custom login form for signing up new users.
    '''

    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = UserAccount
        fields = ("email", "password")

    # Checks if user credentials are valid
    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Error when logging in!")
