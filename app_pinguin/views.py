from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required


from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, "home.html")

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def comparaison(request):
    return render(request, "comparaison.html")

@login_required
def secteur(request):
    return render(request, "secteur.html")

@login_required
def carte(request):
    return render(request, "carte.html")


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def home(request):
    return render(request, "home.html")
