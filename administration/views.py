from django.http import response
from .code import *
from .administrateur import *
from .ajax_methodes import *



#Create your views here.
def LoginPage(request):
    return render(request, "administration/account/login.html")

def logoutUser(request):
    logout(request)
    return redirect('index')

@csrf_protect
def authentication(request):
    form = LoginForm(request.POST)
    context = {}
    if form.is_valid():
        log = form.cleaned_data['login']
        mdp = form.cleaned_data['mdp']
        utilisateur = authenticate(username=log, password=mdp)
        if utilisateur is not None:
            if utilisateur.is_active:
                login(request, utilisateur)
            else:
                return HttpResponse("You're account is disabled.")
        else:
            context['form'] = form
            context['erreur'] = "Aucun profils ne correspond à ces accès"
            return render(request, "administration/account/login.html",
                          context)
        return redirect("administration:dashboard")

    context['errors'] = form.errors.items()
    context['form'] = form
    return render(request, 'administration/account/login.html', context)

#Tableau de bord global
@login_required
def dashboard(request):
    rdvs = RendezVous()
    context = {}
    count = 0
    serv = 0
    if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
        rdvs = RendezVous.objects.all().order_by("-id")
        context['rdvs'] = rdvs
        context['nombre_administre'] = len(Client.objects.all())
        context['nombre_service'] = len(Service.objects.all())
        context['nombre_responsable'] = len(Responsable.objects.all())
        return render(request, 'administration/dashboard.html', context)
    else:
        #récupération des services concernés
        Rservices = ResponsableService.objects.filter(responsable=request.user.responsable.id)
        rdvF = RendezVous.objects.filter(responsable = request.user.responsable)
        context['rdvs'] = rdvF
        context['nombre_administre'] = len(rdvF)
        context['nombre_service'] = len(Rservices) 
        context['nombre_conge'] = len(Evenement.objects.filter(responsable=request.user.responsable.id)) 
        return render(request, 'administration/dashboard.html', context)
    messages.error(request, 'Une érreur est survenue veuillez reéssayer')
    return render(request, 'administration/dashboard.html', context)

    form = ServiceForm(request.POST)
    context = {}
    if form.is_valid() or not form.is_valid():
        try:
            service = Service.objects.filter(pk=id)
            if service.exists():
                service = service.first()
                service.nom = form.cleaned_data['nomService']
                service.duree_rdv = form.cleaned_data['dureeRdv']
                service.responsable = form.cleaned_data['ResponsableService']
                service.save()
                messages.success(request, "service Modifié  avec success")
                form = ServiceForm()
                return redirect('administration:service_dashboard')
            else:
                messages.warning(request, "service inexistant")
                form = ServiceForm()
                return redirect('administration:service_dashboard')
        except:
            messages.warning(request,
                             "Erreur interne au système veuillez reéssayer")
            return redirect('administration:service_dashboard')

    context['errors'] = form.errors.items()
    context['form'] = form
    return render(request, 'administration/service_edit.html', context)

#>>>>>>>>>Gestion des administrés

#dasboard administre
@login_required
def dashboardAdministre(request):
    context = {}
    clients = Client.objects.none()
    rdv_client = []
    _rdv = 0
    try:
        if request.user.groups.filter(
                name="Administrateur").exists() or request.user.groups.filter(
                    name="Adjoint").exists() or request.user.groups.filter(
                        name="Superviseur").exists():
            clients = Client.objects.all().order_by('-id')
            context['administres'] = clients
        else:
            clients = Client.objects.all().order_by('-id')
            context['administres'] = clients
            respoServ_all = ResponsableService.objects.filter(responsable=request.user.responsable.id)
            """client_all = Client.objects.all()
            respoServ_all = ResponsableService.objects.filter(
                responsable=request.user.responsable.id)
            for respo in respoServ_all:
                rdv_temp = RendezVous.objects.filter(service=respo.service.id)
                if rdv_temp.exists:
                    for rd in rdv_temp:
                        _rdv = _rdv + 1
                        rdv_client.append(rd.client.id)
            for client in client_all:
                if (client.id in rdv_client) and (client not in clients):
                    clients |= Client.objects.filter(pk=client.id)"""

            context['administres'] = clients
            context['service'] = len(respoServ_all)
            context['rdv'] = _rdv
    except:
        messages.error(request, "Erreur interne au système")
    return render(request, 'administration/administre.html', context)

#partir ajouter administré
@login_required
def goToAddAministre(request):
    form = AdministreForm()
    context = {
        'form': form,
    }
    return render(request, 'administration/administre_add.html', context)

#ajout administre
@login_required
def addAdministre(request):
    form = AdministreForm(request.POST)
    context = {}
    if form.is_valid() or not form.is_valid():
        if form.cleaned_data['mdp'] == form.cleaned_data['mdp1']:
            try:
                administre = Client()
                administre.nom = form.cleaned_data['nom']
                administre.prenom = form.cleaned_data['prenom']
                administre.email = form.cleaned_data['email']
                administre.adresse = form.cleaned_data['adress']
                administre.telephone = form.cleaned_data['tel_number']
                administre.password = form.cleaned_data['mdp']
                ad = Client.objects.filter(email=form.cleaned_data['email'])
                if ad.exists():
                    context['form']=form
                    messages.error(request, 'Un administré avec le mail '+ form.cleaned_data['email']+ ' Existe déjà')
                    return render(request, 'administration/administre_add.html', context)

                administre.save()
                nt = Notification()
                nt = configureNotification("ajout_administre",administre)
                envoyerMail(nt,[administre.email], 'brunoowona12@gmail.com')
                messages.success(request, 'Administré ajouté avec succes')
                return redirect('administration:administre_dashboard')
            except:
                context['form'] = form
                messages.error(request, 'Une érreur interne est survenue veuillez reéssayer')
                return render(request, 'administration/administre_add.html',context)
        context['form'] = form
        messages.error(request, 'Les mots de passes de sont pas identiques')
        return render(request, 'administration/administre_add.html', context)
    context['form'] = form
    context['errrors'] = form.errors.items()
    return render(request, 'administration/administre_add.html')

#recupérer administre pour edituon
def getAdministreToEdit(request, id):
    try:
        administre = Client.objects.filter(pk=id).first()
        form = AdministreForm({
            'nom': administre.nom,
            'prenom': administre.prenom,
            'tel_number': administre.telephone,
            'email': administre.email,
            'adress': administre.adresse,
        })
        context = {
            "administre": administre,
            "form": form,
        }
        return render(request, 'administration/administre_edit.html', context)
    except:
        messages.error(request,
                       " Erreur lors de la recupération de l'administré11")
        return redirect('administration:dashboard')
    messages.error(request, " Erreur lors de la recupération de l'administré")
    return redirect('administration:dashboard')

#edit administre
@login_required
def editAdministre(request, id):
    form = AdministreForm(request.POST)
    context = {}
    test = False
    if form.is_valid() or not form.is_valid():
        administre = Client()
        try:
            administre = Client.objects.filter(pk=id)
        except:
            messages.error(request, "L'administré sollicté est inexistant")
            return redirect("administration:administre_dashboard")

        if form.cleaned_data['mdp'] != "" and form.cleaned_data['mdp1'] != "":
            if form.cleaned_data['mdp'] == form.cleaned_data['mdp1']:
                test = True
            else:
                messages.error(request,
                               "Les mots de passe ne sont pas identiques")
                context = {'form': form}
                return render(request, "administration/administre_edit.html",
                              context)
            if administre.exists():
                administre = administre.first()
                administre.nom = form.cleaned_data['nom']
                administre.prenom = form.cleaned_data['prenom']
                administre.telephone = form.cleaned_data['tel_number']
                administre.email = form.cleaned_data['email']
                administre.adresse = form.cleaned_data['adress']
                ad = Client.objects.filter(email=form.cleaned_data['email'])
                #check if exsit
                if ad.exists() and ad.first().id != administre.id:
                    context['form']=form
                    context['administre']=administre 
                    messages.error(request, 'Un administré avec le mail '+ form.cleaned_data['email']+ ' Existe déjà')
                    return render(request, 'administration/administre_edit.html', context)

                if test:
                    administre.password = form.cleaned_data['mdp']
                administre.save()
                nt = Notification()
                nt = configureNotification("modification_administre",administre)
                envoyerMail(nt,[administre.email], ' ')
                messages.success(request, "Information de l'administré " + administre.nom +" " + administre.prenom + " ont été modifées avec succes")
                return redirect("administration:administre_dashboard")
            else:
                messages.error(request,"Erreur lors de la recupération de vos donnez veuillez reéssayer plus tard"
                )
                context = {'form': form}
                return render(request, "administre/edit_administre.html",context)

    context = {
        'administre': Client.objects.filter(pk=id).first(),
        'form': form,
        'errors': form.errors.items(),
    }
    messages.error(request, 'Tous les champs sont obligatoires')
    return render(request, 'administration/administre_edit.html', context)

