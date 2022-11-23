from django.contrib import admin
from .models import RendezVous,Responsable,Service,Client,ResponsableService,CreneauHoraire

# Register your models here.

@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):

    search_fields=['nom','email','telephone']

    list_filter=[]
    #les champs à afficher
    fieldsets = [
        (None, {'fields':['user','telephone','adresse']})
    ]

    #fields=["nom","prenom","email",'telephone']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    search_fields=['nom']
    list_filter=['nom','duree_rdv']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    search_fields=['nom','email']

    list_filter=['nom','email']
    #si on ne veut pas que certains objets soient ajouté depuis l'interface d'administration
    #on surcharge la méthode has_add_permission() dans l'objet en question on retur juste False
    def has_add_permission(self, request):
        return False

@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):

    search_fields=['date_r','service']

    list_filter=['date_r','service']
    #si on ne veut pas que certains objets soient ajouté depuis l'interface d'administration
    #on surcharge la méthode has_add_permission() dans l'objet en question on retur juste False

@admin.register(ResponsableService)
class ResponsableServiceAdmin(admin.ModelAdmin):

    search_fields=['responsable','service']

    list_filter=['responsable','service']
    #si on ne veut pas que certains objets soient ajouté depuis l'interface d'administration
    #on surcharge la méthode has_add_permission() dans l'objet en question on retur juste False


@admin.register(CreneauHoraire)
class CreneauHoraireAdmin(admin.ModelAdmin):

    search_fields=['heure_debut','heure_fin','jour']

    list_filter=['heure_fin','heure_debut','jour','service']
    #si on ne veut pas que certains objets soient ajouté depuis l'interface d'administration
    #on surcharge la méthode has_add_permission() dans l'objet en question on retur juste False

    