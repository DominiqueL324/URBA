from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from rdv.models import Responsable,Service

# Create your models here.

#fs = FileSystemStorage(location='/rdv/medias')
class Adjoint(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    adresse = models.CharField("Adresse",max_length=300,null=True)
    telephone = models.IntegerField('Téléphone')

    def __str__(self):
        return self.user.first_name+" "+self.user.last_name+" "+ str(self.user.id) 
        
    class Meta:
        verbose_name = "Adjoint/Superviseur"


class Administrateur(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    adresse = models.CharField("Adresse",max_length=300,null=True)
    telephone = models.IntegerField('Téléphone')

    def __str__(self):
        return self.user.first_name+" "+self.user.last_name+" "+ str(self.user.id) 
        
    class Meta:
        verbose_name = "Administrateur"

class JourSpecifique(models.Model):
    responsable = models.ForeignKey(Responsable,on_delete=models.CASCADE,null=True)
    date = models.DateField("Jour",null=True)
    heure_debut = models.TimeField("Heure de début")
    heure_fin = models.TimeField("Heure de fin")
    id_jour = models.IntegerField("Id du jour")
    date_debut = models.DateField("Date de debut",null=True)
    date_fin = models.DateField("Date de fin",null=True)
    jour_semaine = models.CharField('jour de la semaine',max_length=20, null=True)
    service = models.ForeignKey(Service,on_delete=models.CASCADE,null=True)
    couleur = models.CharField("Couleur du JS",max_length=50,null=True)

