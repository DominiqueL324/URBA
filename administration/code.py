from administration.ajax_methodes import configureNotification,envoyerMail
from django.shortcuts import render, redirect, HttpResponse
from rdv.models import Responsable, RendezVous, Service, Client, ResponsableService, Fichier
from .models import Adjoint,JourSpecifique
from .ajax_methodes import updateZimbraCal,updateZimbraCalDel
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib import messages
from disponibilites.form import EventForm, ResponsableForm, LoginForm
from disponibilites.models import Evenement, Notification
from django.db import transaction, IntegrityError
from datetime import date, datetime,time,timedelta
from django.core.mail import send_mail
from .form import ServiceForm, RdvFormAdmin , AdjointForm
from django.contrib.auth.models import User, Group
from .form import AdministreForm
from django.core.files.storage import FileSystemStorage
import xlwt, xlrd,random, string, json
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


#Gestion des Adjoint et superviseur
#dashboard adjoint et superviseur
@login_required
def dashboardAdSu(request):
    context = {}
    try:
        adjoints = Adjoint.objects.all().order_by('-id')
        context['adjoints'] = adjoints
        context['user'] = request.user
    except:
        messages.error(request, "Erreur interne au système")
    return render(request, 'administration/adjoint.html', context)

#ajout responsable
@login_required
def addAdjointSu(request):
    form = AdjointForm(request.POST)
    context = {}
    if form.is_valid():
        if form.cleaned_data['mdp'] == form.cleaned_data["mdp1"]:
            adjoint = Adjoint()
            if form.cleaned_data['role'] == '':
                messages.error(request,"Mauvais rôle")
                context = {"adjoint": responsable,"user": request.user,"form": form,}
                return render(request,'administration/adjoint_add.html',context)
            with transaction.atomic():
                user = User(is_superuser=False, is_active=True, is_staff=True)
                user.first_name = form.cleaned_data['nom']
                user.last_name = form.cleaned_data['prenom']
                user.email = form.cleaned_data['email']
                user.username = form.cleaned_data['nom_d_utilisateur']
                user.set_password(form.cleaned_data['mdp'])
                us = User.objects.filter(username=user.username)
                cas=""
                if us.exists():
                    messages.error(request, "Un agent utilisateur avec cet identifiant existe déjà")
                    context['form'] = form
                    return render(request, 'administration/adjoint_add.html',context) 
                us = User.objects.filter(email=user.email)
                if us.exists():
                    messages.error(request, "Un agent utilisateur avec ce mail existe déjà")
                    context['form'] = form
                    return render(request, 'administration/adjoint_add.html',context) 
                user.save()
                if form.cleaned_data['role'] == "Adjoint":
                    user.groups.add(Group.objects.filter(name="Adjoint").first().id)
                    cas  = "ajout_adjoint"
                else:
                    user.groups.add(Group.objects.filter(name="Superviseur").first().id)
                    cas  = "ajout_superviseur"
                adjoint.user = user
                adjoint.telephone = form.cleaned_data['tel_number']
                adjoint.save()

                #envoi du mail
                subject = 'Création de compte '+form.cleaned_data['role']
                message = 'Bonjour ' + adjoint.user.first_name + ' votre compte '+form.cleaned_data['role']+' a été crée vos identifiants sont '
                message = message+'\nNom d\'utilisateur: '+ adjoint.user.username +'\n'
                message= message+'mot de Passe: ' +form.cleaned_data['mdp']+ '\n'
                message = message+'Connectez vous pour modifier ces informations au besoin'
                destinataire = adjoint.user.email
                expediteur = 'brunoowona12@gmail.com'
                nt = Notification()
                nt = configureNotification(cas,adjoint,form.cleaned_data['mdp'])
                envoyerMail(nt,[adjoint.user.email], 'brunoowona12@gmail.com')

            messages.success(request, 'Adjoint/Superviseur ajouté avec succès')
            return redirect('administration:adjoint_dashboard')

        messages.error(request, "Les mots de passes ne sont pas identiques")
        context['form'] = form
        return redirect(request, 'administration/adjoint_add.html',context)
    context['form'] = form
    context['errors'] = form.errors.items()
    return redirect(request, 'administration/adjoint_add.html', context)

