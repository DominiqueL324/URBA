from disponibilites.models import Notification
from .ajax_methodes import configureNotification,envoyerMail
from rdv.models import Responsable, RendezVous, Service, Client
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Adjoint,JourSpecifique,Administrateur
from django.contrib import messages
from disponibilites.form import  ResponsableForm
from django.contrib.auth.models import User, Group
from django.db import transaction, IntegrityError
import datetime, random, string
from django.http import JsonResponse
from django.core.mail import send_mail
from rdv.views import updateZimbraCal,updateZimbraCalDel
import requests


#Gestion des Administrateurs
#dashboard adjoint et superviseur
@login_required
def dashboardAdmin(request):
    context = {}
    try:
        administrateur = Administrateur.objects.all().order_by('-id')
        context['administrateurs'] = administrateur
        context['user'] = request.user
    except:
        messages.error(request, "Erreur interne au système")
    return render(request, 'administration/administrateur/administrateur.html', context)

#ajout responsable
@login_required
def addAdmin(request):
    form = ResponsableForm(request.POST)
    context = {}
    if form.is_valid() or not form.is_valid():
        if form.cleaned_data['mdp'] == form.cleaned_data["mdp1"]:
            administrateur = Administrateur()
            with transaction.atomic():
                user = User(is_superuser=True, is_active=True, is_staff=True)
                user.first_name = form.cleaned_data['prenom']
                user.last_name = form.cleaned_data['nom']
                user.email = form.cleaned_data['email']
                user.username = form.cleaned_data['nom_d_utilisateur']
                user.set_password(form.cleaned_data['mdp'])
                us = User.objects.filter(username=user.username)
                if us.exists():
                    messages.error(request, "Un utilisateur avec ce nom d'utiliasteur exise déjà")
                    context['form'] = form
                    context['errors'] = form.errors.items()
                    return render(request,'administration/administrateur/add.html', context)
                
                us = User.objects.filter(email=user.email)
                if us.exists():
                    messages.error(request, "Un utilisateur avec ce mail exise déjà")
                    context['form'] = form
                    context['errors'] = form.errors.items()
                    return render(request,'administration/administrateur/add.html', context)

                user.save()
                user.groups.add(Group.objects.filter(name="Administrateur").first().id)
                administrateur.user = user
                administrateur.telephone = form.cleaned_data['tel_number']
                administrateur.save()

                #envoi du mail
                nt = Notification()
                nt = configureNotification("ajout_administrateur",administrateur,form.cleaned_data['mdp'])
                envoyerMail(nt,[administrateur.user.email], 'brunoowona12@gmail.com')

            messages.success(request, 'Administrateur ajouté avec succès')
            return redirect('administration:administrateur_dashboard')
        messages.error(request, "Les mots de passes ne sont pas identiques")
        context['form'] = form
        return render (request, 'administration/administrateur/add.html',context)
    context['form'] = form
    context['errors'] = form.errors.items()
    return render(request,'administration/administrateur/add.html', context)

