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
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True,'placeholder':'Email'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'required':True,'placeholder':'Username'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'required':True,'placeholder':'Password'}))

def welcome(request):
   return render(request, 'welcome.html', RequestContext(request))

def login_signup(request):
    if request.method == 'POST':
        if request.POST.get('form-name') == 'signup':
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                existing_user = User.objects.filter(username=signup_form.cleaned_data['username'])
                if not existing_user:
                    new_user = User.objects.create_user(
                        username=signup_form.cleaned_data['username'],
                        email=signup_form.cleaned_data['email'],
                        password=signup_form.cleaned_data['password']
                    )
                    return HttpResponseRedirect('/accounts/welcome')
            return render(request, 'accounts.html', {
                'signup_form':signup_form,
                'login_form':LoginForm()
            })
        elif request.POST.get('form-name') == 'login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = authenticate(username=login_form.cleaned_data['username'], password=login_form.cleaned_data['password'])
                if user is None:
                    # Return error
                    return HttpResponse()
                else:
                    # Send to profile
                    return HttpResponse()
            else:
                return render(request, 'accounts.html', {
                    'signup_form':SignupForm(),
                    'login_form':login_form
                })
    else:
        return render(request, 'accounts.html', {
            'signup_form': SignupForm(),
            'login_form': LoginForm()
        })