#edition d'un adjoint
@login_required
def editAdjointSup(request, id):
    context = {}
    test = False
    form = AdjointForm(request.POST)
    if form.is_valid():
        try:
            adjoint = Adjoint.objects.filter(pk=id).first()
            user_e = adjoint.user
            if form.cleaned_data["mdp"] != "" and form.cleaned_data["mdp"] != "":
                if not form.cleaned_data['mdp'] == form.cleaned_data['mdp1']:
                    messages.error(request,"Les mots de passe ne sont pas identiques")
                    context = {"adjoint": responsable,"user": request.user,"form": form,}
                    return render(request,'administration/adjoint_edit.html',context)
                else:
                    test = True
            if form.cleaned_data['role'] == '':
                messages.error(request,"Mauvais rôle")
                context = {"adjoint": responsable,"user": request.user,"form": form,}
                return render(request,'administration/adjoint_edit.html',context)
            groups = Group.objects.filter(name=user_e.groups.all().first().name).first()
            groups.user_set.remove(user_e)
            user_e.groups.add(Group.objects.filter(name=form.cleaned_data['role']).first())
            user_e.username = form.cleaned_data['nom_d_utilisateur']
            user_e.last_name = form.cleaned_data['prenom']
            user_e.first_name = form.cleaned_data['nom']
            user_e.email = form.cleaned_data['email']
            #verification de mail et de username
            us = User.objects.filter(username=user_e.username)
            if us.exists() and us.first().id != user_e.id:
                messages.error(request, "Un  utilisateur avec cet identifiant existe déjà")
                context['form'] = form
                context['adjoint'] = Adjoint.objects.filter(pk=id).first()
                return render(request, 'administration/adjoint_edit.html',context) 
            us = User.objects.filter(email=user_e.email)
            if us.exists() and us.first().id != user_e.id:
                messages.error(request, "Un  utilisateur avec ce mail existe déjà")
                context['form'] = form
                context['adjoint'] = Adjoint.objects.filter(pk=id).first()
                return render(request, 'administration/adjoint_edit.html',context) 

            adjoint.telephone = form.cleaned_data['tel_number']
            adjoint.save()
            pwd = ""
            if test == True:
                messages.success(request,"informations  modifiées avec succès")
                pwd = form.cleaned_data["mdp"]
                user_e.set_password(form.cleaned_data["mdp"])
            else:
                messages.success(request, "informations  modifiées avec succès")
                user_e.save()

            #envoi du mail
            cas =""
            if form.cleaned_data['role'] == "Adjoint":
                cas = "modification_adjoint"
            else:
                cas = "modification_superviseur"
            nt = Notification()
            nt = configureNotification(cas,adjoint,pwd)
            envoyerMail(nt,[adjoint.user.email], 'brunoowona12@gmail.com')

            if request.user.groups.filter(name="Administrateur"):
                return redirect('administration:adjoint_dashboard')
            else:
                return redirect('administration:dashboard')
        except Exception as e:
            messages.error(request,str(e))
            context = {
                "adjoint": Adjoint.objects.filter(pk=id).first(),
                "user": Responsable.objects.filter(pk=id).first().user,
                "form": form,
            }
            context['errors'] = form.errors.items()
            return render(request, 'administration/adjoint_edit.html',context)
    context = {
        "adjoint": Adjoint.objects.filter(pk=id).first(),
        "user": Responsable.objects.filter(pk=id).first().user,
        "form": form,
        "errors" : form.errors.items()
    }
    return render(request, 'administration/adjoint_edit.html', context)

#recupération pour edition
@login_required
def getAdjointToEdit(request, id):
    context = {}
    servF = []
    try:
        adjoint = Adjoint.objects.filter(pk=id)
        if adjoint.exists(): 
            adjoint = adjoint.first()
            form = AdjointForm({
                'nom':adjoint.user.last_name,
                'prenom':adjoint.user.first_name,
                'tel_number':adjoint.telephone,
                'email':adjoint.user.email,
                'nom_d_utilisateur':adjoint.user.username,
                'role':adjoint.user.groups.all().first().name
            })
            context = {
                "adjoint": adjoint,
                "user": adjoint.user,
                "form": form,
            }
            return render(request, 'administration/adjoint_edit.html',context)
    except Exception as e:
        context['test'] = " "
        messages.error(request, str(e))
        return redirect('administration:adjoint_dashboard')
    context['errors'] = "Erreur inconnue"
    return render(request, 'administration/adjoint_edit.html', context)

#suppression d'un ADJOINT
@login_required
def deleteAdjoint(request, id):
    try:
        adjoint = Adjoint.objects.filter(pk=id)
        if adjoint.exists():
            adjoint = adjoint.first()
            us = adjoint.user
            adjoint.delete()
            us.delete()
            messages.success(request, "Adjoint supprimer avec success")
            return redirect('administration:adjoint_dashboard')
    except:
        messages.error(request, "Adjoint inexistant")
        return redirect('administration:adjoint_dashboard')
    messages.error(request,"Erreur de suppréssion de service veuillez réessayer")
    return redirect('administration:adjoint_dashboard')

#go to add Adjoint
def goToAddAdjoint(request):
    form = AdjointForm()
    context = {'form': form}
    return render(request, 'administration/adjoint_add.html', context)