#suppression d'un administré
@login_required
def deleteAdministre(request, id):
    try:
        administre = Client.objects.filter(pk=id)
        if administre.exists():
            administre = administre.first()
            administre.delete()
            messages.success(request, "Administré  supprimer avec success")
            return redirect('administration:administre_dashboard')
    except:
        messages.error(request, "Administré inexistant")
        return redirect('administration:administre_dashboard')
    messages.error(request,
                   "Erreur de suppréssion de service veuillez réessayer")
    return redirect('administration:administre_dashboard')

#>>>>>>>>>>>>>>gestion des RDV
#dashboard RDV
@login_required
def dashboardRDV(request):
    rdvs = RendezVous()
    context = {}
    count = 0
    serv = 0
    if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists() :
        rdvs = RendezVous.objects.all().order_by("-id")
        context['rdvs'] = rdvs
        context['nombre_administre'] = len(Client.objects.all())
        context['nombre_service'] = len(Service.objects.all())
        context['nombre_responsable'] = len(Responsable.objects.all())
        return render(request, 'administration/rdv.html', context) 
    else:
        Rservices = ResponsableService.objects.filter(responsable=request.user.responsable.id)
        rdvF = RendezVous.objects.filter(responsable = request.user.responsable)
        context['rdvs'] = rdvF
        context['nombre_administre'] = count
        context['nombre_service'] = len(Rservices)
        return render(request, 'administration/rdv.html', context)
    messages.error(request, 'Une érreur est survenue veuillez reéssayer')
    return render(request, 'administration/rdv.html', context)

#ajout d'un RDV
@login_required
def addRdv(request):
    context = {}
    form = RdvFormAdmin(request.POST, request.FILES)
    if form.is_valid() or not form.is_valid():
        rdv = RendezVous()
        try:
            with transaction.atomic():
                rdv.date_r = form.cleaned_data['date']
                rdv.heure_r = form.cleaned_data['heure']
                rdv.nombre_personne = form.cleaned_data['nombre_person']
                rdv.service = Service.objects.filter(id=int(request.POST.get('service'))).first()
                rdv.client = form.cleaned_data['administre']
                rdv.by_phone = form.cleaned_data['phone']
                rdv.adresseTarvaux = form.cleaned_data['adresseTravaux']
                dt = datetime.combine(date.today(), rdv.heure_r) + timedelta( minutes= rdv.service.duree_rdv )
                rdv.heure_f = dt.time()
                rdv.urbanisme = True
                if rdv.heure_r < time(8,0,0) or rdv.heure_r >= time(17,0,0) or rdv.heure_f >= time(17,0,0) :
                    serv = Service.objects.none()
                    if request.user.groups.filter(name="Agent").exists():
                        rsp = ResponsableService.objects.filter(responsable=request.user.responsable.id)
                        for r in rsp:
                            serv |= Service.objects.filter(id=r.service.id)
                        form.fields['service'].queryset = serv
                    else:
                        form.fields['service'].queryset = Service.objects.all()
                    context['form'] = form
                    context['rdv'] = rdv
                    messages.error(request, "Pas de Rendez-vous avant 8h et apres 17h")
                    return render(request, 'administration/rdv_add.html', context)

                if (rdv.heure_r >= time(12,0,0) and rdv.heure_r <= time(14,0,0)) or (rdv.heure_f >= time(12,0,0) and rdv.heure_f <= time(14,0,0)):
                    serv = Service.objects.none()
                    if request.user.groups.filter(name="Agent").exists():
                        rsp = ResponsableService.objects.filter(responsable=request.user.responsable.id)
                        for r in rsp:
                            serv |= Service.objects.filter(id=r.service.id)
                        form.fields['service'].queryset = serv
                    else:
                        form.fields['service'].queryset = Service.objects.all()
                    context['form'] = form
                    context['rdv'] = rdv
                    messages.error(request, "Pas de Rendez-vous durant la pause")
                    return render(request, 'administration/rdv_add.html', context)
                d = datetime(rdv.date_r.year,rdv.date_r.month,rdv.date_r.day,)
                if d.weekday() == 6 or d.weekday() == 5:
                    serv = Service.objects.none()
                    if request.user.groups.filter(name="Agent").exists():
                        rsp = ResponsableService.objects.filter(responsable=request.user.responsable.id)
                        for r in rsp:
                            serv |= Service.objects.filter(id=r.service.id)
                        form.fields['service'].queryset = serv
                    else:
                        form.fields['service'].queryset = Service.objects.all()
                    context['form'] = form
                    context['rdv'] = rdv
                    messages.error(request, "Pas de Rendez-vous durant le weekend")
                    return render(request, 'administration/rdv_add.html', context)
                
                if rdv.nombre_personne > 2 or  rdv.nombre_personne <1:
                    serv = Service.objects.none()
                    if request.user.groups.filter(name="Agent").exists():
                        rsp = ResponsableService.objects.filter(responsable=request.user.responsable.id)
                        for r in rsp:
                            serv |= Service.objects.filter(id=r.service.id)
                        form.fields['service'].queryset = serv
                    else:
                        form.fields['service'].queryset = Service.objects.all()
                    context['form'] = form
                    context['rdv'] = rdv
                    messages.error(request, "Pas plus de 2 personnes et moins d'une personne par RDV ")
                    return render(request, 'administration/rdv_add.html', context)


                rdv_c = RendezVous.objects.filter(Q(heure_r__gte=rdv.heure_r,heure_r__lte=rdv.heure_f)  | Q(heure_f__gte=rdv.heure_f,heure_f__lte=rdv.heure_f), date_r=rdv.date_r,by_phone=rdv.by_phone)
                #verification du chevauchement
                if rdv_c.exists():
                    serv = Service.objects.none()
                    if request.user.groups.filter(name="Agent").exists():
                        rsp = ResponsableService.objects.filter(responsable=request.user.responsable.id)
                        for r in rsp:
                            serv |= Service.objects.filter(id=r.service.id)
                        form.fields['service'].queryset = serv
                    else:
                        form.fields['service'].queryset = Service.objects.all()
                    context['form'] = form
                    context['rdv'] = rdv
                    messages.error(request, "Un Rendez-vous du même type existe déjà à cette heure veuillez choisir un autre créneau horaire")
                    return render(request, 'administration/rdv_add.html', context)
                respo = Responsable()
                if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
                    if request.POST.get('respo') != None:
                        if request.user.groups.filter(name="Administrateur").exists() and int(request.POST.get('respo')) == request.user.id:
                            respo = Responsable.objects.filter(user=int(request.POST.get('respo')))
                            if respo.exists(): 
                                respo = respo.first()
                            else:
                                respo = Responsable()
                                respo.user = request.user
                                respo.adresse = request.user.administrateur.adresse
                                respo.telephone = request.user.administrateur.telephone
                                respo.couleur_js = ""
                                respo.couleur_conge = ""
                                respo.save()
                        else:
                            respo = Responsable.objects.filter(pk=int(request.POST.get('respo'))).first() 
                else:
                    respo = Responsable.objects.filter(pk=request.user.responsable.id).first()
                rdv.responsable = respo 

                rdv.save()
                #envoi du mail
                nt = Notification()
                nt = configureNotification("ajout_rdv",rdv)
                envoyerMail(nt,[rdv.client.email], 'brunoowona12@gmail.com')
                #recupération des fichiers
                files_data = request.FILES.getlist('fichier')
                for fd in files_data:
                    fs = FileSystemStorage()
                    file_path = fs.save(fd.name, fd)
                    fichier = Fichier(fichier=file_path)
                    fichier.save()
                    rdv.fichiers.add(fichier)

                messages.success(
                    request, "Le rendez-vous au service " + rdv.service.nom +
                    " a été enregistré avec succes l\'administré recevra un mail de validation ou non après consultation de l'agent concerné"
                )
                liste_destinataire = []
                services = ResponsableService.objects.filter(
                    service=rdv.service.id)
                for service in services:
                    liste_destinataire.append(service.responsable.user.email)

                #mise à jour du calendrier Zimbra
                code = updateZimbraCal(rdv)
                if code == 0:
                    messages.warning(
                        request,
                        'Le RDV a été enregistré avec succès mais une érreur du serveur Zimbra est survenue les responsables de ce service seront notifiés par mail'
                    )
                    return redirect('administration:rdv_dashboard')

                if code == 10:
                    messages.error(
                        request,
                        "Problème avec le fichier RDV veuillez reéssayez ")
                    return redirect('administration:rdv_dashboard')

                if code != 200:
                    messages.warning(
                        request,
                        "Le RDV a été enregistré avec succès mais une érreur du serveur Zimbra est survenue les responsables de ce service seront notifiés par mail  "
                        + str(code))
                    return redirect('administration:rdv_dashboard')
            return redirect('administration:rdv_dashboard')

        except IntegrityError:
            form.errors['internal'] = "Une érreur est apparue merci de reéssayer!!!"

    serv = Service.objects.none()
    if request.user.groups.filter(name="Agent").exists():
        rsp = ResponsableService.objects.filter(responsable=request.user.responsable.id)
        for r in rsp:
            serv |= Service.objects.filter(id=r.service.id)
        form.fields['service'].queryset = serv
    else:
        form.fields['service'].queryset = Service.objects.all()
    context['errors'] = form.errors.items()
    context['form'] = form
    return render(request, 'administration/rdv_add.html', context)

