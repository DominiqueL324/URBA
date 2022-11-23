from django.shortcuts import render
from django.shortcuts import render,redirect
#from rdv.models import Responsable,RendezVous,Service,ResponsableService
from .form import AdministreForm, LoginFormAdministre, RdvFormAdmini
from urba_project import settings
from rdv.form import RdvForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages 
from rdv.models import Client, RendezVous,Service,Fichier,Responsable
from django.db import transaction, IntegrityError
from datetime import date,time
from django.core.mail import send_mail
from administration.ajax_methodes import  envoyerMail, configureNotification,updateZimbraCal,updateZimbraCalDel
import urllib.request, json
from disponibilites.models import Notification
from django.core.files import File
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
import datetime, random, string
from disponibilites.models import Notification

# Create your views here.

def getEditProfilForm(request):
    if request.session['email'] != " ":
        administre = Client.objects.filter(pk=int(request.session['administre'])).first()
        form = AdministreForm({
            'nom':administre.nom,
            'prenom':administre.prenom,
            'tel_number':administre.telephone,
            'email':administre.email,
            'adress':administre.adresse,
        })
        context ={
            "administre": Client.objects.filter(pk=int(request.session['administre'])).first(),
            "form":form,
        }
        return render(request,'administre/edit_administre.html',context)
    else:
        messages.error(request,"Connectez vous pour continuer")
        return render(request,'administre/login.html')

def connectAdministre(request):
    form = LoginFormAdministre(request.POST)
    context = {}
    if form.is_valid():
        login = form.cleaned_data['login']
        mdp = form.cleaned_data['mdp']
        administre = Client.objects.filter(email=login,password=mdp)
        if administre.exists():
            administre = administre.first()
            request.session['email'] = login
            request.session['administre'] = administre.id
            return redirect('administre:dashboard')
        else:
            request.session['email'] = " "
            messages.error(request,"Aucun compte pour vos accès")
            return render(request,'administre/login.html',context)
    context['errors'] = form.errors.items()
    context['form'] = form
    return render(request,'administre/login.html',context)

def Dashboard(request):
    if request.session['email'] != " ":
        rdvs = RendezVous.objects.filter(client=int(request.session['administre']))
        context = {
            "rdvs" : rdvs,
            "administre" : Client.objects.filter(pk=int(request.session['administre'])).first()
        }
        return render(request,"administre/dashboard.html",context)
    else:
        messages.error(request,"Connectez vous pour continuer")
        return render(request,'administre/login.html') 

def editProfile(request,id):
    test = False
    if request.session['email'] != " ":
        form = AdministreForm(request.POST)
        context ={}
        if form.is_valid():
            administre = Client.objects.filter(pk=int(request.session['administre']))
            if form.cleaned_data['mdp'] !="" and  form.cleaned_data['mdp1'] !="":
                if form.cleaned_data['mdp'] == form.cleaned_data['mdp1']:
                    test=True
                else:
                    messages.error(request,"Les mots de passe ne sont pas identiques")
                    context = {
                            'form':form
                        }
                    return render(request,"administre/edit_administre.html",context)
            
            if administre.exists():
                administre = administre.first()
                administre.nom = form.cleaned_data['nom']
                administre.prenom = form.cleaned_data['prenom']
                administre.telephone = form.cleaned_data['tel_number']
                administre.email = form.cleaned_data['email']
                administre.adresse = form.cleaned_data['adress']
                if test:
                    administre.password = form.cleaned_data['mdp']
                administre.save()
                request.session['email']= administre.email
                messages.success(request,"Vous informations ont été mise à jours avec succès")
                return redirect("administre:dashboard")
            else:
                messages.error(request,"Erreur lors de la recupération de vos donnez veuillez reéssayer plus tard")
                context = {
                        'form':form
                    }
                return render(request,"administre/edit_administre.html",context)

        context['errors'] = form.errors.items()
        context['form'] = form
        return render(request,'administre/edit_administre.html',context)
    messages.error(request,'Connectez vous pour continuer ')
    return render(request,'administre/login.html',context)


