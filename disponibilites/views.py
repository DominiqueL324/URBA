from django.shortcuts import render,redirect
from rdv.models import Responsable,RendezVous,Service,ResponsableService
from .form import LoginForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib import messages 
from .models import Evenement,Notification
from .form import EventForm,ResponsableForm
from django.db import transaction, IntegrityError
from datetime import date
from django.core.mail import send_mail
from administration.models import JourSpecifique

# Create your views here.

def LoginPage(request):
    return render(request,"disponibilites/account/login.html")

def logoutUser(request):
    logout(request)
    return redirect ('index')

@csrf_protect
def authentication(request): 
    form = LoginForm(request.POST)
    context = {}
    if form.is_valid():
        log = form.cleaned_data['login']
        mdp = form.cleaned_data['mdp']
        utilisateur = authenticate(username=log,password=mdp)
        if utilisateur is not None:
            if utilisateur.is_active:
                login(request,utilisateur)
            else:
                return HttpResponse("You're account is disabled.")
        else:
            context['form'] = form
            context['erreur'] = "Aucun profils ne correspond à ces accès"
            return render (request,"disponibilites/account/login.html",context)
        return redirect("disponibilites:dashboard")

    context['errors'] = form.errors.items()
    context['form'] = form
    return render(request,'disponibilites/account/login.html',context)

@login_required()
def validate(request,id):
    context = {}
    rdv = RendezVous.objects.filter(pk=id)
    if rdv.exists():
        context = {
            "rdv" : rdv.first()
        }
        return render(request,'disponibilites/validate.html',context)
    messages.error(request,"desole aucun RDV trouvé pour cet identifiant")
    return redirect(request,'disponibilites/validate.html',context)

@login_required()
def dashboard(request):
    context={}

    #récupération des RDV
    rdvs = RendezVous.objects.all().order_by("-id")
    try:
        Rservices = ResponsableService.objects.filter(responsable=request.user.responsable.id)
        rdvF = RendezVous.objects.none()
        for rdv in rdvs:
            for Rservice in Rservices:
                if rdv.service.id == Rservice.service.id:
                    rdvF |= RendezVous.objects.filter(service=Rservice.service.id,en_attente=0)   
        context['agent'] = request.user
        context['responsable'] = request.user.responsable
        context['rdvs'] = rdvF
        return render(request,"disponibilites/dashboard.html",context)
    except:
        context['agent'] = request.user
        return redirect("/admin/")

@login_required()
def getMyEvent(request):
    context={}
    evts = Evenement.objects.filter(responsable = request.user.responsable.id)
    context = {
        'agent': request.user,
        'evts':evts
    }
    return render(request,"disponibilites/evtDashboard.html",context)
    
@login_required()
def getMyRdv(request):
    context={}
    try: 
        #recupération des RDVS
        rdvs = RendezVous.objects.all().order_by("-id")

        #récupération des services concernés
        Rservices = ResponsableService.objects.filter(responsable=request.user.responsable.id)
        #création d'un queryset vide
        rdvF = RendezVous.objects.none()

        #récupération des rendez-vous concerné
        for rdv in rdvs:
            for Rservice in Rservices:
                if rdv.service.id == Rservice.service.id:
                    rdvF |= RendezVous.objects.filter(service=Rservice.service.id)
                
        rdvs = RendezVous.objects.all()
        context['agent'] = request.user
        context['responsable'] = request.user.responsable
        context['rdvs'] = rdvF
        return render(request,"disponibilites/rdvDashboard.html",context)
    except:
        context['agent'] = request.user
        context['responsable'] = request.user.responsable
        messages.error(request,"Erreur lors de la récupération de vos RDV veuillez reéssayer")
        return render(request,"disponibilites/rdvDashboard.html",context)

