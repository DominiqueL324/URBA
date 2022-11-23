from disponibilites.models import Notification
from django.core.files.storage import FileSystemStorage
from rdv.models import Fichier, RendezVous,Client
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Adjoint,JourSpecifique,Administrateur
from rdv.models import Responsable
from django.contrib import messages
from disponibilites.form import  ResponsableForm
from django.contrib.auth.models import User, Group
from django.db import transaction, IntegrityError
import datetime, random, string
from django.http import JsonResponse, response
from django.core.mail import send_mail
from django.db.models import Q
from datetime import date, datetime,time,timedelta
from django.core.files import File
import requests
import shutil
from des import *
import os
from django.core.mail import EmailMessage
import urllib3

urllib3.disable_warnings()

#récupération des RDV pour tableau de bord adj/adm
def getRDvForAdjSup(request):
    id = request.GET.get('man',None)
    rdv = RendezVous.objects.none()
    final_ = []
    if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists()  :
        if  int(id) == 1:
            rdv = RendezVous.objects.filter(etat="En attente")
        elif int(id)== 2:
            rdv = RendezVous.objects.filter(etat="Approuve")
        elif int(id)==3:
            rdv = RendezVous.objects.filter(etat="Annule")
        else:
            rdv = RendezVous.objects.all()
    else :
        if  int(id) == 1:
            rdv = RendezVous.objects.filter(etat="En attente",responsable=request.user.responsable.id)
        elif int(id)== 2:
            rdv = RendezVous.objects.filter(etat="Approuve",responsable=request.user.responsable.id)
        elif int(id)==3:
            rdv = RendezVous.objects.filter(etat="Annule",responsable=request.user.responsable.id)
        else:
            rdv = RendezVous.objects.filter(responsable=request.user.responsable.id)

    col = ""
    for rd in rdv:
        if rd.by_phone:
            col = "#e4c935"
        else :
            col ="#37f771"

        final_.append({
            "id":rd.id,
            "debut":str(rd.date_r.year)+"-"+str(rd.date_r.month).zfill(2)+"-"+str(rd.date_r.day).zfill(2)+"T"+str(rd.heure_r.hour).zfill(2)+":"+str(rd.heure_r.minute).zfill(2)+"00",
            "fin":str(rd.date_r.year)+"-"+str(rd.date_r.month).zfill(2)+"-"+str(rd.date_r.day).zfill(2)+"T"+str(rd.heure_f.hour).zfill(2)+":"+str(rd.heure_f.minute).zfill(2)+"00",
            "titre":"Agent : "+rd.responsable.user.first_name +" \nAdministré : "+rd.client.nom+" \nService : "+rd.service.nom,
            "couler":col
        })
    return JsonResponse({"liste": final_}, status=200)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>Module Agenda
def dashBoardAgenda(request):
    return render(request,'administration/agenda/agenda.html')

#recupération de la liste des administré
def getAllAdministre(request):
    id = request.GET.get('id',None)
    final_= []
    if request.is_ajax and request.method == "GET":
        clts = Client.objects.all()
        man = JourSpecifique.objects.filter(pk=id).first().responsable
        temp = JourSpecifique.objects.filter(pk=id).first().service.duree_rdv
        for cl in clts:
            final_.append({
                'id':cl.id,
                'nom':cl.nom+" "+cl.prenom
            })
        return JsonResponse({"temps":temp,"administres": final_,"agent":man.user.first_name+" "+man.user.last_name}, status=200)
    else:
        return JsonResponse({"Bad": 0}, status=200)
    return JsonResponse({"Bad": 0}, status=200)

