from django import forms
from rdv.models import Responsable,Service,Client,ResponsableService
from .models import Adjoint

CHOICES =[(True,'Oui'),(False,'Non')]

class AdjointForm(forms.Form):

    ROLE = (('', '*******************'),('Adjoint', 'Adjoint'),('Superviseur', 'Superviseur'),)

    nom = forms.CharField(
        label="Nom de famille",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"nom"}),
        required=True
        )

    prenom = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"prenom"}),
        required=True
        )
    
    tel_number = forms.IntegerField(
        label="Téléphone",
        widget=forms.NumberInput(attrs={'class':'input is-small','id':"telephone1"}),
        required=True
        )
    
    role = forms.ChoiceField(
        choices=ROLE,
        widget=forms.Select(attrs={'class':'input is-small','id':"role"}),
        required=True)

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class':'input is-small','id':'email'}),
        required=True
        )
        
    nom_d_utilisateur = forms.CharField(
        label="Nom d'utilisateur",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"username"}),
        required=True
        )
    
    mdp = forms.CharField(
        label="Mot de passe",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'input is-small','id':"mdp", 'placeholder':"Mot de passe..."}),
        required=False
        )
    
    mdp1 = forms.CharField(
        label="Mot de passe",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'input is-small','id':"mdp1", 'placeholder':"Mot de passe..."}),
        required=False
        )
    
class ServiceForm(forms.Form):

    nom = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class':'input is-small','id':'nomService','placeholder':'Nom du service....'}),
        required=True
        )
    
    duree_rdv = forms.IntegerField(
        label="Durée des RDV",
        widget=forms.NumberInput( attrs={'class':'input is-small','id':"dureeRdv"}),
        required=True
        )
    
    responsable = forms.ModelMultipleChoiceField(
        queryset=Responsable.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class':'input is-small','id':"ResponsableService"})
    )

class RdvFormAdmin(forms.Form):

    phone = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES,required=True,)

    fichier = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True,'id':"formFileMultiple",'type':'file','draggable':True}),required=False)

    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        empty_label="Sélectionnez un service",
        widget=forms.Select(attrs={'id':"inputService"})
    )

    adresseTravaux = forms.CharField(
        label="Adresse des travaux",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"adresseTravauxInput", 'placeholder':"Adresse des travaux...."}),
        required=True
    )


    administre = forms.ModelChoiceField(
        queryset=Client.objects.all().order_by("nom"),
        required=True,
        empty_label="Sélectionnez un administre",
        widget=forms.Select(attrs={'id':"administreI"})
    )
    
    heure = forms.TimeField(
            widget=forms.TimeInput(attrs={'class':'input is-small','id':"inputHeure",'type':'time'},format='%H:%M'),
            required=True,
        )

    heureF = forms.TimeField(
            widget=forms.TimeInput(attrs={'class':'input is-small','id':"inputHeureFin",'type':'time',"readonly":"readonly"},format='%H:%M'),
            required=False,
        )
    
    date = forms.DateField(
            label="Date",
            widget=forms.DateInput(attrs={'class':'input is-small','id':"inputDate",'type':'date'}),
            required=True
        )
    
    nombre_person = forms.IntegerField(
        label="Nombre de Personnes",
        widget=forms.NumberInput(attrs={'class':'input is-small','id':"inputNombre"}),
        required=True
        )

class AdministreForm(forms.Form):

    nom = forms.CharField(
        label="Nom de famille",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"nom", 'placeholder':"Nom de famille..."}),
        required=True
        )

    prenom = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"prenom", 'placeholder':"Prénom..."}),
        required=True
        )
    
    tel_number = forms.IntegerField(
            label="Téléphone",
            widget=forms.NumberInput(attrs={'class':'input is-small','id':"telephone1"}),
            required=True
        )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class':'input is-small','id':'email','placeholder':'email'}),
        required=True
        )
    
    adress = forms.CharField(
        label="Adresse",
        max_length=200,
        widget=forms.TextInput( attrs={'class':'input is-small','id':"adresse", 'placeholder':"Adresse..."}),
        required=True
        )
    
    mdp = forms.CharField(
        label="Mot de passe",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'input is-small','id':"mdp"}),
        required=False
        )
    
    mdp1 = forms.CharField(
        label="Mot de passe",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'input is-small','id':"mdp1"}),
        required=False
        )



    