from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode  # on n'importe ceci pour la gestion des tokens
from django.utils.encoding import force_bytes, force_text  # on n'importe ceci pour la gestion des tokens
from django.template.loader import render_to_string  # on importe ceci pour rendre les templates d'email
from django.contrib.sites.shortcuts import get_current_site  # on importe ceci pour obtenir le site courant

from Authentification import settings 
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User # ici on importe le modèle User pour gérer les utilisateurs
from django.contrib import messages # ici on importe le module messages pour afficher des messages à l'utilisateur
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMessage

from app.token import TokenGenerator # on importe la fonction send_mail pour envoyer des emails



# Create your views here.

def home(request):
    return render(request, "app/index.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Nom d'utilisateur déjà pris.")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email déjà utilisé.")
            return redirect("register")
        if not username.isalnum():
            messages.error(request, "Le nom d'utilisateur ne doit contenir que des caractères alphanumériques.")
            return redirect("register")
        
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("register")
        

        mon_utilisateur = User.objects.create(username=username, email=email, password=password)
        mon_utilisateur.username = username
        mon_utilisateur.email = email
        mon_utilisateur.set_password(password)

        mon_utilisateur.is_active = False  # Désactive le compte jusqu'à la confirmation par email

        mon_utilisateur.save()
        messages.success(request, "Utilisateur créé avec succès.")
        
        # Envoi d'un email de bienvenue
        subject = "Bienvenue sur notre site"
        message = f"Merci de vous être inscrit sur notre site, cher(e) {mon_utilisateur}. \nNous sommes ravis de vous avoir parmi nous ! \n\nCordialement,\nL'équipe du site."
        from_email = settings.EMAIL_HOST_USER
        to_list = [mon_utilisateur.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)  #fail_silently=True pour éviter les erreurs d'envoi d'email en développement

        #Email de confirmation d'inscription (optionnel)
        current_site = get_current_site(request)
        email_subject = "Confirmez votre adresse email"
        message_confirm = render_to_string("confirm_email.html", {
            "user": mon_utilisateur,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(mon_utilisateur.pk)),
            "token": TokenGenerator().make_token(mon_utilisateur),
        })
        email_message = EmailMessage(email_subject, message_confirm, settings.EMAIL_HOST_USER, [mon_utilisateur.email])
        email_message.fail_silently = False
        email_message.send()

        return redirect("login")
    return render(request, "app/register.html")


def login_view(request):
    if request.method == "POST":
       username = request.POST.get("username")
       password = request.POST.get("password")
       user = authenticate(username=username, password=password)
       my_user = User.objects.get(username=username)

       if user is not None:
           login(request, user)
           username = user.username
           return render(request, "app/index.html", {"username": username})
       elif my_user.is_active == False:
           messages.error(request, "Compte inactif. Veuillez vérifier votre email pour l'activer.")
           return redirect("login")
       else:
           messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
           return redirect("login")
    return render(request, "app/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        mon_utilisateur = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        mon_utilisateur = None

    if mon_utilisateur is not None and TokenGenerator().check_token(mon_utilisateur, token):
        mon_utilisateur.is_active = True
        mon_utilisateur.save()
        messages.success(request, "Votre compte a été activé avec succès.")
        return redirect("login")
    else:
        messages.error(request, "Le lien d'activation est invalide.")
        return redirect("register")