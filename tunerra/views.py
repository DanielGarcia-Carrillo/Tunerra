from django.template import RequestContext
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect

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
        signup = SignupForm(request.POST)
        login = LoginForm(request.POST)
        if signup.is_valid():
            # TODO send to profile/display thanks for signing up
            return HttpResponseRedirect('')
        elif login.is_valid():
            # TODO send to profile
            return HttpResponseRedirect('')
        else:
            return render(request, 'accounts.html', RequestContext(request))
    else:
        return render(request, 'accounts.html', RequestContext(request))