@login_required()
def validerRdv(request,id):
    context={}
    rdv = RendezVous.objects.filter(pk=id).first()
    if rdv.en_attente:
        messages.success(request,"Rendez-vous Mis en attente avec succes" )
        rdv.etat = "Approuvé"
        groupe =""
        if request.user.groups.filter(name='Agent').exists():
            groupe = "Agent"
        elif request.user.groups.filter(name='Adjoint').exists():
            groupe = "Adjoint"
        else:
            groupe ="Administrateur"

        notification = Notification.objects.create(
            objet_n="Validation de Rendez-vous",
            user_type = groupe,
            user_n = request.user,
            rdv = rdv,
            type_n="rdv",
            user_name= request.user.get_full_name()
         )
        send_mail(
                   'Mise en attente du  Rendez-Vous', #subject
                   'Salut '+ rdv.client.prenom+' votre rendez vous du '+str(rdv.date_r.day) +'/'+str(rdv.date_r.month)+'/'+str(rdv.date_r.year)+' au service '+rdv.service.nom+" a été mis en attente vous recevrez d'éventules changements par mail",
                   'brunoowona12@gmail.com', #from_mail
                   [rdv.client.email], #recipient list []
                   fail_silently=False, #fail_silently
                )
    else:
        
        messages.success(request,"Rendez-vous approuvé avec succes" )
        rdv.etat = "En attente"
        groupe =""
        if request.user.groups.filter(name='Agent').exists():
            groupe = "Agent"
        elif request.user.groups.filter(name='Adjoint').exists():
            groupe = "Adjoint"
        else:
            groupe ="Administrateur"

        notification = Notification.objects.create(
            objet_n="Mise en attente de Rendez-vous",
            user_type = groupe,
            user_n = request.user,
            rdv = rdv,
            type_n="rdv",
            user_name= request.user.get_full_name()
         )

        send_mail(
                   'Confirmation Rendez-Vous', #subject
                   'Salut '+ rdv.client.prenom+' votre rendez vous du '+str(rdv.date_r.day) +'/'+str(rdv.date_r.month)+'/'+str(rdv.date_r.year)+' au service '+rdv.service.nom+" a été été confirmé vous recevrez d'éventules changements par mail",
                   'brunoowona12@gmail.com', #from_mail
                   [rdv.client.email], #recipient list []
                   fail_silently=False, #fail_silently
                )
    rdv.save()
    return redirect("disponibilites:dashboard_rdv")
    
@login_required()
def gotToAddEventPage(request):
    form = EventForm()
    context = {
        'form':form
    }
    return render(request,"disponibilites/addevent.html",context)

@login_required()
def AddEvenement(request):
    if request.method == 'POST':
        context ={}
        form = EventForm(request.POST)
        if form.is_valid():
            responsable = request.user.responsable
            try:
                with transaction.atomic():
                    event =  Evenement()
                    event.description = form.cleaned_data['description']
                    event.responsable = responsable
                    event.date_d = form.cleaned_data['date_d']
                    event.date_f = form.cleaned_data['date_f']
                    event.color = form.cleaned_data['color']
                    event.type_e = "holiday"
                    event.name = form.cleaned_data['name']
                    if event.date_d > event.date_f:
                        form.errors['internal'] = "La date de début ne saurai être apres la date de fin"
                        context['errors'] = form.errors.items()
                        context['form'] = form
                        return render(request,"disponibilites/addevent.html",context)
                        
                    event.save()

                    #gestion des notifications
                    groupe =""
                    if request.user.groups.filter(name='Agent').exists():
                        groupe = "Agent"
                    elif request.user.groups.filter(name='Adjoint').exists():
                        groupe = "Adjoint"
                    else:
                        groupe ="Administrateur"

                    notification = Notification.objects.create(
                        objet_n="création d'évènement",
                        user_type = groupe,
                        user_n = request.user,
                        evt = event,
                        type_n="evenement",
                        user_name= request.user.get_full_name()
                    )
                    messages.success(request,"Evènement ajouté avec succes" )
                    form = EventForm()
                    return redirect("disponibilites:dashboard_evt")
            except IntegrityError:
                    form.errors['internal'] = "Une érreur est apparue merci de reéssayer!!!"

    context['errors'] = form.errors.items()
    context['form'] = form
    return render(request,"disponibilites/addevent.html",context)

