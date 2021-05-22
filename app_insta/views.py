from django.shortcuts import render,redirect
from .models import Image, Profile, Comment, Relation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from .forms import uploadForm ,SignUpForm


# Create your views here.
@login_required(login_url='/accounts/login/')
def feed(request):
    pictures = Image.objects.all()
    return render(request, 'index.html',{'pictures':pictures})

@login_required(login_url='/accounts/login/')
def profile(request):
    return render(request, 'profile.html') 

def login(request):
    return render (request, 'registration/login.html')  

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user=form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('app_insta:profile')
    else:
        form = SignUpForm()
    return render(request,'registration/signup.html', {'form':form})
 

@login_required(login_url='login/')
def new_image(request):
    current_user = request.user.profile
    if request.method == 'POST':
        form = uploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.profile = current_user
            image.save()
        return redirect('profile')
    else:
        form = uploadForm()
    return render(request, 'new_image.html', {'form':form}) 
