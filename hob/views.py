from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from hob.forms import RegistrationForm, AuthenticationForm

from hob.models import Hobby

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    context = { 
        'title': "Home", 
    }
    return render(request, 'hob/index.html', context)

def profile(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    context = { 
        'title': "Profile", 
    }
    return render(request, 'hob/profile.html', context)

def hobbies(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    context = { 
        'title': "Hobbies", 
        'hobbies': hobbies, 
    }
    return render(request, 'hob/hobbies.html', context)

def similar_hobbies(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    context = { 
        'title': "Similar Hobbies",
    }
    return render(request, 'hob/hobbies/similar_hobbies.html', context)

def register(request):
    context = {
        'title': "Register",
    }

    if request.user.is_authenticated:
        return redirect('home')

    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            acc = form.save()
            login(request, acc, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        else:
            context['reg_form'] = form
    else:
        form= RegistrationForm()
        context['reg_form'] = form

    return render(request, 'account/register.html', context)

def loginUser(request):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect('home')
    
    if request.POST: 
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()

    context['login_form'] = form
    return render(request, 'account/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')
