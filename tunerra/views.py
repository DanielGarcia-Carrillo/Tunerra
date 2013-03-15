from django.template import RequestContext
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from tunerra.models import *

def index(request):
    if request.user.is_authenticated():
        # TODO send to profile page, also figure out their name
        return render(request, 'welcome.html', RequestContext(request))
    else:
        # Treat them as anonymous user
        return render(request,'index.html', RequestContext(request))

def welcome(request):
   return render(request, 'welcome.html', RequestContext(request))

def logout_user(request):
    # Logs out user through auth system
    logout(request)
    return HttpResponseRedirect('/')

def login_signup(request):
    if request.method == 'POST':
        if request.POST.get('form-name') == 'signup':
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                # SELECT * FROM SiteUser WHERE username = ?:  signup_form.cleaned_data['username']
                existing_user = User.objects.filter(username=signup_form.cleaned_data['username'])
                if not existing_user:
                    # INSERT INTO User (username, email, password) VALUES (?,?,?): username, email, password
                    new_user = User.objects.create_user(
                        username=signup_form.cleaned_data['username'],
                        email=signup_form.cleaned_data['email'],
                        password=signup_form.cleaned_data['password']
                    )
                    return HttpResponseRedirect('/accounts/welcome')
            # Returns current signup_form as env variable so that form errors will show up to user
            return render(request, 'accounts.html', {
                'signup_form':signup_form,
                'login_form':LoginForm()
            })
        elif request.POST.get('form-name') == 'login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = authenticate(username=login_form.cleaned_data['username'], password=login_form.cleaned_data['password'])
                if user is None:
                    # Return error that something is wrong
                    return HttpResponse()
                else:
                    login(request, user)
                    # Send to profile TODO don't know url to redirect
                    return HttpResponse()
            else:
                # Returns current login_form so that the login form errors will show up to user
                return render(request, 'accounts.html', {
                    'signup_form':SignupForm(),
                    'login_form':login_form
                })
    else:
        return render(request, 'accounts.html', {
            'signup_form': SignupForm(),
            'login_form': LoginForm()
        })

def search(request):
    # TODO currently just sends to search page, should also populate with results
    return render(request, 'results.html', RequestContext(request))

# TODO actually do something useful
def user_profile(request):
    return render(request, 'base.html', RequestContext(request))

class SignupForm(forms.Form):
    # Putting these attrs here suck
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True,'placeholder':'Email'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))