def editRdv(request,id):
    if request.session['email'] != " ":
        context={}
        rdv = RendezVous.objects.filter(pk=id)
        rdv = rdv.first()
        form = RdvFormAdmini(request.POST,request.FILES)
        rdvs =""
        rdvs = RendezVous.objects.filter(client=rdv.client.id)
        if form.is_valid():
            rdv = RendezVous.objects.filter(pk=id)
            if not rdv.exists():
                messages.error(request,'Erreur de recupération du RDV')
                return redirect('administre:dashboard')
            rdv = rdv.first()
            #---opérations formulaire---#
            try:
                with transaction.atomic():
                    #recupération du service
                    service = form.cleaned_data['service']
                    #création du RDV
                    rdv.date_r = form.cleaned_data['date']
                    rdv.heure_r = form.cleaned_data['heure']
                    rdv.heure_f = form.cleaned_data['heureF']
                    rdv.nombre_personne =  form.cleaned_data['nombre_person']
                    rdv.by_phone = form.cleaned_data['phone']
                    rdv.urbanisme = form.cleaned_data['urbanisme']
                    rdv.adresseTarvaux = form.cleaned_data['adresseTravaux']
                    rdvs = RendezVous.objects.filter(client=rdv.client.id)

                    if rdv.heure_r < time(8,0,0) or rdv.heure_r >= time(17,0,0) or rdv.heure_f >= time(17,0,0) :
                        context['form'] = form
                        context['adresses'] = rdvs
                        context['rdv'] = rdv
                        messages.error(request, "Pas de Rendez-vous avant 8h et apres 17h")
                        return render(request, 'administre/edit_rdv.html', context)

                    if (rdv.heure_r >= time(12,0,0) and rdv.heure_r <= time(12,59,0)) or (rdv.heure_f >= time(12,0,0) and rdv.heure_f <= time(12,59,0)):
                        context['form'] = form
                        context['rdv'] = rdv
                        messages.error(request, "Pas de Rendez-vous durant la pause")
                        return render(request, 'administre/edit_rdv.html', context)

                    rdv_c = RendezVous.objects.filter(heure_r=rdv.heure_r, heure_f=rdv.heure_f, date_r=rdv.date_r,responsable=rdv.responsable)
                    #verification du chevauchement
                    if rdv_c.exists() and rdv_c.first().id != rdv.id:
                        context['form'] = form
                        context['adresses'] = rdvs
                        context['rdv'] = rdv
                        messages.error(request, "Votre agent a déjà un Rendez-vous sur ce créneau à cette date selectionnez un autre créneau"+str(rdv.id)+"  "+str(rdv_c.first().id))
                        return render(request, 'administre/edit_rdv.html', context)
 
                    rdv_c = RendezVous.objects.filter(Q(heure_r__gte=rdv.heure_r,heure_r__lte=rdv.heure_f)  | Q(heure_f__gte=rdv.heure_f,heure_f__lte=rdv.heure_f), date_r=rdv.date_r,by_phone=rdv.by_phone)
                    #verification du chevauchement
                    if rdv_c.exists() and rdv_c.first().id != rdv.id:
                        context['form'] = form
                        context['adresses'] = rdvs
                        context['rdv'] = rdv
                        messages.error(request, "Un Rendez-vous du même type existe déjà à cette heure veuillez choisir un autre créneau horaire")
                        return render(request, 'administre/edit_rdv.html', context)

                    rdv.save()
                    #envoi du mail
                    send_mail(
                    'Modification Rendez-Vous', #subject
                    'Bonjour '+ rdv.client.prenom+' votre rendez vous du '+str(rdv.date_r.day) +'/'+str(rdv.date_r.month)+'/'+str(rdv.date_r.year)+' au service '+rdv.service.nom+' a été bien modifié vous recevrez une confirmation de validation par mail',
                    'brunoowona12@gmail.com', #from_mail
                    [rdv.client.email], #recipient list []
                    fail_silently=False, #fail_silently
                    )
                    #recupération des fichiers    
                    files_data = request.FILES.getlist('fichier')
                    for fd in files_data:
                        fs = FileSystemStorage()
                        file_path = fs.save(fd.name,fd)
                        fichier = Fichier( fichier=file_path)
                        fichier.save()
                        rdv.fichiers.add(fichier)
                    rdvs = RendezVous.objects.filter(client=int(request.session['administre'])).order_by("-id")
                    context = {
                        "rdvs" : rdvs,
                        "administre" : Client.objects.filter(pk=int(request.session['administre'])).first()
                    }

                    #mise à jour du calendrier Zimbra
                    code = updateZimbraCal(rdv)
                    if code == 0:
                        messages.warning(request,'Le RDV a été Modifié avec succès mais une érreur du serveur Zimbra est survenue les responsables de ce service seront notifiés par mail')
                        return redirect('administre:dashboard')
                    
                    if code == 10:
                        messages.error(request,"Problème avec le fichier RDV veuillez reéssayez ") 
                        return redirect('administre:dashboard')

                    if code != 200:
                        messages.success(request,"Le RDV a été modifié avec succès les responsables de ce service seront notifiés par mail  ")
                        return redirect('administre:dashboard')

                rdvs = RendezVous.objects.filter(client=int(request.session['administre'])).order_by("-id")
                context = {
                    "rdvs" : rdvs,
                    "administre" : Client.objects.filter(pk=int(request.session['administre'])).first()
                }
                return render(request,"administre/dashboard.html",context)
            except IntegrityError:
                form.errors['internal'] = "Une érreur est apparue merci de reéssayer!!!"# do soemthing
        context['errors'] = form.errors.items()
        context['form'] = form
        context['rdv'] = rdv
        context['adresses']=rdvs
        return render(request,'administre/edit_rdv.html',context)
    messages.error(request,("Connectez vous pour continuer"))
    return render(request,'administre/login.html')


