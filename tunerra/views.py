from django.template import RequestContext
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

def index(request):
    return render(request,'index.html', RequestContext(request))

class SignupForm(forms.Form):
    username = forms.CharField(max_length=30, min_length=5)
    email = forms.EmailField()
    password = forms.CharField(max_length=50, min_length=8, widget=forms.PasswordInput)

class LoginForm(forms.Form):
    user_info = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50, min_length=8, widget=forms.PasswordInput)

def login_signup(request):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST)
        login_form = LoginForm(request.POST)
        if signup_form.is_valid():
            # TODO send to welcome page
            return HttpResponseRedirect('/accounts/welcome')
        elif login_form.is_valid():
            user = authenticate(username=login_form.user_info, password=login_form.password)
            if user is None:
                user = authenticate(email=login_form.user_info, password=login_form.password)
            if user is None:
                # Return error
                return HttpResponse()
            else:
                # Send to profile
                return HttpResponse()
        else:
            # TODO Indicate that something is invalid
            return render(request, 'accounts.html', RequestContext(request))
    else:
        return render(request, 'accounts.html', RequestContext(request))