#ajout d'un rdv Ajax
def addRdvAjax(request):
    administre = Client.objects.filter(pk=int(request.POST.get("administre",None))).first()
    Jour_s = JourSpecifique.objects.filter(pk=int(request.POST.get("js",None))).first()
    dates = request.POST.get('date',None)
    debut = request.POST.get('debut',None)
    fin = request.POST.get('fin',None)
    phone = request.POST.get('telephone',None)
    personne = request.POST.get('personne',None)
    taille = request.POST.get('taille',None)
    adresse = request.POST.get('adresseTravauxInput',None)
    if request.is_ajax and request.method == "POST":
        rdv = RendezVous()
        rdv.client = administre
        rdv.service = Jour_s.service
        rdv.responsable = Jour_s.responsable
        rdv.by_phone = True if phone=="oui" else False
        rdv.nombre_personne = personne
        d1 = dates.split('-')
        d = date(int(d1[0]),int(d1[1]),int(d1[2]))
        rdv.date_r = d
        hd = debut.split(":")
        heure_debut = time(int(hd[0]),int(hd[1]),0)
        hd = fin.split(":")
        heure_fin = time(int(hd[0]),int(hd[1]),0)
        rdv.heure_f = heure_fin
        rdv.heure_r =  heure_debut
        #verification du chevauchement
        rdv_c = RendezVous.objects.filter(Q(heure_r__gte=rdv.heure_r,heure_r__lte=rdv.heure_f)  | Q(heure_f__gt=rdv.heure_r,heure_f__lte=rdv.heure_f), date_r=rdv.date_r,by_phone=rdv.by_phone)
        if rdv_c.exists():
            return JsonResponse({"existant":1},status=200)
        rdv_c = RendezVous.objects.filter(Q(heure_r__gte=rdv.heure_r,heure_r__lte=rdv.heure_f)  | Q(heure_f__gt=rdv.heure_r,heure_f__lte=rdv.heure_f), date_r=rdv.date_r,responsable=rdv.responsable)
        if rdv_c.exists():
            return JsonResponse({"existant":1},status=200)
        rdv.adresseTarvaux = adresse
        rdv.save()

        #recupération des fichiers
        for i in range(int(taille)):
            files_data = request.FILES.getlist('fichiers'+str(i))
            for fd in files_data:
                fs = FileSystemStorage()
                file_path = fs.save(fd.name, fd)
                fichier = Fichier(fichier=file_path)
                fichier.save()
                rdv.fichiers.add(fichier)

        #mise à jour du calendrier Zimbra
        code = updateZimbraCal(rdv)
        nt = Notification()
        nt = configureNotification("ajout_rdv",rdv)
        envoyerMail(nt,[rdv.client.email], 'brunoowona12@gmail.com')
        messages.success(request,'Rendez-vous ajouté avec succès')
        return JsonResponse({"good":1},status=200)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>Module notification
def dashBoardNotification(request):
    return render(request, 'administration/notifications/notifications.html')

#ajout d'une noticifation 
def addNotificationMails(request):
    cas = request.POST.get('cas',None)
    body = request.POST.get('body',None)
    sujet = request.POST.get('sujet',None)
    if request.is_ajax and request.method =="POST":
        notif = Notification()
        notif.body = body
        notif.cas = cas
        notif.sujet =  sujet
        notif.save()
        messages.success(request,'Notification Enregistrez avec success')
        return JsonResponse({"god":"ok"},status=200)
    return JsonResponse({"bad":"ok"},status=200)

