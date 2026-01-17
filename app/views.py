from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User # ici on importe le modèle User pour gérer les utilisateurs
from django.contrib import messages # ici on importe le module messages pour afficher des messages à l'utilisateur
from django.contrib.auth import authenticate, login, logout




# Create your views here.

def home(request):
    return render(request, "app/index.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        mon_utilisateur = User.objects.create(username=username, email=email, password=password)
        mon_utilisateur.username = username
        mon_utilisateur.email = email
        mon_utilisateur.set_password(password)
        mon_utilisateur.save()
        messages.success(request, "Utilisateur créé avec succès.")
        return redirect("login")
    return render(request, "app/register.html")


def login_view(request):
    if request.method == "POST":
       username = request.POST.get("username")
       password = request.POST.get("password")
       user = authenticate(username=username, password=password)
       if user is not None:
           login(request, user)
           username = user.username
           return render(request, "app/index.html", {"username": username})
       else:
           messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
           return redirect("login")
    return render(request, "app/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("login")