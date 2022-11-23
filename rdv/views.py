from django.db.models.fields import NOT_PROVIDED
from django.shortcuts import render,redirect
from .form import RdvForm,OwnError
from .models import RendezVous,Service,Client,Responsable,Fichier,CreneauHoraire,ResponsableService
from django.db import transaction, IntegrityError
from datetime import date,time,timedelta
import datetime, random, string
from django.http import JsonResponse
from urba_project import settings
import urllib.request, json
from django.views.generic.edit import FormView
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from disponibilites.models import Evenement, Notification
import requests
#pour les messages flash
from django.contrib import messages
from django.core.files import File
from administration.models import JourSpecifique
from django.db.models import Q
import urllib3
from administration.ajax_methodes import envoyerMail, configureNotification,updateZimbraCal,updateZimbraCalDel
 
 #urllib3.disable_warnings()

# Create your views here

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

def home(request):
    rdvs = RendezVous.objects.all().order_by("-id")
    context = {
        "rdvs" : rdvs
    }
    return render(request,'rdv/home.html',context) 

def prendre_rdv(request):
    formulaire = RdvForm() 
    context = {
        'form': formulaire,
    }
    return render(request, 'rdv/nouveau.html',context)

def GetResponsable(request):
    # request should be ajax and method should be GET.
    if request.is_ajax and request.method == "GET":
        # get the nick name from the client side.
        id= request.GET.get("id", None)
        # check for the nick name in the database.
        service = Service.objects.filter(pk=id)
        if service.exists():
            service = service.first()
            responsable = service.responsable
            # if nick_name found return not valid new friend
            return JsonResponse({"nom":responsable.nom+" "+responsable.prenom,"tel":responsable.telephone,"email":responsable.email}, status = 200)
        else:
            # if nick_name not found, then user can create a new friend.
            return JsonResponse({"responsable":False}, status = 200)

    return JsonResponse({}, status = 400)

def AddRdv(request):
    context={}
    form = RdvForm(request.POST,request.FILES,error_class=OwnError)
    if form.is_valid() or not form.is_valid():
        email = form.cleaned_data['email']
        rdv = RendezVous()
        recaptcha_response = request.POST.get('g-recaptcha-response')
         #---- captcha -----#
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }        
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)       
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())    
        #---- process data  -----#
        if result: # if captcha is successful 
           pass
        else:
            messages.error(request,'Le captcha est obligatoire')
            context['form'] = form
            return render(request,'home.html',context)
        #---opérations formulaire---#
        try:
            test = False
            text=""
            with transaction.atomic():
                client = Client.objects.filter(email=email)
                if not client.exists():
                    test= True
                    client = Client.objects.create(
                            nom= form.cleaned_data['nom'],
                            prenom= form.cleaned_data['prenom'],
                            email= email,
                            telephone= form.cleaned_data['tel_number'],
                            adresse= form.cleaned_data['adress'],
                            password="".join([random.choice(string.ascii_letters) for _ in range(10)]) 
                        )
                else:
                    client = client.first()

                #recupération du service
                service = form.cleaned_data['service']

                #création du RDV
                rdv.date_r = form.cleaned_data['date']
                rdv.heure_r = form.cleaned_data['heure']
                rdv.nombre_personne =  form.cleaned_data['nombre_person']
                rdv.service = service
                rdv.client = client
                rdv.by_phone = form.cleaned_data['phone']
                rdv.urbanisme = form.cleaned_data['urbanisme']
                rdv.heure_f = form.cleaned_data['heureF']
                rdv.adresseTarvaux = form.cleaned_data['adresseTravaux']
                rs = ResponsableService.objects.filter(service=rdv.service.id)
                respo=[]
                ls=[]
                for r in rs:
                    respo.append(r.responsable.user.first_name+"-"+r.responsable.user.last_name+"-"+str(r.responsable.id))
                respo = sorted(respo)
                #controle de chevauchement
                if checkDate(rdv.date_r,rdv.heure_r,rdv.heure_f,rdv.by_phone): 
                    messages.error(request,"Attention il y a chevauchement de Rendez vous veuillez verifier vos horaires et recommencer")
                    context['form'] = form
                    return render(request,'home.html',context)
                #ajout du responsable
                r = selectResponsable(respo,rdv)
                if r != -1:
                    rdv.responsable = r
                else:
                    messages.error(request,"Attention plus de rendez-vous disponible à cette date")
                    context['form'] = form
                    return render(request,'home.html',context)
                #enregistrement de RDV

                rdv.save()

                  #try:
                if test:
                    nt = Notification()
                    nt = configureNotification("ajout_rdv",rdv)
                    envoyerMail(nt,[rdv.client.email], 'brunoowona12@gmail.com')
                    nt = configureNotification("ajout_administre",client)
                    envoyerMail(nt,[client.email], 'brunoowona12@gmail.com')
                else:
                    nt = Notification()
                    nt = configureNotification("ajout_rdv",rdv)
                    envoyerMail(nt,[rdv.client.email], '')
                  #except Exception as e:
                      #rdv.save()
                      #messages.error(request,str(e))
                    
                
                #recupération des fichiers    
                files_data = request.FILES.getlist('fichier')
                for fd in files_data:
                    fs = FileSystemStorage()
                    file_path = fs.save(fd.name,fd)
                    fichier = Fichier( fichier=file_path)
                    fichier.save()
                    rdv.fichiers.add(fichier)

                messages.success(request,"DEMANDE ENREGISTREE en attente de confirmation" )
                rdvs = RendezVous.objects.filter(client=rdv.client.id).order_by("-id")
                context = {
                    "rdvs" : rdvs
                }
                liste_destinataire = []
                services = ResponsableService.objects.filter(service=rdv.service.id)
                for service in services:
                    liste_destinataire.append(service.responsable.user.email)
                    
                #mise à jour du calendrier Zimbra
                code = updateZimbraCal(rdv)
                if code == 0:
                    return redirect ('index')
                
                if code == 10:
                    messages.error(request,"Problème avec le fichier RDV veuillez reéssayez ") 
                    return redirect ('index')

                if code != 200:
                    return redirect ('index')
            rdvs = RendezVous.objects.filter(client=rdv.client.id).order_by("-id")
            context = {
                    "rdvs" : rdvs
                }
            return redirect ('index')

        except IntegrityError:
            form.errors['internal'] = "Une érreur est apparue merci de reéssayer!!!"# do soemthing
        
    context['errors'] = form.errors.items()
    context['form'] = form
    return render(request,'home.html',context)