#edition d'un adjoint
@login_required
def editAdmin(request, id):
    context = {}
    test = False
    form = ResponsableForm(request.POST)
    if form.is_valid() or not form.is_valid():
        try:
            administrateur = Administrateur.objects.filter(pk=id).first()
            user_e = administrateur.user
            if form.cleaned_data["mdp"] != "" and form.cleaned_data["mdp"] != "":
                if not form.cleaned_data['mdp'] == form.cleaned_data['mdp1']:
                    messages.error(request,"Les mots de passe ne sont pas identiques")
                    context = {"administrateur": administrateur,"user": request.user,"form": form,}
                    return render(request,'administration/administrateur/edit.html',context)
                else:
                    test = True
            user_e.username = form.cleaned_data['nom_d_utilisateur']
            user_e.last_name = form.cleaned_data['prenom']
            user_e.first_name = form.cleaned_data['nom']
            user_e.email = form.cleaned_data['email']
            us = User.objects.filter(username=user_e.username)
            if us.exists() and us.first().id != user_e.id:
                messages.error(request, "Un utilisateur avec ce nom d'utiliasteur exise déjà")
                context['form'] = form
                context['administrateur'] = Administrateur.objects.filter(pk=id).first()
                context['errors'] = form.errors.items()
                return render(request,'administration/administrateur/edit.html', context)
                
            us = User.objects.filter(email=user_e.email)
            if us.exists() and us.first().id != user_e.id:
                messages.error(request, "Un utilisateur avec ce mail exise déjà")
                context['form'] = form
                context['administrateur'] = Administrateur.objects.filter(pk=id).first()
                context['errors'] = form.errors.items()
                return render(request,'administration/administrateur/edit.html', context)
            administrateur.telephone = form.cleaned_data['tel_number']
            administrateur.save()
            pwd =""
            if test == True:
                messages.success(request,"informations  modifiées avec succès")
                pwd = form.cleaned_data["mdp"]
                user_e.set_password(form.cleaned_data["mdp"])
            else:
                messages.success(request, "informations  modifiées avec succès")
            user_e.save()
            #envoi du mail
            nt = Notification()
            nt = configureNotification("modification_administrateur",administrateur,pwd)
            envoyerMail(nt,[administrateur.user.email], 'brunoowona12@gmail.com')
           

            return redirect('administration:administrateur_dashboard')
        except Exception as e:
            messages.error(request,str(e))
            context = {
                "administrateur": Administrateur.objects.filter(pk=id).first(),
                "user": Administrateur.objects.filter(pk=id).first().user,
                "form": form,
            }
            context['errors'] = form.errors.items()
            return render(request, 'administration/administrateur/edit.html',context)
    context = {
        "administrateur": Administrateur.objects.filter(pk=id).first(),
        "user": Administrateur.objects.filter(pk=id).first().user,
        "form": form,
        "errors" : form.errors.items()
    }
    return render(request, 'administration/administrateur/edit.html', context)

#recupération pour edition
@login_required
def getAdminToEdit(request, id):
    context = {}
    servF = []
    #try:
    administrateur = Administrateur.objects.filter(pk=id)
    if administrateur.exists():
        administrateur = administrateur.first()
        form = ResponsableForm({
                'nom':administrateur.user.last_name,
                'prenom':administrateur.user.first_name,
                'tel_number':administrateur.telephone,
                'email':administrateur.user.email,
                'nom_d_utilisateur':administrateur.user.username,
            })
        context = {
                "administrateur": administrateur,
                "user": administrateur.user,
                "form": form,
            }
        return render(request, 'administration/administrateur/edit.html', context)
    #except Exception as e:
        #context['test'] = " "
        #messages.error(request, str(e))
        #return redirect('administration:administrateur_dashboard')
    context['errors'] = "Erreur inconnue"
    return  redirect('administration:administrateur_dashboard')

#suppression d'un ADmin
@login_required
def deleteAdmin(request, id):
    try:
        administrateur = Administrateur.objects.filter(pk=id)
        if administrateur.exists():
            administrateur = administrateur.first()
            us = administrateur.user
            administrateur.delete()
            us.delete()
            messages.success(request, "Administrateur supprimer avec success")
            return redirect('administration:administrateur_dashboard')
    except:
        messages.error(request, "Administrateur inexistant")
        return redirect('administration:administrateur_dashboard')
    messages.error(request,"Erreur de suppréssion de service veuillez réessayer")
    return redirect('administration:administrateur_dashboard')

#go to add Admin
def goToAddAdmin(request):
    form = ResponsableForm()
    context = {'form': form}
    return render(request, 'administration/administrateur/add.html', context)

#>>>>>>>>>>>>>>>>Gestion du compté oublié
def getAcces(request):
    return render(request, 'administration/account/password1.html')

