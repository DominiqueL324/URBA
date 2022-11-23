from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User

# Create your models here.

#fs = FileSystemStorage(location='/rdv/medias')
class Responsable(models.Model):  
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    adresse = models.CharField("Adresse",max_length=300,null=True)
    telephone = models.IntegerField('Téléphone')
    couleur_js = models.CharField("code couleur Jours spécifiques",max_length=60,null=True)
    couleur_conge = models.CharField("code couleur Jours off",max_length=60,null=True)
    login_zimbra = models.CharField("Nom d'utilisateur zimbra",max_length=100,null=True,default="")
    mot_de_passe_zimbra = models.CharField("Mot de passe Zimbra",max_length=100,null=True,default="")

    def __str__(self):
        return self.user.first_name+" "+self.user.last_name
        
    class Meta:
        verbose_name = "responsable"

class Service(models.Model):
    nom = models.CharField("Nom",max_length=200)
    duree_rdv = models.IntegerField("Durée des RDV dans ce service",default=45)
    debut_pause = models.TimeField("Début de la pause",auto_now_add=False,auto_now=False,null=True)
    fin_pause = models.TimeField("Fin de la pause",auto_now=False,auto_now_add=False,null=True)
    
    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "service"

class CreneauHoraire(models.Model):
    heure_debut = models.TimeField("Heure de début", auto_now_add=False, auto_now=False, null=True)
    heure_fin = models.TimeField("Heure de Fin", auto_now=False, auto_now_add=False, null=True)
    service = models.ForeignKey(Service,on_delete=models.CASCADE,null=True)
    jour = models.CharField("Jour de la semaine",max_length=10,
        choices=[('Lundi','Lundi'),('Mardi','Mardi'),('Mercredi','Mercredi'),('Jeudi','Jeudi'),('Vendredi','Vendredi')],default='Lundi'
    )
    def __str__(self):
        return  self.service.nom+" ouvert le "+self.jour+" de "+ str(self.heure_debut.hour)+'h:'+str(self.heure_debut.minute)+' à '+ str(self.heure_fin.hour)+'h:'+str(self.heure_fin.minute)


class Fichier(models.Model):
    id = models.AutoField(primary_key=True)
    fichier = models.FileField(upload_to="fichier/",max_length=500)


class ResponsableService(models.Model):
    service = models.ForeignKey(Service,on_delete = models.CASCADE)
    responsable = models.ForeignKey(Responsable,on_delete=models.CASCADE)
    def __str__(self):
        return self.service.nom+" --- Responsable: "+self.responsable.user.last_name
        
    class Meta:
        verbose_name = "Responsable de service"

class Client(models.Model):
    nom = models.CharField("Nom",max_length=200,null=True)
    prenom = models.CharField("Prenom",max_length=200,null=True)
    email = models.EmailField("Email",max_length=300)
    adresse = models.CharField("Adresse",max_length=300,null=True)
    telephone = models.IntegerField('Téléphone',null=True)
    password = models.CharField("Mot de passe", max_length=300,default="password")

    def __str__(self):
        return self.nom+" "+self.prenom

    class Meta:
        verbose_name = "client"

class RendezVous(models.Model):
    by_phone = models.BooleanField("Rendez-vous Téléphonique",default=False)
    urbanisme = models.BooleanField("Avez vous déjà pris contact avec le service d'urbanisme",default=False)
    date_r = models.DateField("Date Rdv")
    heure_r = models.TimeField('Heure Rdv')
    heure_f = models.TimeField('Heure de fin Rdv',null=True)
    nombre_personne = models.IntegerField('Nombre de Personne')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    fichiers = models.ManyToManyField(Fichier,"rdv_fichier")
    etat = models.CharField("Etat du Rdv",max_length=30,default="En attente",null=True)
    responsable = models.ForeignKey(Responsable,on_delete=models.CASCADE,null=True)
    adresseTarvaux = models.CharField("Adresse des travaux",max_length=30,default=" ",null=True)

    def __str__(self):
        return self.client.nom +" "+self.client.prenom +" service: "+self.service.nom
    
    class Meta:
        verbose_name = "rendez-vous"
        verbose_name_plural = "rendez-vous"