#go to add
@login_required
def goToAddRdv(request):
    form = RdvFormAdmin()
    serv = Service.objects.none()
    if request.user.groups.filter(name="Agent").exists():
        rsp = ResponsableService.objects.filter(responsable=request.user.responsable.id)
        for r in rsp:
            serv |= Service.objects.filter(id=r.service.id)
        form.fields['service'].queryset = serv
    else:
        form.fields['service'].queryset = Service.objects.all()
    context = {'form': form}
    return render(request, 'administration/rdv_add.html', context)

#get Rdv to edit
@login_required
def getRdvToEdit(request, id):
    rdv = RendezVous()
    context = {}
    rdvs=""
    try:
        rdv = RendezVous.objects.filter(pk=id)
        if rdv.exists():
            rdv = rdv.first()
            rdvs = RendezVous.objects.filter(client=rdv.client.id)
    except:
        messages.error(request, "Ce RDV n'existe pas veuillez rréssayer")
        return redirect('administration:dashboard_rdv')
    #form = RdvFormAdmin()    
    form = RdvFormAdmin({
        'phone': rdv.by_phone,
        'fichier': rdv.fichiers,
        #'service': rdv.service,
        'administre': rdv.client,
        'heure': rdv.heure_r,
        'heureF': rdv.heure_f,
        'date': rdv.date_r,
        'nombre_person': rdv.nombre_personne,
        'adresseTravaux': rdv.adresseTarvaux
    })
    fl = rdv.fichiers.all()
    #form.fields['service'].queryset = Service.objects.all()
    context['form'] = form
    context['rdv'] = rdv
    context['duree'] = rdv.service.duree_rdv
    context['fl']=fl
    context['adresses']=rdvs
    return render(request, 'administration/rdv_edit.html', context)

#edit rdv
@login_required
def editRdv(request, id):
    form = RdvFormAdmin(request.POST, request.FILES)
    context = {}
    rdv = RendezVous()
    etatChange = False
    etat = ""
    try:
        rdv = RendezVous.objects.filter(pk=id)
        if rdv.exists():
            rdv = rdv.first()
    except:
        messages.error(request, "Ce RDV n'existe pas veuillez reéssayer")
        return redirect('administration:rdv_dashboard')
    if form.is_valid() or not form.is_valid() :

        if request.POST.get('state') != rdv.etat:
            etatChange = True
            etat = request.POST.get('state')
        rdv.date_r = form.cleaned_data['date']
        rdv.heure_r = form.cleaned_data['heure']
        rdv.nombre_personne = form.cleaned_data['nombre_person']
        rdv.client = form.cleaned_data['administre']
        rdv.by_phone = form.cleaned_data['phone']
        rdv.adresseTarvaux = form.cleaned_data['adresseTravaux']
        rdv.etat = request.POST.get('state')
        dt = datetime.combine(date.today(), rdv.heure_r) + timedelta( minutes= rdv.service.duree_rdv )
        rdv.heure_f = dt.time()
        rdv.urbanisme = False
        if rdv.heure_r < time(8,0,0) or rdv.heure_r >= time(17,0,0) or rdv.heure_f >= time(17,0,0) :
            context['form'] = form
            context['rdv'] = rdv
            messages.error(request, "Pas de Rendez-vous avant 8h et apres 17h")
            return render(request, 'administration/rdv_edit.html', context)
       
        if (rdv.heure_r >= time(12,0,0) and rdv.heure_r <= time(14,0,0)) or (rdv.heure_f >= time(12,0,0) and rdv.heure_f <= time(14,0,0)):   
            context['form'] = form
            context['rdv'] = rdv
            messages.error(request, "Pas de Rendez-vous durant la pause")
            return render(request, 'administration/rdv_edit.html', context)

        rdv_c = RendezVous.objects.filter(Q(heure_r__gte=rdv.heure_r,heure_r__lte=rdv.heure_f)  | Q(heure_f__gte=rdv.heure_f,heure_f__lte=rdv.heure_f), date_r=rdv.date_r,by_phone=rdv.by_phone)
                    #verification du chevauchement
        if rdv_c.exists() and rdv_c.first().id != rdv.id:
            context['form'] = form
            context['rdv'] = rdv
            messages.error(request, "Un Rendez-vous du même type existe déjà à cette heure veuillez choisir un autre créneau horaire")
            return render(request, 'administration/rdv_edit.html', context)
        d = datetime(rdv.date_r.year,rdv.date_r.month,rdv.date_r.day,)
        if d.weekday() == 6 or  d.weekday() == 5:
            context['form'] = form
            context['rdv'] = rdv
            messages.error(request, "Pas de Rendez-vous durant le weekend"+ str(d.weekday()))
            return render(request, 'administration/rdv_edit.html', context)
        
        if rdv.nombre_personne > 2 or  rdv.nombre_personne <1:
            context['form'] = form
            context['rdv'] = rdv
            messages.error(request, "Pas plus de 2 personnes et moins d'une personne par RDV ")
            return render(request, 'administration/rdv_edit.html', context)
        respo = Responsable()
        if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
            if request.POST.get('respo') != None:
                if request.user.groups.filter(name="Administrateur").exists() and int(request.POST.get('respo')) == request.user.id:
                    respo = Responsable.objects.filter(user=int(request.POST.get('respo')))
                    if respo.exists(): 
                        respo = respo.first()
                    else:
                        respo = Responsable()
                        respo.user = request.user
                        respo.adresse = request.user.administrateur.adresse
                        respo.telephone = request.user.administrateur.telephone
                        respo.couleur_js = "blue"
                        respo.couleur_conge = "green"
                        respo.save()
                else:
                    respo = Responsable.objects.filter(pk=int(request.POST.get('respo'))).first() 
        else:
            respo = Responsable.objects.filter(pk=request.user.responsable.id).first() 
             
        rdv.responsable = respo        
        #envoi du mail
        try:
            nt = Notification()
            if etatChange == True:
                if etat == "Annule":
                    nt = configureNotification("rdv_annule",rdv)
                    updateZimbraCalDel(rdv)
                if etat == "Approuve":
                    nt = configureNotification("rdv_valide",rdv)
                if etat == "En attente":
                    nt = configureNotification("rdv_en_attente",rdv)
                envoyerMail(nt,[rdv.client.email], 'brunoowona12@gmail.com')
            
            nt = configureNotification("ajout_rdv",rdv)
            envoyerMail(nt,[rdv.client.email], 'brunoowona12@gmail.com')
        except:
            pass
        #recupération des fichiers
        files_data = request.FILES.getlist('fichier')
        for fd in files_data:
            fs = FileSystemStorage()
            file_path = fs.save(fd.name, fd)
            fichier = Fichier(fichier=file_path)
            fichier.save()
            rdv.fichiers.add(fichier)
        rdv.save() 
        if rdv.etat == "Annule":
            updateZimbraCalDel(rdv)
        messages.success(
            request, "Votre Rendez-vous au service " + rdv.service.nom +
            " a été modifié avec succes vous recevrez un mail de validation ou non après consultation de l'agent concerné"
        )
        liste_destinataire = []
        services = ResponsableService.objects.filter(service=rdv.service.id)
        for service in services:
            liste_destinataire.append(service.responsable.user.email)

        #mise à jour du calendrier Zimbra
        code = updateZimbraCal(rdv)
        if code == 0:
            messages.warning(
                request,
                'Le RDV a été modifé avec succès mais une érreur du serveur Zimbra est survenue les responsables de ce service seront notifiés par mail'
            )
            return redirect('administration:rdv_dashboard')

        if code == 10:
            messages.error(request,
                           "Problème avec le fichier RDV veuillez reéssayez ")
            return redirect('administration:rdv_dashboard')

        if code != 200:
            messages.warning(
                request,
                "Le RDV a été modifé avec succès mais une érreur du serveur Zimbra est survenue les responsables de ce service seront notifiés par mail  "
                + str(code))
            return redirect('administration:rdv_dashboard')
        return redirect('administration:rdv_dashboard')
    context['errors'] = form.errors.items()
    context['form'] = form
    context['rdv'] = rdv
    return render(request, 'administration/rdv_edit.html', context)

