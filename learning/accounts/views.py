from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Enrollment
from courses.models import Course

def index(request):
    return render(request, 'index.html')


def signup_view(request):
    if request.method=="POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "registration Successful...")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html",{"form":form})


def login_view(request):
    if request.method=="POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid usee name or password!")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html",{"form":form})


def logout_view(request):
    if request.method=="POST":
        logout(request)
        return redirect("home")
    
 
@login_required(login_url='login')
def dashboard_view(request):
    courses = Course.objects.all()
    return render(request, 'accounts/dashboard.html',{'courses':courses})

    