def checkEmailAndPhon(request):
    email = request.POST.get('email',None)
    tel = request.POST.get('tel',None)
    us = User.objects.filter(email=email)
    context={}
    if us.exists():
        us = us.first()
        adm = Administrateur.objects.filter(user=us.id,telephone=tel)
        rsp = Responsable.objects.filter(user=us.id,telephone=tel)
        adj = Adjoint.objects.filter(user=us.id,telephone=tel)
        if adm.exists():
            context['man']=adm.first()
            return render(request, 'administration/account/password2.html',context)
        elif rsp.exists():
            context['man']=rsp.first()
            return render(request, 'administration/account/password2.html',context)
        elif adj.exists():
            context['man']=adj.first()
            return render(request, 'administration/account/password2.html',context)
        else:
            messages.error(request,'Désolé aucun compte retrouvé avec l\'email '+email+' et le Numéro '+str(tel))
            return render(request, 'administration/account/password1.html')
    else:
        messages.error(request,'Désolé aucun compte retrouvé avec l\'email '+email)
        return render(request, 'administration/account/password1.html')

def editPass(request,id):
    user = User.objects.filter(pk=id)
    adm = Administrateur.objects.filter(user=user.first().id)
    rsp = Responsable.objects.filter(user=user.first().id)
    adj = Adjoint.objects.filter(user=user.first().id)
    context ={}
    mdp = "".join([random.choice(string.ascii_letters) for _ in range(10)])
    if adm.exists():
        context['man']=adm.first()
    if rsp.exists():
        context['man']=rsp.first()
    if adj.exists():
        context['man']=adj.first()
    
    if user.exists():
        user = user.first()
        user.set_password(mdp)
        user.save()

        data_ = {
            "sujet":'Modification de mot de passe',
            "from_mail":"ne-pas-repondre@saint-medard-en-jalles.fr",
            "recipient":user.email+",",
            "html_body":" ",
            "email_host_user":"ne-pas-repondre@saint-medard-en-jalles.fr",
            "email_host_password":"@XB58fk33",
            "content": 'Bonjour '+user.last_name+' '+user.first_name+' Votre nouveau mot de passe est '+mdp+' connectez-vous pour le changer au besoin ',
        }
        token = requests.post("https://reservation.saint-medard-en-jalles.fr:4443/mail/send",data=data_,verify=False).json()

        """send_mail( 
            'Modification de mot de passe', #subject
            'Bonjour '+user.last_name+' '+user.first_name+' Votre nouveau mot de passe est '+mdp+' connectez-vous pour le changer au besoin ',
            'brunoowona12@gmail.com', #from_mail
            [user.email,], #recipient list []
            fail_silently=False, #fail_silently
        )"""
        messages.success(request,'Mot de passe modifié avec succès consulter votre boite email pour le récupérer')
        return render(request, 'administration/account/login.html')
    messages.error(request,"Erreur")
    context['man']=user.first()
    return render(request, 'administration/account/password2.html',context)

#supréssion de plusieurs RDV
def deleteManyRdv(request):
    liste_ = request.GET.get('liste',None)
    ident = request.GET.get('id',None)
    liste_= liste_.replace('[','')
    liste_= liste_.replace(']','')
    liste_ = liste_.split(',')
    if ident == "RDV" or ident == 'DASH':
        for id in liste_:
            rdv = RendezVous.objects.filter(pk=int(id)).first()
            updateZimbraCalDel(rdv)
            rdv.delete()
    if ident == "ADMNS":
        for id in liste_:
            cl = Client.objects.filter(pk=int(id)).first()
            cl.delete()
    if ident == "ADMNT":
        for id in liste_:
            ad = Administrateur.objects.filter(pk=int(id)).first()
            us = ad.user
            ad.delete()
            us.delete()
    if ident == "SERVICE":
        for id in liste_:
            serv = Service.objects.filter(pk=int(id)).first()
            serv.delete()
    if ident == "ADJ":
        for id in liste_:
            adj = Adjoint.objects.filter(pk=int(id)).first()
            us = adj.user
            adj.delete()
            us.delete()
    if ident == "RSP":
        for id in liste_:
            rsp = Responsable.objects.filter(pk=int(id)).first()
            us = rsp.user
            rsp.delete()  
            us.delete()
    return JsonResponse({"good": 1}, status=200)