#delete rdv
@login_required
def deleteRdv(request, id):
    try:
        rdv = RendezVous.objects.filter(pk=id)
        if rdv.exists():
            rdv = rdv.first()
            updateZimbraCalDel(rdv)
            rdv.delete()
            messages.success(request, "Rendez-vous  supprimer avec success")
            return redirect('administration:rdv_dashboard')
    except:
        messages.error(
            request,
            "Erreur1 de suppréssion de service veuillez réessayer inexistant")
        return redirect('administration:rdv_dashboard')
    messages.error(request,
                   "Erreur de suppréssion de service veuillez réessayer")
    return redirect('administration:rdv_dashboard')

#>>>>>>>>>>>>>>>>gestion des congés

#dashboard congés
@login_required
def dashboardConges(request):
    agent = Responsable.objects.all()
    ags = Responsable.objects.none()
    conges = ""
    if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
        conges = Evenement.objects.all()
    else:
        conges = Evenement.objects.filter(responsable = request.user.responsable)
    for ag in agent:
        if not ag.user.groups.filter(name="Administrateur").exists():
            ags |= Responsable.objects.filter(pk=ag.id)
    context ={
        'agents':ags,
        'conges':conges,
    }
    return render(request, 'administration/conges.html',context)

#aller à la page ajout congé
@login_required
def goToAddConge(request):
    agent = Responsable.objects.all()
    ags = Responsable.objects.none()
    for ag in agent:
        if not ag.user.groups.filter(name="Administrateur").exists():
            ags |= Responsable.objects.filter(pk=ag.id)

    form = EventForm()
    form.fields['responsable'].queryset= ags
    context = {
        'form': form,
    }
    return render(request, 'administration/conges_add.html', context)

#ajouter un congé
@login_required
def addConges(request):
    if request.method == 'POST':
        context = {}
        form = EventForm(request.POST)
        if form.is_valid() or not form.is_valid():
            responsable = Responsable()
            if request.user.groups.filter(name="Administrateur") or request.user.groups.filter(name="Adjoint") or request.user.groups.filter(name="Superviseur"):
                responsable = Responsable.objects.filter(pk=int(request.POST.get('responsable'))).first()
            else:
                responsable = request.user.responsable
            if form.cleaned_data['date_d'] > form.cleaned_data['date_f']:
                agent = Responsable.objects.all()
                ags = Responsable.objects.none()
                for ag in agent:
                    if not ag.user.groups.filter(name="Administrateur").exists():
                        ags |= Responsable.objects.filter(pk=ag.id)

                form.fields['responsable'].queryset= ags
                messages.error(request,'La date de début est après la date de fin')
                context['form'] = form
                return render(request, "administration/conges_add.html",context)
            try:
                with transaction.atomic():
                    event = Evenement()
                    event.descriptions = form.cleaned_data['description']
                    event.responsable = responsable
                    event.date_d = form.cleaned_data['date_d']
                    event.date_f = form.cleaned_data['date_f']
                    event.color = responsable.couleur_conge
                    event.type_e = "holiday"
                    event.name = form.cleaned_data['name']
                    rdv= RendezVous.objects.filter(date_r__gte=event.date_d,date_r__lte=event.date_f,responsable=event.responsable)
                    if rdv.exists():
                        agent = Responsable.objects.all()
                        ags = Responsable.objects.none()
                        for ag in agent:
                            if not ag.user.groups.filter(name="Administrateur").exists():
                                ags |= Responsable.objects.filter(pk=ag.id)
                        form.fields['responsable'].queryset= ags
                        context['form'] = form
                        messages.error(request, "Il y a déjà un RDV à cette date pour ce responsable")
                        return render(request, "administration/conges_add.html", context)
                    event.save()
                    """send_mail(
                        'Ajout de congé',
                        'Bonjour le responsable ' +
                        event.responsable.user.first_name + " " +
                        event.responsable.user.last_name +
                        " a enregistré un congé partant du " +
                        str(event.date_d.day).zfill(2) + '/' +
                        str(event.date_d.month).zfill(2) + '/' +
                        str(event.date_d.year) + ' au ' +
                        str(event.date_f.day).zfill(2) + '/' +
                        str(event.date_f.month).zfill(2) + '/' +
                        str(event.date_f.year),
                        'brunoowona12@gmail.com',  #from_mail
                        ['brunoowona12@gmail.com'],  #recipient list []
                        fail_silently=False,  #fail_silently
                    )"""
                    messages.success(request, "Jour off ajouté avec succes")
                    form = EventForm()
                    return redirect("administration:conges")
            except IntegrityError:
                agent = Responsable.objects.all()
                ags = Responsable.objects.none()
                for ag in agent:
                    if not ag.user.groups.filter(name="Administrateur").exists():
                        ags |= Responsable.objects.filter(pk=ag.id)

                form.fields['responsable'].queryset= ags
                form.errors['internal'] = "Une érreur est apparue merci de reéssayer!!!"

    agent = Responsable.objects.all()
    ags = Responsable.objects.none()
    for ag in agent:
        if not ag.user.groups.filter(name="Administrateur").exists():
            ags |= Responsable.objects.filter(pk=ag.id)

    form.fields['responsable'].queryset= ags
    context['errors'] = form.errors.items()
    context['form'] = form
    return render(request, "administration/conges_add.html", context)

#recupération du congé pour édition
@login_required
def getCongeToEdit(request, id):
    conge = Evenement()
    context = {}
    try:
        conge = Evenement.objects.filter(pk=id)
        if conge.exists():
            conge = conge.first()
        else:
            messages.error(request, 'Congé inexistant')
            return redirect('administration:conges')
    except:
        messages.error(request, "Jour off inexistant veuillez reéssayer")
        return redirect('administration:conges')
    form = EventForm({
        'name': conge.name,
        'description': conge.descriptions,
        'date_d': conge.date_d,
        'date_f': conge.date_f,
        'color': conge.color,
    })
    context['form'] = form
    context['conge'] = conge
    return render(request, 'administration/conges_edit.html', context)