#configuartion de notification
def configureNotification(cas,obj,pwd=""):
    notif = Notification.objects.filter(cas=cas)
    nt = Notification()
    if type(obj) is RendezVous:
        for noti in notif:
            noti.sujet = noti.sujet.replace("%rdv_date%",str(obj.date_r.day).zfill(2) + '/' +str(obj.date_r.month).zfill(2) + '/' +str(obj.date_r.year))
            noti.sujet = noti.sujet.replace("%rdv_heure_debut%",str(obj.heure_r.hour).zfill(2) + ':' +str(obj.heure_r.minute).zfill(2))
            noti.sujet = noti.sujet.replace("%rdv_heure_fin%",str(obj.heure_f.hour).zfill(2) + ':' +str(obj.heure_f.minute).zfill(2))
            noti.sujet = noti.sujet.replace("%service_nom%",obj.service.nom)
            noti.sujet = noti.sujet.replace("%rdv_adresse_travaux%",obj.adresseTarvaux)
            noti.sujet = noti.sujet.replace("%agent_nom%",obj.responsable.user.last_name)
            noti.sujet = noti.sujet.replace("%agent_prenom%",obj.responsable.user.first_name)
            noti.sujet = noti.sujet.replace("%agent_email%",obj.responsable.user.email)
            noti.sujet = noti.sujet.replace("%agent_telephone%",str(obj.responsable.telephone))
            noti.sujet = noti.sujet.replace("%agent_mot_de_passe%",pwd)
            noti.sujet = noti.sujet.replace("%administre_nom%",obj.client.nom)
            noti.sujet = noti.sujet.replace("%administre_prenom%",obj.client.prenom)
            noti.sujet = noti.sujet.replace("%administre_adresse%",obj.client.adresse)
            noti.sujet = noti.sujet.replace("%administre_email%",obj.client.email)
            noti.sujet = noti.sujet.replace("%administre_telephone%",str(obj.client.telephone))
            noti.sujet = noti.sujet.replace("%administre_mot_de_passe%",obj.client.password)

            noti.body = noti.body.replace("%rdv_date%",str(obj.date_r.day).zfill(2) + '/' +str(obj.date_r.month).zfill(2) + '/' +str(obj.date_r.year))
            noti.body = noti.body.replace("%rdv_heure_debut%",str(obj.heure_r.hour).zfill(2) + ':' +str(obj.heure_r.minute).zfill(2))
            noti.body = noti.body.replace("%rdv_heure_fin%",str(obj.heure_f.hour).zfill(2) + ':' +str(obj.heure_f.minute).zfill(2))
            noti.body = noti.body.replace("%service_nom%",obj.service.nom)
            noti.body = noti.body.replace("%rdv_adresse_travaux%",obj.adresseTarvaux)
            noti.body = noti.body.replace("%agent_nom%",obj.responsable.user.last_name)
            noti.body = noti.body.replace("%agent_prenom%",obj.responsable.user.first_name)
            noti.body = noti.body.replace("%agent_email%",obj.responsable.user.email)
            noti.body = noti.body.replace("%agent_telephone%",str(obj.responsable.telephone))
            noti.body = noti.body.replace("%agent_mot_de_passe%",pwd)
            noti.body = noti.body.replace("%administre_nom%",obj.client.nom)
            noti.body = noti.body.replace("%administre_prenom%",obj.client.prenom)
            noti.body = noti.body.replace("%administre_adresse%",obj.client.adresse)
            noti.body = noti.body.replace("%administre_email%",obj.client.email)
            noti.body = noti.body.replace("%administre_telephone%",str(obj.client.telephone))
            noti.body = noti.body.replace("%administre_mot_de_passe%",obj.client.password)
            nt = noti
    if type(obj) is Client:
        for noti in notif:
            noti.sujet = noti.sujet.replace("%administre_nom%",obj.nom)
            noti.sujet = noti.sujet.replace("%administre_prenom%",obj.prenom)
            noti.sujet = noti.sujet.replace("%administre_adresse%",obj.adresse)
            noti.sujet = noti.sujet.replace("%administre_email%",obj.email)
            noti.sujet = noti.sujet.replace("%administre_login%",obj.email)
            noti.sujet = noti.sujet.replace("%administre_telephone%",str(obj.telephone))
            noti.sujet = noti.sujet.replace("%administre_mot_de_passe%",obj.password)

            noti.body = noti.body.replace("%administre_nom%",obj.nom)
            noti.body = noti.body.replace("%administre_prenom%",obj.prenom)
            noti.body = noti.body.replace("%administre_adresse%",obj.adresse)
            noti.body = noti.body.replace("%administre_email%",obj.email)
            noti.body = noti.body.replace("%administre_telephone%",str(obj.telephone))
            noti.body = noti.body.replace("%administre_login%",str(obj.email))
            noti.body = noti.body.replace("%administre_mot_de_passe%",obj.password)
            nt = noti
    
    if type(obj) is Adjoint:
        for noti in notif:
            noti.sujet = noti.sujet.replace("%adjoint_nom%",obj.user.last_name)
            noti.sujet = noti.sujet.replace("%adjoint_prenom%",obj.user.first_name)
            noti.sujet = noti.sujet.replace("%adjoint_email%",obj.user.email)
            noti.sujet = noti.sujet.replace("%adjoint_login%",obj.user.username)
            noti.sujet = noti.sujet.replace("%adjoint_telephone%",str(obj.telephone))
            noti.sujet = noti.sujet.replace("%adjoint_role%","Adjoint")
            
            noti.body = noti.body.replace("%adjoint_nom%",obj.user.last_name)
            noti.body = noti.body.replace("%adjoint_role%","Adjoint")
            noti.body = noti.body.replace("%adjoint_prenom%",obj.user.first_name)
            noti.body = noti.body.replace("%adjoint_login%",obj.user.username)
            noti.body = noti.body.replace("%adjoint_email%",obj.user.email)
            noti.body = noti.body.replace("%adjoint_telephone%",str(obj.telephone))

            noti.sujet = noti.sujet.replace("%superviseur_nom%",obj.user.last_name)
            noti.sujet = noti.sujet.replace("%superviseur_prenom%",obj.user.first_name)
            noti.sujet = noti.sujet.replace("%superviseur_login%",obj.user.username)
            noti.sujet = noti.sujet.replace("%superviseur_email%",obj.user.email)
            noti.sujet = noti.sujet.replace("%superviseur_telephone%",str(obj.telephone))
            noti.sujet = noti.sujet.replace("%superviseur_role%","Superviseur")
            
            noti.body = noti.body.replace("%superviseur_nom%",obj.user.last_name)
            noti.body = noti.body.replace("%superviseur_prenom%",obj.user.first_name)
            noti.body = noti.body.replace("%superviseur_login%",obj.user.username)
            noti.body = noti.body.replace("%superviseur_email%",obj.user.email)
            noti.body = noti.body.replace("%superviseur_telephone%",str(obj.telephone))
            noti.body = noti.body.replace("%superviseur_role%","Superviseur")

            noti.body = noti.body.replace("%adjoint_mot_de_passe%",pwd)
            noti.sujet = noti.sujet.replace("%adjoint_mot_de_passe%",pwd)
            noti.body = noti.body.replace("%superviseur_mot_de_passe%",pwd)
            noti.sujet = noti.sujet.replace("%superviseur_mot_de_passe%",pwd)

            nt = noti
    
    if type(obj) is Administrateur:
        for noti in notif:
            noti.sujet = noti.sujet.replace("%administrateur_nom%",obj.user.last_name)
            noti.sujet = noti.sujet.replace("%administrateur_prenom%",obj.user.first_name)
            noti.sujet = noti.sujet.replace("%administrateur_email%",obj.user.email)
            noti.sujet = noti.sujet.replace("%administrateur_login%",obj.user.username)
            noti.sujet = noti.sujet.replace("%administrateur_telephone%",str(obj.telephone))
            
            noti.body = noti.body.replace("%administrateur_nom%",obj.user.last_name)
            noti.body = noti.body.replace("%administrateur_prenom%",obj.user.first_name)
            noti.body = noti.body.replace("%administrateur_email%",obj.user.email)
            noti.body = noti.body.replace("%administrateur_login%",obj.user.username)
            noti.body = noti.body.replace("%administrateur_telephone%",str(obj.telephone))

            noti.body = noti.body.replace("%administrateur_mot_de_passe%",pwd)
            noti.sujet = noti.sujet.replace("%administrateur_mot_de_passe%",pwd)
            nt = noti

    if type(obj) is Responsable:
        for noti in notif:
            noti.sujet = noti.sujet.replace("%agent_nom%",obj.user.last_name)
            noti.sujet = noti.sujet.replace("%agent_prenom%",obj.user.first_name)
            noti.sujet = noti.sujet.replace("%agent_email%",obj.user.email)
            noti.sujet = noti.sujet.replace("%agent_login%",obj.user.username)
            noti.sujet = noti.sujet.replace("%agent_telephone%",str(obj.telephone))
            
            noti.body = noti.body.replace("%agent_nom%",obj.user.last_name)
            noti.body = noti.body.replace("%agent_prenom%",obj.user.first_name)
            noti.body = noti.body.replace("%agent_email%",obj.user.email)
            noti.body = noti.body.replace("%agent_login%",obj.user.username)
            noti.body = noti.body.replace("%agent_telephone%",str(obj.telephone))

            noti.body = noti.body.replace("%agent_mot_de_passe%",pwd)
            noti.sujet = noti.sujet.replace("%agent_mot_de_passe%",pwd)
            nt = noti
    return nt