def getRdvToEdit(request,id):
    if request.session['email'] != " ":
        context = {}
        rdv = RendezVous.objects.filter(pk=id)
        fl = rdv.first().fichiers.all()
        adresse = []
        if rdv.exists():
            rdv = rdv.first()
            rdvs = RendezVous.objects.filter(client=rdv.client.id)
            form = RdvFormAdmini({
                    'nombre_person':rdv.nombre_personne,
                    'date': rdv.date_r,
                    'heure': rdv.heure_r,
                    'heureF':rdv.heure_f,
                    'service' : rdv.service,
                    'phone' : rdv.by_phone,
                    'urbanisme' : rdv.urbanisme,
                    'fichier' : rdv.fichiers,
                    'adresseTravaux': rdv.adresseTarvaux
                })

            context['form']=form
            context['adresses']=rdvs
            context['rdv']=rdv
            context['fl']=fl
            return render(request,'administre/edit_rdv.html',context)

        messages.error(request,"desole aucun RDV trouvé pour cet identifiant")
        return render(request,'disponibilites/validate.html',context)
    messages.error(request,"connectez vous pour continuer")
    return render(request,'administre/login.html')



def logout(request):
    request.session['email'] = " "
    request.session['administre'] = " "
    return redirect('index')

def loginPage(request):
    return render(request,'administre/login.html')


def getRdvToShow(request,id):
    if request.session['email'] != " ":
        context = {}
        rdv = RendezVous.objects.filter(pk=id)
        if rdv.exists():
            rdv = rdv.first()
            fl = rdv.fichiers.all()
            context['rdv'] = rdv
            context['fl'] = fl
            return render(request,'administre/details_rdv.html',context)
        messages.error(request,"desole aucun RDV trouvé pour cet identifiant")
        return render(request,'disponibilites/validate.html',context)

    messages.error(request,"connectez vous pour continuer")
    return render(request,'administre/login.html')

def deleteFile(request):
    #try:
    id = request.GET.get('id',None)
    idr = request.GET.get('rdv',None)
    fl = Fichier.objects.filter(pk=id)
    rdv = RendezVous.objects.filter(pk=idr).first()
    if fl.exists():
        fl = fl.first()
        rdv.fichiers.remove(fl)
        fl.delete()
        messages.success(request, "Fichier supprimer avec succes")
        return JsonResponse({"id": rdv.id}, status=200) 
    #except:
    messages.error(request,"Echec de supréssion")
    return redirect('administre:dashboard')


def recoverStep1(request):
    return render(request,'administre/account/password1.html')

def recoverCheckAccess(request):
    context = {}
    email = request.POST.get('email',None)
    tel = request.POST.get('tel',None)
    client = Client.objects.filter(email=email,telephone=tel)
    if client.exists():
        client = client.first()
        context['administre']=client
        return render(request,'administre/account/password2.html',context)
    messages.error(request,"Aucun compte administré pour le mail: "+email+" et le téléphone: "+str(tel))
    return render(request,'administre/account/password1.html')

def recoverFinalStep(request):
    context = {}
    email = request.POST.get('email',None)
    tel = request.POST.get('tel',None)
    client = Client.objects.filter(email=email,telephone=tel)
    mdp = "".join([random.choice(string.ascii_letters) for _ in range(10)])
    if client.exists():
        client = client.first()
        client.password=mdp
        client.save()
        nt = Notification()
        nt = configureNotification("modification_administre",client)
        envoyerMail(nt,[client.email], 'brunoowona12@gmail.com')
        messages.success(request,'Mot de passe modifié avec succès consulter votre boite email pour le récupérer')
        return render(request, 'administre/login.html')
    messages.error(request,"Erreur durant la récupération du compte veuillez reéssayer plus tard")
    return render(request, 'administre/login.html',context)






