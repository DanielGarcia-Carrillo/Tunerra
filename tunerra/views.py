from django.template import RequestContext
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

def index(request):
    return render(request,'index.html', RequestContext(request))

class SignupForm(forms.Form):
    # Putting these attrs here suck
    username = forms.CharField(max_length=30, min_length=5,widget=forms.TextInput(attrs={'required':True,'placeholder':'Username'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True,'placeholder':'Email',type:'email'}))
    password = forms.CharField(max_length=50, min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))

class LoginForm(forms.Form):
    user_info = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username/Email'}))
    password = forms.CharField(max_length=50, min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))

def welcome(request):
   return render(request, 'welcome.html', RequestContext(request))

def login_signup(request):
    if request.method == 'POST':
        # Hacky way to tell which form is being POSTed
        signup_form = SignupForm(request.POST)
        login_form = LoginForm(request.POST)
        if signup_form.is_valid():
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
            return render(request, 'accounts.html', {'signup_form':signup_form, 'login_form':login_form})
    else:
        return render(request, 'accounts.html', {
            'signup_form': SignupForm(auto_id='id_signup_%s'),
            'login_form':LoginForm(auto_id='id_login_%s')
        })