def envoyerMail(nt,destinataire,expediteur):
    data_ = {
        "sujet":nt.sujet,
        "from_mail":"ne-pas-repondre@saint-medard-en-jalles.fr",
        "recipient":destinataire[0]+",",
        "html_body":nt.body,
        "email_host_user":"ne-pas-repondre@saint-medard-en-jalles.fr",
        "email_host_password":"@XB58fk33",
        "content":" "
    }
    token = requests.post("https://reservation.saint-medard-en-jalles.fr:4443/mail/send",data=data_,verify=False)
    #return token
    """send_mail(
                nt.sujet,  #subject
                " ", 
                "ne-pas-repondre@saint-medard-en-jalles.fr",#from_mail
                destinataire,  #recipient list []
                fail_silently=True,  #fail_silently
                html_message=nt.body
                )"""

#recuperation de la dernière notification 
def getLastNotification(request):
    cas = request.GET.get('cas',None)
    final_ =[]
    if request.is_ajax and request.method == 'GET':
        nts = Notification.objects.filter(cas=cas)
        if nts.exists():
            for nt in nts:
                final_.append({
                    "sujet": nt.sujet,
                    "body":nt.body
                })
            return JsonResponse({"notification" : final_}, status=200)
        return JsonResponse({"notification" : 0}, status=200)
    return JsonResponse({"notification" : 0}, status=200)