#methode Ajax qui recupère tous les évènement d'un responsable
@login_required()
def GetEvenement(request):
    # request should be ajax and method should be GET.
    if request.is_ajax and request.method == "GET":
        if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Superviseur").exists() or request.user.groups.filter(name="Adjoint").exists():
            evt = Evenement.objects.all()
        else:
            id= request.user.responsable.id
            evt = Evenement.objects.filter(responsable=id)      
        # check for the nick name in the database.
        return JsonResponse({"evt":list(evt.values())}, status = 200)
    else:
            # if nick_name not found, then user can create a new friend.
        return JsonResponse({"responsable":False}, status = 200)

    return JsonResponse({}, status = 400)


#methode Ajax qui recupère  les évènement d'un responsable
@login_required()
def GetEvenementSingle(request,id):
    # request should be ajax and method should be GET.
    if request.is_ajax and request.method == "GET":
        if id == 0:
            evt = Evenement.objects.all()
            return JsonResponse({"evt":list(evt.values())}, status = 200) 
        respo= Responsable.objects.filter(pk=id)
        evt = Evenement.objects.filter(responsable=respo.first().id)      
        # check for the nick name in the database.
        return JsonResponse({"evt":list(evt.values())}, status = 200)
    else:
            # if nick_name not found, then user can create a new friend.
        return JsonResponse({"responsable":False}, status = 200)

    return JsonResponse({}, status = 400)

