from django import forms
from rdv.models import Service

CHOICES =[(True,'Oui'),(False,'Non')]

class LoginFormAdministre(forms.Form):
    login = forms.EmailField(
        label="Nom d'utilisateur",
        widget=forms.EmailInput(attrs={'class':'form-control','id':'text','placeholder':'votre Email....'}),
        required=True
        )
    
    mdp = forms.CharField(
        label="Mot de passe",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'form-control','id':"mdp", 'placeholder':"Mot de passe..."}),
        required=True
        )


class AdministreForm(forms.Form):

    nom = forms.CharField(
        label="Nom de famille",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control','id':"nom", 'placeholder':"Nom de famille..."}),
        required=True
        )

    prenom = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control','id':"prenom", 'placeholder':"Prénom..."}),
        required=True
        )
    
    tel_number = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'id':'telephone',
            'class':'form-control',
            'type':'tel',
            })
        )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class':'form-control','id':'email','placeholder':'email'}),
        required=True
        )
    
    adress = forms.CharField(
        label="Adresse",
        max_length=200,
        widget=forms.TextInput( attrs={'class':'form-control','id':"adresse", 'placeholder':"Adresse..."}),
        required=True
        )
    
    mdp = forms.CharField(
        label="Mot de passe",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'form-control','id':"mdp"}),
        required=False
        )
    
    mdp1 = forms.CharField(
        label="Mot de passe",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'form-control','id':"mdp1"}),
        required=False
        )
    
class RdvFormAdmini(forms.Form):

    urbanisme = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES,required=True)

    phone = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES,required=True)

    fichier = forms.FileField(widget=forms.ClearableFileInput(attrs={'class':'form-control','multiple': True,'id':"formFileMultiple",'type':'file','draggable':True}),required=False)

    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=True,
        empty_label="Sélectionnez un service",
        widget=forms.Select(attrs={'id':"inputService",'class':'form-control'})
    )
    adresseTravaux = forms.CharField(
        label="Adresse des travaux",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control','id':"inputAdresseTravaux", 'placeholder':"Adresse des travaux...."}),
        required=True
        )
    
    heure = forms.TimeField(
            widget=forms.TimeInput(attrs={'class':'form-control','id':"inputHeure",'type':'time',"readonly":"readonly"},format='%H:%M'),
            required=True,
        )
    
    heureF = forms.TimeField(
            widget=forms.TimeInput(attrs={'class':'form-control','id':"inputHeureFin",'type':'time',"readonly":"readonly"},format='%H:%M'),
            required=True,
        )
    
    date = forms.DateField(
        label="Date",
        widget=forms.DateInput(attrs={'class':'form-control','id':"inputDate",'type':'date'}),
        required=True
        )
    
    nombre_person = forms.IntegerField(
        label="Nombre de Personnes",
        widget=forms.NumberInput(attrs={'class':'form-control','id':"inputNombre"}),
        required=True
        )