def updateZimbraCal(rdv):
    oday1= date(rdv.date_r.year,rdv.date_r.month,rdv.date_r.day).isoformat()
    base = oday1.replace("-","")
    oday1 = base+"T"+str(rdv.heure_r.hour).zfill(2)+str(rdv.heure_r.minute).zfill(2)+str(58)
    oday2 = base+"T"+str(rdv.heure_f.hour).zfill(2)+str(rdv.heure_f.minute).zfill(2)+str(58)
    strs = ""
    title=""
    if rdv.by_phone == "True" or rdv.by_phone:
        title = "Rendez-vous téléphonique avec "+ rdv.responsable.user.last_name+ " "+rdv.responsable.user.first_name+" au service "+rdv.service.nom
        strs = "Vous avez une demande rendez-vous  téléphonique au service "+rdv.service.nom +" avec "+ rdv.client.nom+ " "+rdv.client.prenom+" \\n le mail de réponse est: ne-pas-repondre@saint-medard-en-jalles.fr"
    if rdv.by_phone == "False" or not rdv.by_phone :
        title = "Rendez-vous physique avec "+ rdv.responsable.user.last_name+ " "+rdv.responsable.user.first_name+" au service "+rdv.service.nom
        strs = "Vous avez une demande rendez-vous  physique au service "+rdv.service.nom +" avec "+ rdv.client.nom+ " "+rdv.client.prenom+" \\n le mail de réponse est: ne-pas-repondre@saint-medard-en-jalles.fr"
    try:
        with open('rdv.ics','w') as f:
            fichier = File(f)
            fichier.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//hacksw/handcal//NONSGML v1.0//EN\nBEGIN:VEVENT\nUID:rdv"+str(rdv.id)+"@import.com\n")
            fichier.write("DTSTAMP:"+oday1+"\nORGANIZER;CN="+rdv.client.nom+" "+rdv.client.prenom+":MAILTO:mail.saint-medard-en-jalles.fr")
            fichier.write("\nDTSTART:"+oday1)
            fichier.write("\nDTEND:"+oday2)
            fichier.write("\nSUMMARY:"+title)
            fichier.write("\nDESCRIPTION:"+strs)
            fichier.write("\nEND:VEVENT")
            fichier.write("\nEND:VCALENDAR")
    except:
        return 10

    if rdv.responsable.login_zimbra != "" and rdv.responsable.mot_de_passe_zimbra != "":
        login = rdv.responsable.login_zimbra
        pwd = rdv.responsable.mot_de_passe_zimbra
        myfiles = {'file': open('rdv.ics', 'r')}
        reponse = requests.post("https://mail.saint-medard-en-jalles.fr/home/urba-info/calendar?fmt=ics",auth=(login,pwd),files=myfiles)

    else:

        name_ = 'rdv_'+rdv.service.nom+"_"+str(rdv.date_r.day) +"_"+ str(rdv.date_r.month) +"_"+ str(rdv.date_r.year) +'.ics'
        name_ = name_.replace(" ","")
        name_ = name_.replace("/","_")
        name_ = name_.replace("-","_")
      
        with open(name_ , 'w') as f:
            fichier = File(f)
            fichier.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//hacksw/handcal//NONSGML v1.0//EN\nBEGIN:VEVENT\nUID:rdv"+str(rdv.id)+"@import.com\n")
            fichier.write("DTSTAMP:"+oday1+"\nORGANIZER;CN="+rdv.client.nom+" "+rdv.client.prenom+":MAILTO:mail.saint-medard-en-jalles.fr")
            fichier.write("\nDTSTART:"+oday1)
            fichier.write("\nDTEND:"+oday2)
            fichier.write("\nSUMMARY:"+title)
            fichier.write("\nDESCRIPTION:"+strs)
            fichier.write("\nEND:VEVENT")
            fichier.write("\nEND:VCALENDAR") 
            fichier.close()  

        """email = EmailMessage(
            'Notification de RDV',
            'Fichier ICS de demande de Rendez-vous dans votre service '+rdv.service.nom,
            'ne-pas-repondre@saint-medard-en-jalles.fr',
            [rdv.responsable.user.email],
            [],
            reply_to=[],
            headers={'Message-ID': rdv.id},
        )
        email.attach_file(name_)
        email.send()"""

        


    myfiles = {'file': open('rdv.ics', 'r')}
    try:
        reponse = requests.post("https://mail.saint-medard-en-jalles.fr/home/urba-info/calendar?fmt=ics",auth=("urba-info","urba33160"),files=myfiles)
        return rdv.by_phone
    except:
        return 0