#modification d'un congé
@login_required
def editConge(request, id):
    if request.method == 'POST':
        context = {}
        form = EventForm(request.POST)
        if form.is_valid() or not form.is_valid():
            
            if form.cleaned_data['date_d'] > form.cleaned_data['date_f']:
                messages.error(request,
                               'La date de début est après la date de fin')
                context['form'] = form
                return render(request, "administration/conges_edit.html",
                              context)
            try:
                with transaction.atomic():
                    event = Evenement.objects.filter(pk=id)
                    if event.exists():
                        event = event.first()
                    else:
                        messages.error(request, 'Congé inexistant')
                        context['form'] = form
                        return redirect("administration:conges")
                    responsable = event.responsable
                    event.descriptions = form.cleaned_data['description']
                    event.date_d = form.cleaned_data['date_d']
                    event.date_f = form.cleaned_data['date_f']
                    event.type_e = "holiday"
                    event.name = form.cleaned_data['name']
                    rdv= RendezVous.objects.filter(date_r__gte=event.date_d,date_r__lte=event.date_f,responsable=event.responsable)
                    if rdv.exists():
                        agent = Responsable.objects.all()
                        ags = Responsable.objects.none()
                        for ag in agent:
                            if not ag.user.groups.filter(name="Administrateur").exists():
                                ags |= Responsable.objects.filter(pk=ag.id)
                        context['conge'] = Evenement.objects.filter(pk=id).first()
                        context['form'] = form
                        messages.error(request, "Il y a déjà un RDV à cette date pour ce responsable")
                        return render(request, "administration/conges_edit.html", context)
                    event.save()
                    send_mail(
                        'Modification de congé',
                        'Bonjour le responsable ' +
                        event.responsable.user.first_name + " " +
                        event.responsable.user.last_name +
                        " a modifé son congé partant du " +
                        str(event.date_d.day).zfill(2) + '/' +
                        str(event.date_d.month).zfill(2) + '/' +
                        str(event.date_d.year) + ' au ' +
                        str(event.date_f.day).zfill(2) + '/' +
                        str(event.date_f.month).zfill(2) + '/' +
                        str(event.date_f.year),
                        'brunoowona12@gmail.com',  #from_mail
                        ['brunoowona12@gmail.com'],  #recipient list []
                        fail_silently=False,  #fail_silently
                    )
                    messages.success(request, "Jour off modifié avec succes")
                    form = EventForm()
                    return redirect("administration:conges")
            except IntegrityError:
                form.errors[
                    'internal'] = "Une érreur est apparue merci de reéssayer!!!"
    context['errors'] = form.errors.items()
    context['form'] = form
    context['conge'] = Evenement.objects.filter(pk=id).first()
    return render(request, "administration/edit_add.html", context)

#suppression de congé
@login_required
def deleteConge(request, id):
    try:
        conge = Evenement.objects.filter(pk=id)
        if conge.exists():
            conge = conge.first()
            conge.delete()
            messages.success(request, "Jour off supprimer avec success")
            return redirect('administration:conges')
    except:
        messages.error(
            request,
            "Erreur1 de suppréssion du Jour off veuillez réessayer inexistant")
        return redirect('administration:conges')
    messages.error(request,
                   "Erreur de suppréssion du Jours off veuillez réessayer")
    return redirect('administration:conges')


#---------------------METHODES AJAX-------------------------#

#methode ajax qui recupère les rdv
@login_required
def getRdvAjax(request, en_attente):
    if request.is_ajax and request.method == "GET":
        rdvF = RendezVous.objects.none()
        result = []
        evtRdv = []
        if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
            if en_attente == 1:
                rdvF = RendezVous.objects.filter(etat="En attente").order_by("-id")
            if en_attente == 2 :
                rdvF = RendezVous.objects.filter(etat="Approuve").order_by("-id")
            if en_attente == 3:
                rdvF = RendezVous.objects.filter(etat="Annule").order_by("-id")
            if en_attente == 4:
                rdvF = RendezVous.objects.all().order_by("-id")
        else:
            Rservices = ResponsableService.objects.filter(
                responsable=request.user.responsable.id)
            if en_attente == 2:
                for Rservice in Rservices:
                    rdvF |= RendezVous.objects.filter(service=Rservice.service.id, etat="Approuve")
            if en_attente == 1:
                for Rservice in Rservices:
                    rdvF |= RendezVous.objects.filter(service=Rservice.service.id, etat="En attente")
            if en_attente == 3:
                for Rservice in Rservices:
                    rdvF |= RendezVous.objects.filter(service=Rservice.service.id, etat="Annule")
            if en_attente == 4:
                for Rservice in Rservices:
                    rdvF |= RendezVous.objects.filter(service=Rservice.service.id)
            

        for final_rdv in rdvF:
            result.append({
                'client':final_rdv.client.nom + " " + final_rdv.client.prenom,
                "service":final_rdv.service.nom,
                "date":str(final_rdv.date_r.day).zfill(2)+"/"+str(final_rdv.date_r.month).zfill(2)+"/"+str(final_rdv.date_r.year),
                "id":final_rdv.id,
                "etat": final_rdv.etat,
            })
            if final_rdv.etat == "En attente":
                color = "#2bff00"
            elif final_rdv.etat == "Approuve":
                color = "#040675"
            elif final_rdv.etat == "Annule":
                color = "red"
            elif final_rdv.etat == "Reporte":
                color = "#5d0274"
            else:
                color = "#e100ff"
            a = "<a href='/administration/rdv/recuperer/{}' class=' is-success button is-small' ><span><i class='fa fa-eye'></i></span></a>".format(final_rdv.id)
            evtRdv.append({
                'id':final_rdv.id,
                'name':"Rendez-Vous",
                'date': [final_rdv.date_r, final_rdv.date_r],
                'type':"Rendez-vous",
                'color':color,
                'everyYear':False,
                'description':"Rendez-vous avec " + str(final_rdv.client.nom) + " " +final_rdv.client.prenom + " au service " +final_rdv.service.nom + " à " + str(final_rdv.heure_r.hour) +"h:" + str(final_rdv.heure_r.minute) + "  " + a
            })
        return JsonResponse({"rdvs": result, "evt": evtRdv}, status=200)
    else:
        return JsonResponse({"rdv": False}, status=200)
    return JsonResponse({}, status=400)

#methode ajax qui recupère des rdv selon les critères du form
@login_required
def getRdvForSearchField(request):
    valeur = request.GET.get("valeur", None)
    attribut = request.GET.get("attribut", None)
    result = []
    if request.is_ajax and request.method == "GET":
        rdvF = RendezVous.objects.none()
        if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
            try:
                if attribut == "service":
                    service = Service.objects.filter(nom__icontains=valeur).first()
                    rdvF = RendezVous.objects.filter(service=service.id)
                if attribut == "date":
                    rdvF = RendezVous.objects.filter(date_r=valeur)
                if attribut == "administre":
                    client = Client.objects.filter(email__icontains=valeur).first()
                    rdvF = RendezVous.objects.filter(client=client.id)
            except:
                return JsonResponse({"rdvs": 0}, status=200)
        if request.user.groups.filter(name="Agent").exists():
            Rservices = ResponsableService.objects.filter(responsable=request.user.responsable.id)

            if attribut == "service":
                service = Service.objects.filter(nom__icontains=valeur)
                if service.exists():
                    for serv in service:
                        for Rservice in Rservices:
                            if Rservice.service.id == serv.id:
                                rdvF |= RendezVous.objects.filter(service=serv.id)

            if attribut == "administre":
                client = Client.objects.filter(email__icontains=valeur)
                if client.exists():
                    client = client.first()
                    for Rservice in Rservices:
                        rdvF |= RendezVous.objects.filter(client=client.id,service=Rservice.service.id)
            if attribut == "date":
                for Rservice in Rservices:
                    rdvF |= RendezVous.objects.filter(date_r=valeur,service=Rservice.service.id)
        if rdvF.exists():
            for final_rdv in rdvF:
                result.append({
                    'client':final_rdv.client.nom + " " + final_rdv.client.prenom,
                    "service":final_rdv.service.nom,
                    "date":str(final_rdv.date_r.day).zfill(2)+"/"+str(final_rdv.date_r.month).zfill(2)+"/"+str(final_rdv.date_r.day),
                    "id":final_rdv.id,
                    "etat":final_rdv.etat,
                })
            return JsonResponse({"rdvs": result}, status=200)
        return JsonResponse({"rdv": False}, status=200)
    return JsonResponse({}, status=400)

#methode ajax de recupération de rendez-vous entre deux dates
@login_required
def getRdvBetweenDate(request):
    debut = request.GET.get("debut", None)
    fin = request.GET.get("fin", None)
    result = []
    tabDate = debut.split("-")
    tabDateF = fin.split("-")
    debut = date(int(tabDate[0]), int(tabDate[1]), int(tabDate[2]))
    fin = date(int(tabDateF[0]), int(tabDateF[1]), int(tabDateF[2]))
    if request.is_ajax and request.method == "GET":
        rdvF = RendezVous.objects.none()
        if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
            rdvF = RendezVous.objects.filter(date_r__gte=debut,date_r__lte=fin) 
        else:
            Rservices = ResponsableService.objects.filter(responsable=request.user.responsable.id)
            for Rservice in Rservices:
                rdvF |= RendezVous.objects.filter(date_r__gte=debut,date_r__lte=fin,service=Rservice.service.id)
        if rdvF.exists():
            for final_rdv in rdvF:
                result.append({
                    'client':final_rdv.client.nom + " " + final_rdv.client.prenom,
                    'email':final_rdv.client.email,
                    "service":final_rdv.service.nom,
                    "date":str(final_rdv.date_r.day).zfill(2)+"/"+str(final_rdv.date_r.month).zfill(2)+"/"+str(final_rdv.date_r.year),
                    "id":final_rdv.id,
                    "etat":final_rdv.etat
                })
            return JsonResponse({"rdvs": result}, status=200)
        return JsonResponse({"rdv": debut, "fin": fin}, status=200)
    return JsonResponse({}, status=400)