def getCreneaux(request):
    liste_lundi = []
    if request.is_ajax() and request.method == "GET":
        id= request.GET.get("service", None)
        date_e = request.GET.get("date",None)
        rdvi = request.GET.get("rdv",None)
        date_s = date_e.split("/")
        date_r = date(int(date_s[2]),int(date_s[0]),int(date_s[1]))
        service  = Service.objects.filter(pk=id).first()
        pause_d = timedelta(hours=12,minutes=0,seconds=0)
        pause_f = timedelta(hours=13,minutes=0,seconds=0)
        temps_duree = timedelta(hours=0,minutes=service.duree_rdv,seconds=0)
        if rdvi is not None:
            respo = RendezVous.objects.filter(pk=int(rdvi)).first().responsable
            JsL = JourSpecifique.objects.filter(date=date_r,service=service,responsable=respo)
            JsR = JourSpecifique.objects.filter(responsable=respo,date_debut__lte=date_r, date_fin__gte=date_r,service=service)
        else:
            JsL = JourSpecifique.objects.filter(date=date_r,service=service)
            JsR = JourSpecifique.objects.filter(date_debut__lte=date_r, date_fin__gte=date_r,service=service)

        if JsL.exists():
            for js in JsL:
                heure_fin = timedelta(hours=js.heure_fin.hour,minutes=js.heure_fin.minute,seconds=0)
                heure_debut = timedelta(hours=js.heure_debut.hour,minutes=js.heure_debut.minute,seconds=0)
                while heure_debut < heure_fin:
                    debut = heure_debut
                    heure_debut = heure_debut + temps_duree
                    if heure_debut > pause_d and heure_debut <= pause_f:
                        pass
                    else:
                        test = True
                        for l in liste_lundi:
                            if l["debut"]== str(debut.seconds//3600).zfill(2)+":"+str((debut.seconds//60)%60).zfill(2):
                                test = False
                                break
                        if test==True:
                            liste_lundi.append({
                                'debut':str(debut.seconds//3600).zfill(2)+":"+str((debut.seconds//60)%60).zfill(2),
                                'fin':str(heure_debut.seconds//3600).zfill(2)+":"+str((heure_debut.seconds//60)%60).zfill(2)
                            })
        if JsR.exists():
            for js in JsR:
                d = date_r.weekday()+1
                for n in js.jour_semaine:
                    if str(d) == n:
                        heure_fin = timedelta(hours=js.heure_fin.hour,minutes=js.heure_fin.minute,seconds=0)
                        heure_debut = timedelta(hours=js.heure_debut.hour,minutes=js.heure_debut.minute,seconds=0)
                        while heure_debut < heure_fin:
                            debut = heure_debut
                            heure_debut = heure_debut + temps_duree
                            if heure_debut > pause_d and heure_debut <= pause_f:
                                pass
                            else:
                                test = True
                                for l in liste_lundi:
                                    if l["debut"] == str(debut.seconds//3600).zfill(2)+":"+str((debut.seconds//60)%60).zfill(2):
                                        test = False
                                        break
                                if test == True:
                                    liste_lundi.append({
                                        'debut':str(debut.seconds//3600).zfill(2)+":"+str((debut.seconds//60)%60).zfill(2),
                                        'fin':str(heure_debut.seconds//3600).zfill(2)+":"+str((heure_debut.seconds//60)%60).zfill(2)
                                    })
        return JsonResponse({"reste":sorted(liste_lundi,key=lambda x: x['debut']),"bad":False}, status = 200)
    return JsonResponse({"bad":True}, status = 400)

#Méthode Ajax qui recupère les heures de RDV d'un jour et les jours spécifiques
def GetHorairesDuJour(request):
    date_e = request.GET.get("date",None)
    service = request.GET.get('service',None)
    liste_rdvP = []
    liste_rdvF = []
    liste_JsL = []
    liste_JsR = []
    date_s = date_e.split("/")
    date_p = date(int(date_s[2]),int(date_s[1]),int(date_s[0]))
    RdvP = RendezVous.objects.filter(date_r = date_p,by_phone=False)
    RdvF = RendezVous.objects.filter(date_r = date_p,by_phone=True)
    JsL = JourSpecifique.objects.filter(date=date_p,service=service)
    JsR = JourSpecifique.objects.filter(date_debut__lte=date_p, date_fin__gte=date_p,service=service)
    if RdvP.exists():
        for rdv in RdvP:
            strt = str(rdv.heure_r.hour).zfill(2)+":"+str(rdv.heure_r.minute).zfill(2)+":"+str(rdv.heure_r.second).zfill(2) 
            fin = str(rdv.heure_f.hour).zfill(2)+":"+str(rdv.heure_f.minute).zfill(2)+":"+str(rdv.heure_f.second).zfill(2)   
            liste_rdvP.append({
                'start':strt,
                'end':fin
            })
    if RdvF.exists():
        for rdv in RdvF:
            strt = str(rdv.heure_r.hour).zfill(2)+":"+str(rdv.heure_r.minute).zfill(2)+":"+str(rdv.heure_r.second).zfill(2) 
            fin = str(rdv.heure_f.hour).zfill(2)+":"+str(rdv.heure_f.minute).zfill(2)+":"+str(rdv.heure_f.second).zfill(2)   
            liste_rdvF.append({
                'start':strt,
                'end':fin
            })
    if JsR.exists():
        for Js in JsR:
            strt = str(Js.heure_debut.hour).zfill(2)+":"+str(Js.heure_debut.minute).zfill(2)+":"+str(Js.heure_debut.second).zfill(2) 
            fin = str(Js.heure_fin.hour).zfill(2)+":"+str(Js.heure_fin.minute).zfill(2)+":"+str(Js.heure_fin.second).zfill(2)
            liste_JsR.append({
                'start':strt,
                'end':fin
            })
    else:
        liste_JsR= 0
    if JsL.exists():
        for Js in JsL:
            strt = str(Js.heure_debut.hour).zfill(2)+":"+str(Js.heure_debut.minute).zfill(2)+":"+str(Js.heure_debut.second).zfill(2) 
            fin = str(Js.heure_fin.hour).zfill(2)+":"+str(Js.heure_fin.minute).zfill(2)+":"+str(Js.heure_fin.second).zfill(2)
            liste_JsL.append({
                'start':strt,
                'end':fin
            })
    else:
        liste_JsL= 0

    return JsonResponse({"rdvP":liste_rdvP,"rdvF":liste_rdvF,"reccurence":liste_JsR,"lineaire":liste_JsL}, status = 200)

#verification de rdv et construction des créneaux disponibles
def checkDate(date,heure_deb,heure_fin,phone):
    rdv = RendezVous.objects.filter(date_r = date)
    for rd in rdv:
        heure_Deb = timedelta(hours=heure_deb.hour,minutes=heure_deb.minute,seconds=heure_deb.second)
        heure_Fin = timedelta(hours=heure_fin.hour,minutes=heure_fin.minute,seconds=heure_fin.second)
        rdvD =  timedelta(hours=rd.heure_r.hour,minutes=rd.heure_r.minute,seconds=rd.heure_r.second)
        rdvF =  timedelta(hours=rd.heure_f.hour,minutes=rd.heure_f.minute,seconds=rd.heure_f.second)
        if (heure_Deb >= rdvD and heure_Deb <= rdvF) or (heure_Fin >= rdvD and heure_Fin <= rdvF):
            if rd.by_phone == phone:
                return True
    return False

#méthode ajax de récupération eds responsables de service
def GetResponsableService(request):
    service = request.GET.get('service',None)
    responsable_liste = []
    if request.is_ajax and request.method == "GET":
        serv = ResponsableService.objects.filter(service=service)
        if serv.exists():
            for se in serv:
                responsable_liste.append({
                    'id':se.responsable.id,
                    'nom':se.responsable.user.last_name,
                    'prenom':se.responsable.user.first_name
                })
    return JsonResponse({"agent":responsable_liste}, status = 200)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

#méthode pour collectionner les jours libres
def buildFreeDate(request):
    service = request.GET.get('service',None)
    service = Service.objects.filter(pk=int(service)).first()
    respo = ResponsableService.objects.filter(service=service)
    responsable=[]
    today =  datetime.datetime.now()
    today +=timedelta(days=8)
    duree = service.duree_rdv -1
    list_free_day=[]
    
    if respo.exists():
        for res in respo:
            responsable.append(res.responsable)
        for res in responsable:
            js = JourSpecifique.objects.filter(date__gte=today,responsable=res,service=service)
            jsr = JourSpecifique.objects.filter(date_debut__gte=today,responsable=res,service=service)
            for j in js:
                ouverture = datetime.datetime(today.year,today.month,today.day,j.heure_debut.hour,j.heure_debut.minute)
                fermeture = datetime.datetime(today.year,today.month,today.day,j.heure_fin.hour,j.heure_fin.minute)
                while ouverture < fermeture:
                    if ouverture.hour != 12 and ouverture.hour != 13:
                        Rdv = RendezVous.objects.filter(Q(heure_r__gte=ouverture,heure_r__lte=fermeture)  | Q(heure_f__gte=ouverture,heure_f__lte=fermeture),date_r=j.date,responsable=res,by_phone=True)
                        RdvP = RendezVous.objects.filter(Q(heure_r__gte=ouverture,heure_r__lte=fermeture)  | Q(heure_f__gte=ouverture,heure_f__lte=fermeture),date_r=j.date,responsable=res,by_phone=False)
                        conge = Evenement.objects.filter(date_d__gte=j.date,date_f__lte=j.date, responsable=res)
                        if Rdv.exists() or RdvP.exists():
                            pass
                        elif conge.exists():
                            pass
                        else :
                            if j.date not in list_free_day:
                                list_free_day.append(j.date)
                    ouverture += timedelta(minutes=duree)
            for j in jsr:
                day=["1","2","3","4","5"]
                for single_date in daterange(j.date_debut,j.date_fin):
                    for n in j.jour_semaine:
                        if n in day:
                            if (int(n)-1)==single_date.weekday():
                                ouverture = datetime.datetime(today.year,today.month,today.day,j.heure_debut.hour,j.heure_debut.minute)
                                fermeture = datetime.datetime(today.year,today.month,today.day,j.heure_fin.hour,j.heure_fin.minute)
                                while ouverture < fermeture:
                                    if ouverture.hour != 12 and ouverture.hour != 13:
                                        Rdv = RendezVous.objects.filter(Q(heure_r__gte=ouverture,heure_r__lte=fermeture)  | Q(heure_f__gte=ouverture,heure_f__lte=fermeture),date_r=single_date,responsable=res,by_phone=True)
                                        RdvP = RendezVous.objects.filter(Q(heure_r__gte=ouverture,heure_r__lte=fermeture)  | Q(heure_f__gte=ouverture,heure_f__lte=fermeture),date_r=single_date,responsable=res,by_phone=False)
                                        conge = Evenement.objects.filter(responsable=res,date_d__gte=j.date,date_f__lte=j.date)
                                        if Rdv.exists() and RdvP.exists():
                                            pass
                                        elif conge.exists():
                                            pass
                                        else :
                                            if j.date not in list_free_day:
                                                list_free_day.append(j.date)
                                    ouverture += timedelta(minutes=duree)
    else:
        return JsonResponse({"date":list_free_day}, status = 200)
    return JsonResponse({"date":list_free_day}, status = 200)
    """today =  datetime.datetime.now()
    today +=timedelta(days=8)
    today =  date(today.year,today.month,today.day)
    service = Service.objects.all()
    js = JourSpecifique.objects.filter(date__gte=today)
    jsr = JourSpecifique.objects.filter(date_debut__gte=today)
    list_free_day=[]
    for j in js:
        ouverture = datetime.datetime(today.year,today.month,today.day,j.heure_debut.hour,j.heure_debut.minute)
        fermeture = datetime.datetime(today.year,today.month,today.day,j.heure_fin.hour,j.heure_fin.minute)
        for ser in service:
            duree = ser.duree_rdv
            while ouverture < fermeture:
                if ouverture.hour != 12 and ouverture.hour != 13:
                    Rdv = RendezVous.objects.filter(Q(heure_r__gte=ouverture,heure_r__lte=fermeture)  | Q(heure_f__gte=ouverture,heure_f__lte=fermeture),date_r=j.date,by_phone=True)
                    RdvP = RendezVous.objects.filter(Q(heure_r__gte=ouverture,heure_r__lte=fermeture)  | Q(heure_f__gte=ouverture,heure_f__lte=fermeture),date_r=j.date,by_phone=False)
                    conge = Evenement.objects.filter(date_d__gte=j.date,date_f__lte=j.date)
                    if Rdv.exists() and RdvP.exists():
                        pass
                    elif conge.exists():
                        conge=conge.first()
                        respo = conge.responsable
                        respoS = ResponsableService.objects.all()
                        for r in respoS:
                            if r.responsable != respo and r.service == j.service:
                                if j.date not in list_free_day:
                                    list_free_day.append(j.date)

                    else :
                        if j.date not in list_free_day:
                            list_free_day.append(j.date)
                ouverture += timedelta(minutes=duree)
    for j in jsr:
            day=["1","2","3","4","5"]
            for single_date in daterange(j.date_debut,j.date_fin):
                for n in j.jour_semaine:
                    if n in day:
                        if (int(n)-1)==single_date.weekday():
                            ouverture = datetime.datetime(today.year,today.month,today.day,j.heure_debut.hour,j.heure_debut.minute)
                            fermeture = datetime.datetime(today.year,today.month,today.day,j.heure_fin.hour,j.heure_fin.minute)
                            for ser in service:
                                duree = ser.duree_rdv
                                while ouverture < fermeture:
                                    if ouverture.hour != 12 and ouverture.hour != 13:
                                        Rdv = RendezVous.objects.filter(Q(heure_r__gte=ouverture,heure_r__lte=fermeture)  | Q(heure_f__gte=ouverture,heure_f__lte=fermeture),date_r=j.date,by_phone=True)
                                        RdvP = RendezVous.objects.filter(Q(heure_r__gte=ouverture,heure_r__lte=fermeture)  | Q(heure_f__gte=ouverture,heure_f__lte=fermeture),date_r=j.date,by_phone=False)
                                        conge = Evenement.objects.filter(date_d__gte=j.date,date_f__lte=j.date)
                                        if Rdv.exists() and RdvP.exists():
                                            pass
                                        elif conge.exists():
                                            conge=conge.first()
                                            respo = conge.responsable
                                            respoS = ResponsableService.objects.all()
                                            for r in respoS:
                                                if r.responsable != respo and r.service == j.service:
                                                    if j.date not in list_free_day:
                                                        list_free_day.append(j.date)
                                        else :
                                            if j.date not in list_free_day:
                                                list_free_day.append(j.date)
                                    ouverture += timedelta(minutes=duree)
    return JsonResponse({"date":list_free_day}, status = 200)"""

def checkIfAgentBusy(request):
    responsable = request.GET.get('responsable',None)
    debut = request.GET.get('debut',None)
    service = request.GET.get('service',None)
    date_ = request.GET.get('date',None)
    date_ = date_.split("-")
    date_ = date(int(date_[0]),int(date_[1]),int(date_[2]))
    debut = debut.split(":")
    debut = time(int(debut[0]),int(debut[1]),0)
    if responsable != '':
        responsable = Responsable.objects.filter(pk=int(responsable)).first()
        service = Service.objects.filter(pk=int(service)).first()
        rdv = RendezVous.objects.filter(responsable=responsable,service=service,date_r=date_,heure_r=debut)
        if rdv.exists():
            return JsonResponse({"existant":"oui"},status = 200)
    return JsonResponse({"existant":"non"},status = 200)

#methode pour verifier si on peut encore ajouter un RDV sur un créneaux déjà occupé au cas où on a deux jours spécfique qui coincide
def checkIfCreneauAvailable(request):
    if request.is_ajax():
        service = request.GET.get('service',None)
        date_ = request.GET.get('date',None)
        debut = request.GET.get('debut',None)
        fin = request.GET.get('fin',None)
        #recupération des variables
        service = Service.objects.filter(pk=int(service)).first()
        date_ = date(int(date_.split('/')[2]),int(date_.split('/')[1]),int(date_.split('/')[0]))
        debut = debut.split(":")
        debut = time(int(debut[0]),int(debut[1]),0)
        #fin = debut.split(":")
        #fin = time(int(fin[0]),int(fin[1]),0)
        duree = service.duree_rdv
        testJs=True
        testJr=True
        rdv = RendezVous.objects.filter(date_r=date_,heure_r=debut,heure_f=fin,service=service)
        if rdv.exists():
            rdv = rdv.first()
            respo_serv = ResponsableService.objects.filter(service=service)
            for res in respo_serv:
                if res.responsable.id != rdv.responsable.id:
                    conge = Evenement.objects.filter(responsable=res.responsable,date_d__lte=date_,date_f__gte=date_)
                    if conge.exists():
                        return JsonResponse({"reponse":"bad"},status=200) 
                    js = JourSpecifique.objects.filter(date=date_,responsable=res.responsable,service=service)
                    jsr = JourSpecifique.objects.filter(date_debut__lte=date_,date_fin__gte=date_,responsable=res.responsable,service=service)
                    if js.exists():
                        for j in js:
                            ouverture = datetime.datetime(date_.year,date_.month,date_.day,j.heure_debut.hour,j.heure_debut.minute)
                            fermeture = datetime.datetime(date_.year,date_.month,date_.day,j.heure_fin.hour,j.heure_fin.minute)
                            while ouverture < fermeture:
                                if ouverture.time() == debut and fermeture.time():
                                    return JsonResponse({"reponse":"ok"},status=200)
                                ouverture += timedelta(minutes=duree)
                            testJs = False
                    else:
                        testJs = False
                    if jsr.exists():
                        for j in jsr:
                            for single_date in daterange(j.date_debut,j.date_fin):
                                if single_date==date_ and str((date_.weekday()+1)) in j.jour_semaine:
                                    #return JsonResponse({"jour semaine":j.jour_semaine,"day":date_.weekday()+1,"single_date":single_date,"auday":date_,"debut":j.date_debut,"fin":j.date_fin},status=200)
                                    ouverture = datetime.datetime(date_.year,date_.month,date_.day,j.heure_debut.hour,j.heure_debut.minute)
                                    fermeture = datetime.datetime(date_.year,date_.month,date_.day,j.heure_fin.hour,j.heure_fin.minute)
                                    while ouverture < fermeture:
                                        if ouverture.time() == debut and fermeture.time():
                                            return JsonResponse({"reponse":"ok"},status=200)
                                        ouverture += timedelta(minutes=duree)
                                    testJr = False
                        testJr = False
                    else:
                        testJr = False
            if testJs==False and testJr == False:
                return JsonResponse({"reponse":"bad"},status=200)
        else:
            respoS = ResponsableService.objects.filter(service=service)
            for r in respoS:
                conge = Evenement.objects.filter(responsable=r.responsable,date_d__lte=date_,date_f__gte=date_)
                if not conge.exists():
                    js = JourSpecifique.objects.filter(heure_debut__lte=debut,heure_fin__gte=fin,date=date_,responsable=r.responsable,service=service)
                    jsr = JourSpecifique.objects.filter(heure_debut__lte=debut,heure_fin__gte=fin,date_debut__lte=date_,date_fin__gte=date_,responsable=r.responsable,service=service)
                    if js.exists():
                        return JsonResponse({"reponse":"ok"},status=200)
                    if jsr.exists():
                        for j in jsr:
                            for single_date in daterange(j.date_debut,j.date_fin):
                                if single_date==date_ and str((date_.weekday()+1)) in j.jour_semaine:
                                    return JsonResponse({"reponse":"ok"},status=200)
            return JsonResponse({"reponse":"bad"},status=200)
    return JsonResponse({"reponse":"erreur"},status=200)

def selectResponsable(liste_respo,rdv):
    for res in liste_respo:
        respo = Responsable.objects.filter(pk=int(res.split('-')[2])).first()
        js = JourSpecifique.objects.filter(date=rdv.date_r,responsable=respo,service=rdv.service)
        jsr = JourSpecifique.objects.filter(date_debut__lte=rdv.date_r,date_fin__gte=rdv.date_r,responsable=respo,service=rdv.service)
        if js.exists():
            for j in js:
                ouverture = datetime.datetime(rdv.date_r.year,rdv.date_r.month,rdv.date_r.day,j.heure_debut.hour,j.heure_debut.minute)
                fermeture = datetime.datetime(rdv.date_r.year,rdv.date_r.month,rdv.date_r.day,j.heure_fin.hour,j.heure_fin.minute)
                while ouverture < fermeture:
                    if ouverture.time() == rdv.heure_r and fermeture.time():
                        rdvt = RendezVous.objects.filter(responsable=respo,service=rdv.service,date_r=rdv.date_r,heure_r=ouverture.time())
                        if not rdvt.exists():
                            return respo
                    ouverture += timedelta(minutes=rdv.service.duree_rdv)
        if jsr.exists():
            for j in jsr:
                for single_date in daterange(j.date_debut,j.date_fin):
                    if single_date==rdv.date_r and str((rdv.date_r.weekday()+1)) in j.jour_semaine:
                        ouverture = datetime.datetime(rdv.date_r.year,rdv.date_r.month,rdv.date_r.day,j.heure_debut.hour,j.heure_debut.minute)
                        fermeture = datetime.datetime(rdv.date_r.year,rdv.date_r.month,rdv.date_r.day,j.heure_fin.hour,j.heure_fin.minute)
                        while ouverture < fermeture:
                            if ouverture.time() == rdv.heure_r and fermeture.time():
                                rdvt = RendezVous.objects.filter(responsable=respo,service=rdv.sevice,date_r=rdv.date_r,heure_r=ouverture.time())
                                if not rdvt.exists():
                                    return respo
                            ouverture += timedelta(minutes=rdv.service.duree_rdv)
    return -1
        
def getAllAdresse(request):
    user_ = request.GET.get('administre',None)
    id_= request.GET.get('id',None)
    
    if id_ is not None:
        user_ = Client.objects.filter(pk=id_)
    else:
        user_ = Client.objects.filter(email=user_)
    if user_.exists():
        user_ = user_.first()
        rdvs = RendezVous.objects.filter(client = user_.id)
        finalList= []
        if rdvs.exists():
            for rdv in rdvs:
                if  rdv.adresseTarvaux not in finalList:
                    finalList.append({
                        'adresse': rdv.adresseTarvaux,
                    })
            return JsonResponse({"adresses":finalList},status=200)
    return JsonResponse({"adresses":"0"},status=200)


    









       
    