#Méthode Ajax on verifie si un service est ouvert à une date donnée recupère les RDV et les horaires spécifiques
#d'une journée pour le calendar de prise de RDV (fullcalendar)
def GetEventForAdministrateCalendar(request):
    id_service = request.GET.get("service",None)
    date_e = request.GET.get("date",None)
    responsables = []
    tab_id_responsable=[]
    tab_id_responsable_evt=[]
    liste_rdv = []
    liste_JsL = []
    liste_JsR = []
    responsable = Responsable()

    #creation de la date
    date_s = date_e.split("/")
    date_r = date(int(date_s[2]),int(date_s[1]),int(date_s[0]))
    date_p = date_r
    #recuperation du responsable
    responsable_service = ResponsableService.objects.filter(service=int(id_service))

    if responsable_service.exists():
        for respon_serv in responsable_service:
            responsables.append(Responsable.objects.filter(pk=respon_serv.responsable.id).first())
    else:
        return JsonResponse({"contenu":-2}, status = 200)

    #recupération de tous les rdv de ce jour pour afficher les créneaux pris
    Rdv = RendezVous.objects.filter(date_r = date_p)
    if Rdv.exists():
        for rdv in Rdv:
            obj = {}
            strt = str(rdv.date_r.year)+str(rdv.date_r.month).zfill(2)+str(rdv.date_r.day).zfill(2)+"T"+str(rdv.heure_r.hour).zfill(2)+":"+str(rdv.heure_r.minute).zfill(2)+":"+str(rdv.heure_r.second).zfill(2) 
            fin = str(rdv.date_r.year)+str(rdv.date_r.month).zfill(2)+str(rdv.date_r.day).zfill(2)+"T"+str(rdv.heure_f.hour).zfill(2)+":"+str(rdv.heure_f.minute).zfill(2)+":"+str(rdv.heure_f.second).zfill(2)   
            if rdv.by_phone :
                obj =  {
                        'title':'RDV',
                        'start':strt,
                        'end':fin,
                        'color': '#e4c935'
                    }
            else:
               obj =  {
                        'title':'RDV',
                        'start':strt,
                        'end':fin,
                        'color': '#37f771'
                    }

            liste_rdv.append(obj)
    #recupeartion des heures spécifiques de ce jours 
    JsL = JourSpecifique.objects.filter(date=date_p,service=id_service)
    JsR = JourSpecifique.objects.filter(date_debut__lte=date_p, date_fin__gte=date_p,service=id_service)

    if JsR.exists():
        for Js in JsR:
            strt = str(Js.heure_debut.hour).zfill(2)+":"+str(Js.heure_debut.minute).zfill(2)+":"+str(Js.heure_debut.second).zfill(2) 
            fin = str(Js.heure_fin.hour).zfill(2)+":"+str(Js.heure_fin.minute).zfill(2)+":"+str(Js.heure_fin.second).zfill(2)
            e = {
                    'id': Js.id ,
                    'title': "Heure spécifique d'ouverture du service",
                    'startTime':strt ,
                    'endTime': fin,
                    'startRecur': Js.date_debut,
                    'endRecur' : Js.date_fin,
                    'daysOfWeek': Js.jour_semaine,
                    'color':'#7CFC00',
                    'display': 'background'
                }
            liste_rdv.append(e)
    if JsL.exists():
        for Js in JsL:
            strt = str(Js.date.year).zfill(2)+str(Js.date.month).zfill(2)+str(Js.date.day).zfill(2)+"T"+str(Js.heure_debut.hour).zfill(2)+":"+str(Js.heure_debut.minute).zfill(2)+":"+str(Js.heure_debut.second).zfill(2) 
            fin = str(Js.date.year).zfill(2)+str(Js.date.month).zfill(2)+str(Js.date.day).zfill(2)+"T"+str(Js.heure_fin.hour).zfill(2)+":"+str(Js.heure_fin.minute).zfill(2)+":"+str(Js.heure_fin.second).zfill(2)
            e = {
                    'id': Js.id,
                    'title': "Heure spécifique d'ouverture du service",
                    'start': strt,
                    'end': fin,
                    'display': 'background',
                    'allDay': False
                }
            liste_rdv.append(e)

    dateI = str(date_p.year)+"-"+str(date_p.month).zfill(2)+"-"+str(date_p.day).zfill(2)
    tempsService = Service.objects.filter(id=id_service).first().duree_rdv
    #travail
    if len(responsables) > 1:
        for respo in responsables:
            tab_id_responsable.append(respo.id)

        #recupération des évènements concerné par ce jour
        evt = Evenement.objects.filter(date_d__lte=date_r,date_f__gte=date_r)
        if evt.exists():
            #resupération des responsables de ces évènemnts
            for ev in evt:
                tab_id_responsable_evt.append(ev.responsable.id)

            #on vérfie si un des responsables du services n'est pas responsables d'un évènement qui inclut ce jour
            for respo in tab_id_responsable:
                if respo not in tab_id_responsable_evt:
                    return JsonResponse({"contenu":0,"rdv":liste_rdv,"start_date":dateI,"duree":tempsService}, status = 200)

            #on retourne la réponse
            return JsonResponse({"contenu":1}, status = 200) 
        else:
            return JsonResponse({"contenu":0,"rdv":liste_rdv,"start_date":dateI,"duree":tempsService}, status = 200)  
    else:
        evts = Evenement.objects.filter(responsable=responsable_service.first().responsable.id)
        for evt in evts:
            if evt.date_d <= date_r and evt.date_f >= date_r:
                return JsonResponse({"contenu":1}, status = 200) 
        return JsonResponse({"contenu":0,"lineaire":liste_JsL,"reccurence":liste_JsR,"rdv":liste_rdv,"start_date":dateI,"duree":tempsService}, status = 200)  
    return JsonResponse({"contenu":-1}, status = 200)

#methode Ajax qui recupère toutes les notifications pour la barre de menu et le menu left
@login_required()
def getNotification(request,vue_chk):

    if request.is_ajax and request.method == "GET":
        if vue_chk ==1:
            notif = Notification.objects.all()
        if vue_chk ==2:
            notif = Notification.objects.filter(vue=True)
        if vue_chk ==3:
            notif = Notification.objects.filter(vue=False)

        return JsonResponse({"notif":list(notif.values())}, status = 200)
    else:
        return JsonResponse({"responsable":False}, status = 200)
        
    return JsonResponse({}, status = 400)