#méthode ajax qui recupère des client selon un filtre
@login_required
def getAdministreBynameOrEmail(request):
    valeur = request.GET.get("valeur", None)
    attribut = request.GET.get("attribut", None)
    context = {}
    clients = Client.objects.none()
    rdv_client = []
    final = []
    if request.is_ajax and request.method == "GET":
        try:
            if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
                if attribut == "nom":
                    clients = Client.objects.filter(nom__icontains=valeur)
                else:
                    clients = Client.objects.filter(email__icontains=valeur)
            else:
                client_all = Client.objects.all()
                respoServ_all = ResponsableService.objects.filter(responsable=request.user.responsable.id)
                for respo in respoServ_all:
                    rdv_temp = RendezVous.objects.filter(
                        service=respo.service.id)
                    if rdv_temp.exists:
                        for rd in rdv_temp:
                            rdv_client.append(rd.client.id)
                for client in client_all:
                    if (client.id in rdv_client) and (client not in clients):
                        if attribut == "nom":
                            clients |= Client.objects.filter(nom__icontains=valeur)
                        else:
                            clients |= Client.objects.filter(email__icontains=valeur)
            for client in clients:
                final.append({
                    'nom': client.nom,
                    'prenom': client.prenom,
                    'email': client.email,
                    'id': client.id,
                })
            return JsonResponse({"administre": final}, status=200)
        except:
            return JsonResponse({"administre": False}, status=200)
    return JsonResponse({"administre": "Vide"}, status=200)

#méthode ajax qui recupère les responsable selon le nom ou le mail
@login_required
def getResponsableBynameOrEmail(request):
    valeur = request.GET.get("valeur", None)
    attribut = request.GET.get("attribut", None)
    final = []
    if request.is_ajax and request.method == "GET":
        try:
            if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
                if attribut == "nom":
                    users = User.objects.filter(last_name__icontains=valeur)
                else:
                    users = User.objects.filter(email__icontains=valeur)
            for user in users:
                final.append({
                    'username':
                    user.username,
                    'email':
                    user.email,
                    'first_name':
                    user.first_name,
                    'last_name':
                    user.last_name,
                    'id':
                    Responsable.objects.filter(user=user.id).first().id,
                })
            return JsonResponse({"responsable": final}, status=200)
        except:
            return JsonResponse({"responsable": False}, status=200)
    return JsonResponse({"responsable": "Vide"}, status=200)

#méthode ajax qui recupère les rendez vous
@login_required
def getRdvByAjax(request):
    rdvs = RendezVous()
    evetRdv = []
    context = {}
    color = ""
    rdvF = RendezVous.objects.none()
    if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
        rdvF = RendezVous.objects.all().order_by("-id")
    else:
        rdvs = RendezVous.objects.all().order_by("-id")
        Rservices = ResponsableService.objects.filter(responsable=request.user.responsable.id)
        for rdv in rdvs:
            for Rservice in Rservices:
                if rdv.service.id == Rservice.service.id:
                    rdvF |= RendezVous.objects.filter(service=Rservice.service.id)
    for rd in rdvF:
        debut = rd.date_r.isoformat()
        fin = rd.date_r.isoformat()

        if rd.etat == "En attente":
            color = "#2bff00"
        elif rd.etat == "Approuve":
            color = "#040675"
        elif rd.etat == "Annule":
            color = "red"
        elif rd.etat == "Reporte":
            color = "#5d0274"
        else:
            color = "#e100ff"

        a = "<a href='/administration/rdv/recuperer/{}' class=' is-success button is-small' ><span><i class='fa fa-eye'></i></span></a>".format(rd.id)
        evetRdv.append({
            'id':rd.id,
            'name':"Rendez-Vous",
            'date': [debut, fin],
            'type':"Rendez-vous",
            'color':color,
            'everyYear':False,
            'description': "Rendez-vous avec " + str(rd.client.nom) + " " + rd.client.prenom +" au service " + rd.service.nom + " à " + str(rd.heure_r.hour) +"h:" + str(rd.heure_r.minute) + "  " + a
        })
    return JsonResponse({"evt": evetRdv}, status=200)

#---------------------------INTERFACE ADMINISTRATEUR-----------------------------#
#Gestion des agents
#dashboard Responsable
@login_required
def dashboardResponsable(request):
    context = {}
    rsp = Responsable.objects.none()
    try:
        responsables = Responsable.objects.all().order_by('-id')
        for respo in responsables:
            if not respo.user.groups.filter(name="Administrateur").exists():
                rsp |= Responsable.objects.filter(id=respo.id)
        context['responsables'] = rsp
    except:
        messages.error(request, "Erreur interne au système")

    if request.is_ajax() and request.method == 'GET':
        list_=[]
        agent = Responsable.objects.all().order_by('-id')
        for ag in agent:
            if not ag.user.groups.filter(name="Administrateur").exists():
                list_.append({
                    'id':ag.id,
                    'nom':ag.user.last_name,
                    'prenom':ag.user.first_name,
                    'couleur':ag.couleur_js
                })
        return JsonResponse({"respo":list_,"erreur":0}, status=200)
    return render(request, 'administration/responsable.html', context)

#ajout responsable
@login_required
def addResponsable(request):
    form = ResponsableForm(request.POST)
    context = {}
    if form.is_valid() or not form.is_valid():
        if form.cleaned_data['mdp'] == form.cleaned_data["mdp1"]:
            responsable = Responsable()
            with transaction.atomic():
                user = User(is_superuser=False, is_active=True, is_staff=True)
                user.first_name = form.cleaned_data['prenom']
                user.last_name = form.cleaned_data['nom']
                user.email = form.cleaned_data['email']
                user.username = form.cleaned_data['nom_d_utilisateur']
                user.set_password(form.cleaned_data['mdp']) 
                us = User.objects.filter(username=user.username)
                if us.exists() :
                    messages.error(request, "Un utilisateur avec ce nom d'utiliasteur exise déjà")
                    context['form'] = form
                    context['errors'] = form.errors.items()
                    return render(request,'administration/responsable_add.html', context)
                    
                us = User.objects.filter(email=user.email)
                if us.exists() :
                    messages.error(request, "Un utilisateur avec ce mail exise déjà")
                    context['form'] = form
                    context['errors'] = form.errors.items()
                    return render(request,'administration/responsable_add.html', context)
                
                responsable.telephone = form.cleaned_data['tel_number']
                responsable.couleur_js = form.cleaned_data['couleur_js']
                responsable.couleur_conge = form.cleaned_data['couleur_off']

                rsp = Responsable.objects.filter(couleur_conge=responsable.couleur_conge)
                if rsp.exists():
                    messages.error(request, "Un responasble avec ce code couleur de congé existe déjà")
                    context['form'] = form
                    context['errors'] = form.errors.items()
                    return render(request,'administration/responsable_add.html', context)

                rsp = Responsable.objects.filter(couleur_js=responsable.couleur_js)
                if rsp.exists():
                    messages.error(request, "Un responasble avec ce code couleur de jours spécifiques existe déjà")
                    context['form'] = form
                    context['errors'] = form.errors.items()
                    return render(request,'administration/responsable_add.html', context)
                
                user.save()
                user.groups.add(Group.objects.filter(name="Agent").first().id)
                responsable.user = user
                responsable.save()
                #envoi du mail
                subject = 'Création de compte agent'
                message = 'Bonjour ' + responsable.user.first_name + ' votre compte agent  a été crée vos identifiants sont '
                message = message+'\nNom d\'utilisateur: '+ responsable.user.username +'\n'
                message= message+'mot de Passe: ' +form.cleaned_data['mdp']+ '\n'
                message = message+'Connectez vous pour modifier ces informations au besoin'
                destinataire = responsable.user.email
                expediteur = 'brunoowona12@gmail.com'
                nt = Notification()
                nt = configureNotification("ajout_agent",responsable)
                envoyerMail(nt,[responsable.user.email], 'brunoowona12@gmail.com')
                #envoyerMail(subject,message,destinataire,expediteur)

            messages.success(request, 'Responsable ajouté avec succès')
            return redirect('administration:responsable_dashboard')

        messages.error(request, "Les mots de passes ne sont pas identiques")
        context['form'] = form
        return render(request, 'administration/responsable_add.html',
                        context)
    context['form'] = form
    context['errors'] = form.errors.items()
    return render(request, 'administration/responsable_add.html', context)