#-------------------METHODE AJAX------------------------#
#Modifier état rdv
@login_required
def updateRdv(request):
    id = request.GET.get("id", None)
    valeure = request.GET.get("valeure", None)
    if request.is_ajax and request.method == "GET":
        try:
            rdv = RendezVous.objects.filter(id=id).first()
            rdv.etat = valeure
            rdv.save()
            nt = Notification()
            #envoi du mail
            if valeure == "Annule":
                nt = configureNotification("rdv_annule",rdv)
                updateZimbraCalDel(rdv)
            if valeure == "Approuve":
                nt = configureNotification("rdv_valide",rdv)
            #if valeure == "Reporte":
                #nt = configureNotification("ajout_rdv",rdv)
            if valeure == "En attente":
                nt = configureNotification("rdv_en_attente",rdv)

            envoyerMail(nt,[rdv.client.email], 'brunoowona12@gmail.com')
            return JsonResponse({"bon": 1}, status=200)
        except:
            return JsonResponse({"bon": 0}, status=200)

#>>>>>>>>>>>>>>>>>>>>>>>>>Gestion des jours spécifiques

@login_required
def dashboardJS(request):
    return render(request,'administration/specifiques.html')

#recupeation ajax des jours spécifiques pour le calendrier d'acceuil 
@login_required
def getSpecificsDays(request):
    final = []
    day = {}
    js=''
    man = request.GET.get("man",None)
    if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists()  or request.user.groups.filter(name="Superviseur").exists():
        js = JourSpecifique.objects.all()
    else:
        js = JourSpecifique.objects.filter(responsable = request.user.responsable)

    if man != None and int(man) > 0:
        js = JourSpecifique.objects.filter(responsable = int(man))

    if int(man )== -1:
        js = JourSpecifique.objects.all()

    for j in js:
        if j.date != None :
            day = {
                'clef':'non_recurrence',
                'id':j.id,
                'title': j.service.nom,
                'color': j.couleur,
                'start': str(j.date.year)+ str(j.date.month).zfill(2)+str(j.date.day).zfill(2)+"T"+str(j.heure_debut.hour).zfill(2)+":"+str(j.heure_debut.minute).zfill(2)+":00",
                'end':str(j.date.year)+ str(j.date.month).zfill(2)+str(j.date.day).zfill(2)+"T"+str(j.heure_fin.hour).zfill(2)+":"+str(j.heure_fin.minute).zfill(2)+":00",
                'allDays':False,
            }
        else:
            if j.date_fin is not None:
                day = {
                    'clef':'recurrence',
                    'id':j.id,
                    'title': j.service.nom,
                    'startTime': str(j.heure_debut.hour).zfill(2)+":"+str(j.heure_debut.minute).zfill(2)+":00",
                    'endTime':str(j.heure_fin.hour).zfill(2)+":"+str(j.heure_fin.minute).zfill(2)+":00",
                    'startRecur': str(j.date_debut.year)+'-'+ str(j.date_debut.month).zfill(2)+'-'+str(j.date_debut.day).zfill(2),
                    'endRecur': str(j.date_fin.year)+'-'+str(j.date_fin.month).zfill(2)+'-'+str(j.date_fin.day).zfill(2),
                    'daysOfWeek': j.jour_semaine,
                    'color': j.couleur
                }
            else:
                day = {
                    'clef':'recurrence',
                    'id':j.id,
                    'title': j.service.nom,
                    'startTime': str(j.heure_debut.hour).zfill(2)+":"+str(j.heure_debut.minute).zfill(2)+":00",
                    'endTime':str(j.heure_fin.hour).zfill(2)+":"+str(j.heure_fin.minute).zfill(2)+":00",
                    'startRecur': str(j.date_debut.year)+'-'+ str(j.date_debut.month).zfill(2)+'-'+str(j.date_debut.day).zfill(2),
                    'daysOfWeek': j.jour_semaine,
                    'color': j.couleur,
                }
        final.append(day)
             
    return JsonResponse({"js":final},status = 200)

@login_required
def goToAddJS(request):
    services = []
    context = {}
    rsp = ''
    if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists()  or request.user.groups.filter(name="Superviseur").exists():
        rsp = ResponsableService.objects.all()
    else:
        rsp = ResponsableService.objects.filter(responsable=request.user.responsable.id)
    if rsp.exists():
        for serv in rsp:
            services.append(serv.service)
        context={
            'services': services 
        }
        return render(request,'administration/specifiques_add.html',context)
    return render(request,'administration/specifiques_add.html')

@login_required
@csrf_exempt
def addJoursSpecifique(request):
    evt = request.POST.get('evt')
    service = request.POST.get('service')
    service= service.replace('"','')
    service= service.replace('[','')
    service= service.replace(']','')
    service = service.split(',')
    evt = json.loads(evt)
    if request.is_ajax and request.method == "POST":
        for serv in service:
            for ev in evt:
                d = str(ev['start']).split('-')
                JourSpecifique.objects.create(
                    responsable=request.user.responsable,
                    id_jour= ev['id'],
                    service= Service.objects.filter(pk=serv).first(),
                    date=ev['start'],
                    heure_debut = ev['startTime'],
                    heure_fin = ev['endTime'],
                    couleur=request.user.responsable.couleur_js
                )
        return redirect('administration:joursSpecifiques_dashboard')
    return JsonResponse({"bad": 1}, status=200)