#dashboard de notifications
@login_required()
def dashboardNotif(request):
    context={}
    if  request.user.groups.filter(name="Administrateur").exists():
        pass
    else:
        messages.error(request,"Privilèges issufisants")
        return render(request,"disponibilites/dashboard.html",context)

    try:
        notif = Notification.objects.filter(vue=False)
        context = {
                'notifications':notif
            }
        return render(request,"disponibilites/notifications.html",context)
    except:
        messages.error(request,"Une erreur est survenue lors de la récupération des notifications veuillez reéssayer")
        return render(request,"disponibilites/dashboard.html",context)

#methode Ajax qui marque une notification comme vue
@login_required()
def ValidateNotif(request,id):
    if request.is_ajax and request.method == "GET":
        notif = Notification.objects.filter(pk=id).first()
        notif.vue = True 
        notif.save()
        messages.success(request,"Marquée comme lue")
        return redirect("disponibilites:notifications_see")
    else:
        return JsonResponse({"responsable":False}, status = 200)
        
    return JsonResponse({}, status = 400)

#redirection vesr le formulaire de modification d'un agent
@login_required
def goToEditAgent(request):
    form = ResponsableForm({
        'nom':request.user.last_name,
        'prenom':request.user.first_name,
        'tel_number':request.user.responsable.telephone,
        'email':request.user.email,
        'adress':request.user.responsable.adresse,
        'nom_d_utilisateur':request.user.username,
    })
    context ={
        "agent": Responsable.objects.filter(pk=request.user.responsable.id).first(),
        "user": request.user,
        "form":form,
    }
    return render(request,'disponibilites/account/edit_agent.html',context)

@login_required
def editAgent(request):

    context ={}
    test = False
    form = ResponsableForm(request.POST)
    if form.is_valid():
        user_e = request.user
        if  form.cleaned_data["mdp"] != "" and form.cleaned_data["mdp"] != "":
            if not form.cleaned_data['mdp'] == form.cleaned_data['mdp1']:
                messages.error(request,"Les mots de passe ne sont pas identiques")
                context ={
                    "agent": Responsable.objects.filter(pk=request.user.responsable.id).first(),
                    "user": request.user,
                    "form":form,
                }
                return render(request,'disponibilites/account/edit_agent.html',context)
            else:
                test = True 
        user_e.username = form.cleaned_data['nom_d_utilisateur']
        user_e.last_name = form.cleaned_data['prenom']
        user_e.first_name = form.cleaned_data['nom']
        user_e.email = form.cleaned_data['email']
        try:
                respo = Responsable.objects.filter(pk=request.user.responsable.id)
                respo.adresse = form.cleaned_data['adress']
                respo.telephone = form.cleaned_data['tel_number']
                respo.user = user_f
                respo.save()
        except:
                pass
        
        if test == True:
            messages.success(request,"Vos informations ont été modifier avec succès veuillez vous reconnecter avec votre nouveau mot de passe")
            user_e.set_password(form.cleaned_data["mdp"])
        else:
            messages.success(request,"Vos informations ont été modifier avec succès")
        user_e.save()
        request.user = user_e
        form = ResponsableForm()
        return redirect('disponibilites:dashboard')
    else:
        context ={
            "agent": Responsable.objects.filter(pk=request.user.responsable.id).first(),
            "user": request.user,
            "form":form,
        }
        context['errors'] = form.errors.items()
        return render(request,'disponibilites/account/edit_agent.html',context)
    context ={
        "agent": Responsable.objects.filter(pk=request.user.responsable.id).first(),
        "user": request.user,
        "form":form,
    }
    return render(request,'disponibilites/account/edit_agent.html',context)

