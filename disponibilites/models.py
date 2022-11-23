from django.db import models
from rdv.models import Responsable, RendezVous
from django.contrib.auth.models import User

# Create your models here.

class Evenement(models.Model):
    name = models.CharField("Nom de l'évènemnt",max_length=400)
    date_d = models.DateField("Date de debut",auto_now=False,auto_now_add=False)
    date_f = models.DateField("Date de fin",auto_now=False,auto_now_add=False)
    type_e = models.CharField("Type d'evènement",max_length=100,default="holiday")
    descriptions = models.CharField("Description de l'évènement",max_length=1000,default=" ")
    color = models.CharField("Couleur de l'évènement",max_length=100,default="#1ce")
    everyYear = models.BooleanField("Chaque année",default=False)
    responsable = models.ForeignKey(Responsable,on_delete=models.CASCADE)

    def __str__(self):
        return self.name+" description: "+ self.descriptions

    class Meta:
        verbose_name = "Evènement"

class Notification(models.Model):
    sujet = models.CharField("Subject",max_length=500,null=True)
    body = models.TextField("Contenu du mail",max_length=2000,null=True)
    cas = models.CharField("Cas de notification",max_length=50,null=True) 