def updateZimbraCalDel(rdv):
    oday1= date(rdv.date_r.year,rdv.date_r.month,rdv.date_r.day).isoformat()
    base = oday1.replace("-","")
    oday1 = base+"T"+str(rdv.heure_r.hour).zfill(2)+str(rdv.heure_r.minute).zfill(2)+str(58)
    oday2 = base+"T"+str(rdv.heure_f.hour).zfill(2)+str(rdv.heure_f.minute).zfill(2)+str(58)
    strs = ""
    title=""
    if rdv.by_phone == "True" or rdv.by_phone:
        title = "Rendez-vous téléphonique avec "+ rdv.responsable.user.last_name+ " "+rdv.responsable.user.first_name+" au service "+rdv.service.nom
        strs = "Vous avez une demande rendez-vous  téléphonique au service "+rdv.service.nom +" avec "+ rdv.client.nom+ " "+rdv.client.prenom+" \\n le mail de réponse est: ne-pas-repondre@saint-medard-en-jalles.fr"
    if rdv.by_phone == "False" or not rdv.by_phone :
        title = "Rendez-vous physique avec "+ rdv.responsable.user.last_name+ " "+rdv.responsable.user.first_name+" au service "+rdv.service.nom
        strs = "Vous avez une demande rendez-vous  physique au service "+rdv.service.nom +" avec "+ rdv.client.nom+ " "+rdv.client.prenom+" \\n le mail de réponse est: ne-pas-repondre@saint-medard-en-jalles.fr"
    try:
        with open('rdv.ics','w') as f:
            fichier = File(f)
            fichier.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//hacksw/handcal//NONSGML v1.0//EN\nBEGIN:VEVENT\nUID:rdv"+str(rdv.id)+"@import.com\n")
            fichier.write("DTSTAMP:"+oday1+"\nORGANIZER;CN="+rdv.client.nom+" "+rdv.client.prenom+":MAILTO:mail.saint-medard-en-jalles.fr")
            fichier.write("\nSTATUS:CANCELLED")
            fichier.write("\nDTSTART:"+oday1)
            fichier.write("\nDTEND:"+oday2)
            fichier.write("\nSUMMARY:"+title)
            fichier.write("\nDESCRIPTION:"+strs)
            fichier.write("\nEND:VEVENT")
            fichier.write("\nEND:VCALENDAR")
    except:
        return 10


    if rdv.responsable.login_zimbra != "" and rdv.responsable.mot_de_passe_zimbra != "":
        login = rdv.responsable.login_zimbra
        pwd = rdv.responsable.mot_de_passe_zimbra
        myfiles = {'file': open('rdv.ics', 'r')}
        reponse = requests.post("https://mail.saint-medard-en-jalles.fr/home/urba-info/calendar?fmt=ics",auth=(login,pwd),files=myfiles)

    else:

        name_ = 'rdv_'+rdv.service.nom+"_"+str(rdv.date_r.day) +"_"+ str(rdv.date_r.month) +"_"+ str(rdv.date_r.year) +'.ics'
        name_ = name_.replace(" ","")
        name_ = name_.replace("/","_")
        name_ = name_.replace("-","_")
      
        with open(name_ , 'w') as f:
            fichier = File(f)
            fichier.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//hacksw/handcal//NONSGML v1.0//EN\nBEGIN:VEVENT\nUID:rdv"+str(rdv.id)+"@import.com\n")
            fichier.write("DTSTAMP:"+oday1+"\nORGANIZER;CN="+rdv.client.nom+" "+rdv.client.prenom+":MAILTO:mail.saint-medard-en-jalles.fr")
            fichier.write("\nSTATUS:CANCELLED")
            fichier.write("\nDTSTART:"+oday1)
            fichier.write("\nDTEND:"+oday2)
            fichier.write("\nSUMMARY:"+title)
            fichier.write("\nDESCRIPTION:"+strs)
            fichier.write("\nEND:VEVENT")
            fichier.write("\nEND:VCALENDAR")
            fichier.close()  

        """email = EmailMessage(
            'Notification de RDV',
            'Fichier ICS de demande de Rendez-vous dans votre service '+rdv.service.nom,
            'ne-pas-repondre@saint-medard-en-jalles.fr',
            [rdv.responsable.user.email],
            [],
            reply_to=[],
            headers={'Message-ID': rdv.id},
        )
        email.attach_file(name_)
        email.send()"""


    myfiles = {'file': open('rdv.ics', 'r')}
    try:
        reponse = requests.post("https://mail.saint-medard-en-jalles.fr/home/urba-info/calendar?fmt=ics",auth=("urba-info","urba33160"),files=myfiles)
        return reponse.status_code
    except:
        return 0

def dashboardBackup(request):
    return render(request,'administration/backup/backup.html')

def saveDb(request):
    rsp = shutil.copy('db.sqlite3','backups/sauvegarde.sqlite3',follow_symlinks=False)
    messages.success(request,"La base de données a été sauvegardée vers "+rsp)
    return render(request,'administration/backup/backup.html')

def restorDb(request):
    rsp = shutil.copy('backups/sauvegarde.sqlite3','db.sqlite3')
    messages.success(request,"Restauration terminée")
    return render(request,'administration/backup/backup.html')


def getJsHoursForAgenda(request):
    js = request.GET.get('id',None)
    final_ =[]
    if request.is_ajax and request.method == 'GET':
        js = JourSpecifique.objects.filter(pk=int(js))
        if js.exists():
            for j in js:
                final_.append({
                    "debutH": j.heure_debut.hour,
                    "debutM": j.heure_debut.minute,
                    "finH": j.heure_fin.hour,
                    "finM": j.heure_fin.minute,
                })
            return JsonResponse({"heures" : final_}, status=200)
        return JsonResponse({"heures" : 0}, status=200)
    return JsonResponse({"heures" : 0}, status=200)