#edition d'un agent
@login_required
def editResponsable(request, id):
    context = {}
    test = False
    form = ResponsableForm(request.POST)
    if form.is_valid() or not form.is_valid():
        try:
            responsable = Responsable.objects.filter(pk=id).first()
            user_e = responsable.user
            if form.cleaned_data["mdp"] != "" and form.cleaned_data[
                    "mdp"] != "":
                if not form.cleaned_data['mdp'] == form.cleaned_data['mdp1']:
                    messages.error(request,
                                   "Les mots de passe ne sont pas identiques")
                    context = {
                        "agent": responsable,
                        "user": request.user,
                        "form": form,
                    }
                    return render(request,
                                  'administration/responsable_edit.html',
                                  context)
                else:
                    test = True
            user_e.username = form.cleaned_data['nom_d_utilisateur']
            user_e.last_name = form.cleaned_data['nom']
            user_e.first_name = form.cleaned_data['prenom']
            user_e.email = form.cleaned_data['email']
            servF=[]
            services = ResponsableService.objects.filter(responsable=id)
            for serv in services:
                servF.append(serv.service)

            us = User.objects.filter(username=user_e.username)
            if us.exists() and us.first().id != user_e.id:
                messages.error(request, "Un utilisateur avec ce nom d'utiliasteur existe déjà")
                context['form'] = form
                context['agent'] = Responsable.objects.filter(pk=id).first()
                context['services'] = servF
                context['errors'] = form.errors.items()
                return render(request,'administration/responsable_edit.html', context)
                
            us = User.objects.filter(email=user_e.email)
            if us.exists() and us.first().id != user_e.id:
                messages.error(request, "Un utilisateur avec ce mail existe déjà")
                context['form'] = form
                context['agent'] = Responsable.objects.filter(pk=id).first()
                context['services'] = servF
                context['errors'] = form.errors.items()
                return render(request,'administration/responsable_edit.html', context)
                responsable.telephone = form.cleaned_data['tel_number']

            if request.POST.get("nom_d_utilisateur_zimbra",None) is not None and request.POST.get("mdpZ",None) is not None:
                
                if form.cleaned_data['nom_d_utilisateur_zimbra'] != "":
                    responsable.login_zimbra = form.cleaned_data['nom_d_utilisateur_zimbra']
                if form.cleaned_data['mdpZ'] != "":
                    responsable.mot_de_passe_zimbra = form.cleaned_data['mdpZ']
            
            if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
                responsable.couleur_js = form.cleaned_data['couleur_js']
                responsable.couleur_conge = form.cleaned_data['couleur_off']
                rsp = Responsable.objects.filter(couleur_conge=responsable.couleur_conge)
                if rsp.exists() and rsp.first().id != responsable.id:
                    messages.error(request, "Un responasble avec ce code couleur de congé existe déjà")
                    context['form'] = form
                    context['agent'] = Responsable.objects.filter(pk=id).first()
                    context['services'] = servF
                    context['errors'] = form.errors.items()
                    return render(request,'administration/responsable_edit.html', context)

                rsp = Responsable.objects.filter(couleur_js=responsable.couleur_js)
                if rsp.exists() and rsp.first().id != responsable.id:
                    messages.error(request, "Un responasble avec ce code couleur de jours spécifiques existe déjà")
                    context['form'] = form
                    context['agent'] = Responsable.objects.filter(pk=id).first()
                    context['services'] = servF
                    context['errors'] = form.errors.items()
                    return render(request,'administration/responsable_edit.html', context)
            responsable.save()
            
            #adaptation des JS et JO existant au nouveau code couleur
            js = JourSpecifique.objects.filter(responsable=responsable)
            if js.exists():
                for j in js:
                    j.couleur = responsable.couleur_js
                    j.save()
            jo = Evenement.objects.filter(responsable=responsable)
            if jo.exists():
                for j in jo:
                    j.color = responsable.couleur_conge
                    j.save()
            message=""
            if test == True:
                messages.success(request,"Vos informations ont été modifier avec succès veuillez vous reconnecter avec votre nouveau mot de passe")
                nt = Notification()
                nt = configureNotification("modification_agent",responsable,form.cleaned_data['mdp'])
                envoyerMail(nt,[responsable.user.email], 'brunoowona12@gmail.com')
                user_e.set_password(form.cleaned_data["mdp"])
                
            else:
                messages.success(request, "Vos informations ont été modifier avec succès")
                nt = Notification()
                nt = configureNotification("modification_agent",responsable)
                envoyerMail(nt,[responsable.user.email], 'brunoowona12@gmail.com')
            user_e.save()

            if request.user.groups.filter(name="Administrateur").exists() or request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
                return redirect('administration:responsable_dashboard')
            return redirect('administration:dashboard') 
        except Exception as e:
            messages.error(request,str(e))
            context = {
                "agent": Responsable.objects.filter(pk=id).first(),
                "user": Responsable.objects.filter(pk=id).first().user,
                "form": form,
            }
            context['errors'] = form.errors.items()
            return render(request, 'administration/responsable_edit.html',context)
    context = {
        "agent": Responsable.objects.filter(pk=id).first(),
        "user": Responsable.objects.filter(pk=id).first().user,
        "form": form,
    }
    context['errors'] = form.errors.items()
    return render(request, 'administration/responsable_edit.html', context)

#recupération pour edition
@login_required
def getResponsableToEdit(request, id):
    context = {}
    servF = []
    try:
        if request.user.groups.filter(name="Administrateur").exists():  
            responsable = Responsable.objects.filter(pk=id)
        elif request.user.groups.filter(name="Adjoint").exists() or request.user.groups.filter(name="Superviseur").exists():
            responsable =  Responsable.objects.filter(pk=id)
        else:
            responsable = Responsable.objects.filter(pk=request.user.responsable.id)
        if responsable.exists():
            responsable = responsable.first()
            if responsable.user.groups.filter(name="Agent"):
                services = ResponsableService.objects.filter(responsable=responsable)
                for serv in services:
                    servF.append(serv.service)
            form = ResponsableForm({
                'nom':responsable.user.last_name,
                'prenom':responsable.user.first_name,
                'tel_number':responsable.telephone,
                'email':responsable.user.email,
                'nom_d_utilisateur':responsable.user.username,
                'couleur_js': responsable.couleur_js,
                'couleur_off': responsable.couleur_conge,
                'nom_d_utilisateur_zimbra': responsable.login_zimbra,
                'mdpZ':responsable.mot_de_passe_zimbra,
            })
            context = {
                "agent": responsable,
                "user": responsable.user,
                "form": form,
                "services":servF
            }
            return render(request, 'administration/responsable_edit.html',context)
    except:
        context['test'] = " "
        #messages.error(request, 'Erreur interne au système')
        #return redirect('administration:responsable_dashboard')
    context['errors'] = "Erreur inconnue"
    return render(request, 'administration/responsable_edit.html', context)

#suppression d'un agent
@login_required
def deleteResponsable(request, id):
    try:
        responsable = Responsable.objects.filter(pk=id)
        if responsable.exists():
            responsable = responsable.first()
            user = responsable.user
            responsable.delete()
            user.delete()
            messages.success(request, "Responsable supprimer avec success")
            return redirect('administration:responsable_dashboard')
    except:
        messages.error(request, "Responsable inexistant")
        return redirect('administration:responsable_dashboard')
    messages.error(request,
                   "Erreur de suppréssion de service veuillez réessayer")
    return redirect('administration:responsable_dashboard')

#go to add Responsable
def goToAddResponsable(request):
    form = ResponsableForm()
    context = {'form': form}
    return render(request, 'administration/responsable_add.html', context)

#>>>>>>>>>>>> gestion des services 

#dashboard service
@login_required
def dashboardService(request):
    context = {}
    try:
        services = Service.objects.all().order_by('-id')
        context['services'] = services
    except:
        messages.error(request, "Erreur interne au système")
    return render(request, 'administration/service.html', context)