def addJoursSpecifiqueRecurence(request):
    evt = request.POST.get('evt')
    service = request.POST.get('service')
    days = request.POST.get('day')
    service= service.replace('"','')
    service= service.replace('[','')
    service= service.replace(']','')
    service = service.split(',')
    evt = json.loads(evt)
    if request.is_ajax and request.method == "POST":
        for serv in service:
            if evt["endRecur"] != "":
                JourSpecifique.objects.create(
                    responsable = request.user.responsable,
                    id_jour = evt['id'],
                    service= Service.objects.filter(pk=serv).first(),
                    heure_debut = evt['startTime'],
                    heure_fin = evt['endTime'],
                    date_debut = evt['startRecur'],
                    date_fin = evt['endRecur'],
                    jour_semaine = days,
                    couleur=request.user.responsable.couleur_js
                )
            else:
                JourSpecifique.objects.create(
                    responsable = request.user.responsable,
                    id_jour = evt['id'],
                    service= Service.objects.filter(pk=serv).first(),
                    heure_debut = evt['startTime'],
                    heure_fin = evt['endTime'],
                    date_debut = evt['startRecur'],
                    jour_semaine = days,
                    couleur=request.user.responsable.couleur_js
                )
        return JsonResponse({"good": 1}, status=200)
    return JsonResponse({"bad": 1}, status=200)

def deleteJS(request):
    id = id = request.GET.get("id", None)
    js = JourSpecifique.objects.filter(pk=id)
    if js.exists():
        js = js.first()
        js.delete()
        messages.success(request, "Horaire supprimer avec success")
        return JsonResponse({"good": 1}, status=200)

#ajout administre Ajax
@login_required
@csrf_exempt
def addAdministreAjax(request):
    nom = request.POST.get('nom')
    prenom = request.POST.get('prenom')
    phone = request.POST.get('phone')
    mail = request.POST.get('mail')
    adresse = request.POST.get('adresse')
    if request.is_ajax and request.method == "POST":
        administre = Client()
        administre.nom = nom
        administre.prenom = prenom
        administre.email = mail
        administre.adresse = adresse
        administre.telephone = phone
        administre.password = "".join([random.choice(string.ascii_letters) for _ in range(10)])
        ad = Client.objects.filter(email=mail)
        if ad.exists():
            #messages.error(request, "Un administré avec ce mail existe déjà")
            return JsonResponse({"erreur":"Un administré avec le mail "+administre.email+" \nexiste déjà veuillez changer de mail"}, status=200)

        administre.save()
        send_mail(
            'Création de compte administré',  #subject
            'Bonjour ' + administre.prenom +" votre a été  crée au service Urbanisme votre mot de passe est "+ administre.password +" et votre nom d'utilsateur "+administre.email+
            "Vous pouvez modifier votre mot de passe en vous connectant sur notre plateforme",
            'brunoowona12@gmail.com',  #from_mail
            [administre.email],  #recipient list []
            fail_silently=False,  #fail_silently
        )
        return JsonResponse({"erreur":0,"nom": administre.nom,"prenom":administre.prenom,'id':administre.id}, status=200)
    else:
        return JsonResponse({"erreur":"Erreur durant l'ajout veuillez reéssayer"})

#recupération des responsables d'un service pour ediion d'un RDV
@login_required
def getRespoofServiceForEditRdv(request):
    rdv = request.GET.get('rdv',None)
    serv = request.GET.get('service',None)
    responsables = ""
    final=[]
    if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
        if request.is_ajax and request.method == 'GET':
            if serv != " ":
                responsables = ResponsableService.objects.filter(service=serv)
            else:
                service = RendezVous.objects.filter(id=rdv).first().service
                responsables = ResponsableService.objects.filter(service=service.id)
            
            for respo in responsables:
                final.append({
                    'id':respo.responsable.id,
                    'nom':respo.responsable.user.last_name,
                    'prenom':respo.responsable.user.first_name
                })
            if request.user.groups.filter(name="Administrateur").exists():
                final.append({
                    'id':request.user.id,
                    'nom':request.user.last_name,
                    'prenom':request.user.first_name
                })
            return JsonResponse({"respo":final,"erreur":0}, status=200)
        else:
            return JsonResponse({"erreur":"Veuillez reéssayer plus tard"}, status=200)
    else:
        return JsonResponse({"erreur":"Veuillez reéssayer plus tard1"}, status=200)