#create service
@login_required
def addService(request):
    form = ServiceForm(request.POST)
    if form.is_valid() or not form.is_valid():
        try:
            with transaction.atomic():
                service = Service()
                service.nom = form.cleaned_data['nom']
                service.duree_rdv = form.cleaned_data['duree_rdv']
                service.save()
                for responsable in form.cleaned_data['responsable']:
                    ResponsableService.objects.create(service=service,responsable=responsable)
            messages.success(request, "service ajouté avec success")
            form = ServiceForm()
            return redirect('administration:service_dashboard')
        except:
            context = {'form': form}
            messages.error(request,"erreur Interne au système veuillez reéssayer")
            return render(request,'administration/service_add.html', context)
    context = {'form': form}
    messages.error(request, "erreur durant l'ajout du service")
    return render('administration/service_add.html', context)

#aller à ajout de service
@login_required
def goToAddService(request):
    form = ServiceForm()
    context = {'form':form}
    return render(request,'administration/service_add.html',context)

#recupération pour édition
@login_required
def getServiceToEdit(request, id):
    service = Service.objects.filter(pk=id)
    responsableService = ResponsableService.objects.filter(service=id)
    context = {}
    if service.exists():
        service = service.first()
        form = ServiceForm({
            'nom': service.nom,
            'duree_rdv': service.duree_rdv
        })
        context = {
            'form': form,
            'service': service,
            'responsables': responsableService
        }
        return render(request, 'administration/service_edit.html', context)
    messages.error(request, 'Service inexistant')
    return redirect('administration:service_dashboard')

#Edit service
@login_required
def editService(request, id):
    form = ServiceForm(request.POST)
    if form.is_valid() or not form.is_valid():
        try:
            with transaction.atomic():
                service = Service.objects.filter(pk=id).first()
                service.nom = form.cleaned_data['nom']
                service.duree_rdv = form.cleaned_data['duree_rdv']
                service.save()
                for responsable in form.cleaned_data['responsable']:
                    ResponsableService.objects.create(service=service,responsable=responsable)
            messages.success(request, "service Modifié  avec success")
            form = ServiceForm()
            return redirect('administration:service_dashboard')
        except:
            responsableService = ResponsableService.objects.filter(service=id)
            context = {
                'form': form,
                'service': service,
                'responsables': responsableService
            }
            messages.error(request, "erreur Interne au système veuillez reéssayer")
            return render(request, 'administration/service_edit.html', context)
    context = {'form': form}
    messages.error(request, "erreur durant l'ajout du service")
    return render('administration/service_add.html', context)

#delete responsable service
@login_required
def deleteResponsableService(request,id):
    try:
        service = ResponsableService.objects.filter(pk=id).first().service.id
        ResponsableService.objects.filter(pk=id).first().delete()
        messages.success(request,'Responsable de service supprimmer avec succès')
    except:
        messages.error(request,'Echec de suppression')
    return redirect('administration:service_get_edit', id=service)
    
#suppréssion service
@login_required
def deleteService(request, id):
    try:
        service = Service.objects.filter(pk=id)
        responsablesService = ResponsableService.objects.filter(service=id)
        for respo in responsablesService:
            respo.delete()
        if service.exists():
            service = service.first()
            service.delete()
            messages.success(request, "Service supprimer avec success")
            return redirect('administration:service_dashboard')
    except:
        messages.error(request, "service inexistant")
        return redirect('administration:service_dashboard')
    messages.error(request, "Erreur de suppréssion de service veuillez réessayer")
    return redirect('administration:service_dashboard')

#---------------------EXPORT EXCEL----------------------------
#go to export in excel
@login_required
def gotToExportExcel(request):
    rdvs = RendezVous.objects.all().order_by('-id')
    context={
        'rdvs':rdvs
    }
    return render(request,'administration/import_export.html',context)
    
#importer les rdv en excel
@login_required
def exportExcel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=RDV'+ str(datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Rendez-vous')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['service','date','heure début','heure fin','Administrés','Emails administrés','nombre personnes','Responsable']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    if request.is_ajax():
        debut = request.GET.get("debut", None)
        fin = request.GET.get("fin", None)
        tabDate = debut.split("-")
        tabDateF = fin.split("-")
        debut = date(int(tabDate[0]), int(tabDate[1]), int(tabDate[2]))
        fin = date(int(tabDateF[0]), int(tabDateF[1]), int(tabDateF[2]))
        rows = RendezVous.objects.filter(date_r__gte=debut,date_r__lte=fin).values_list('service','date_r','heure_r','heure_f','client','client','nombre_personne','responsable')
    else:
        rows = RendezVous.objects.all().values_list('service','date_r','heure_r','heure_f','client','client','nombre_personne','responsable')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num == 0:
                nom_service = Service.objects.filter(pk=int(row[col_num])).first().nom
                ws.write(row_num,col_num,nom_service, font_style)
            elif col_num == 4:
                nom_administre = Client.objects.filter(pk=int(row[col_num])).first().nom +"  "+Client.objects.filter(pk=int(row[col_num])).first().prenom
                ws.write(row_num,col_num,nom_administre, font_style)
            elif col_num == 5:
                email_administre = Client.objects.filter(pk=int(row[4])).first().email 
                ws.write(row_num,col_num,email_administre, font_style)
            elif col_num == 7:
                email_responsable = Responsable.objects.filter(pk=int(row[col_num])).first().user.email
                ws.write(row_num,col_num,email_responsable, font_style)
            else:
                ws.write(row_num,col_num,str(row[col_num]), font_style)
    wb.save(response)
    return response

#upload an import models
@login_required
def uploadEmptyMode(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=RDV'+ str(datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Rendez-vous')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['service','date','heure','Administrés','Emails administrés','nombre personnes']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num], font_style)
    wb.save(response)
    return response

#import from an excel file
@login_required
def importFromExcelFiles(request):
    fichier = request.FILES.get('fichier')
    data = None
    if not fichier.name.endswith('xls'):
        messages.error(request,'Mauvaise extension')
        return redirect('administration:get_in_excel')
    try:
        data = xlrd.open_workbook(filename=None, file_contents=fichier.read(), formatting_info=True)
    except Exception as e:
        messages.error(request,str(e))
        return redirect('administration:get_in_excel')

    table = data.sheets()[0]
    nligne = table.nrows
    ncolonnes = table.ncols
    colnames = table.row_values(0)
    liste_finale =[]
    for i in range(nligne):
        liste_temp = []
        for j in range(ncolonnes):
            cell_values = table.row_values(i)[j]
            liste_temp.append(cell_values)
        liste_finale.append(liste_temp)
    del(liste_finale[0])
    for liste in liste_finale:
        check = False
        text = ""
        client = Client.objects.filter(email__icontains=liste[5])
        if client.exists():
            client = client.first()
        else:
            
            client = Client.objects.create(
                nom=liste[4],
                prenom = liste[4],
                email=liste[5],
                password="".join([random.choice(string.ascii_letters) for _ in range(10)]) 
            )
            check = True
        try: 
            datef = ""
            serial = liste[1]
            if type(serial) == str:
                temp = liste[1].split("-")
                datef = date(int(temp[0]),int(temp[1]),int(temp[2]))
            elif type(serial) == float:
                seconds = (serial - 25569) * 86400.0
                datef = date.fromtimestamp(seconds)
            else:
                pass
                #return JsonResponse({"evt": liste[2].split(":")[1] }, status=200)
            serv = Service.objects.filter(nom__icontains=str(liste[0]))
            if not serv.exists():
                messages.error(request,'Service inexistant')
                return redirect('administration:get_in_excel')
            rdv = RendezVous()
            rdv.service = serv.first()
            rdv.client = client
            rdv.nombre_personne = int(liste[6])
            rdv.urbanisme = False
            rdv.by_phone = False
            rdv.date_r = datef
            user_= User.objects.filter(email=str(liste[7])).first()
            rdv.responsable = Responsable.objects.filter(user=user_).first()
            rdv.heure_r = time(int(liste[2].split(":")[0]),int(liste[2].split(":")[1]),int(liste[2].split(":")[2]),0)
            rdv.heure_f = time(int(liste[3].split(":")[0]),int(liste[3].split(":")[1]),int(liste[3].split(":")[2]),0)
            rdv.save()
            updateZimbraCal(rdv)
        except Exception as e:
            messages.error(request,'Problème avec le modèle d\'importation')
            return redirect('administration:get_in_excel')    
    messages.success(request,'Importation terminée avec succes')
    return redirect('administration:get_in_excel')
