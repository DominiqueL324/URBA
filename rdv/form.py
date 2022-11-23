from django import forms
from .models import Service
from intl_tel_input.widgets import IntlTelInputWidget
from django.forms.utils import ErrorList
from django.forms import ModelChoiceField


CHOICES =[(True,'Oui'),(False,'Non')]

class OwnError(ErrorList):

    def __str__(self):
        return self.as_divs()
        
    def as_divs(self):
        if not self: return ''
        return '<div class="errorlist">%s</div>' % ''.join(['<p class="small error">%s</p>' % e for e in self])

class RdvForm(forms.Form):

    urbanisme = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES,required=True)

    phone = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES,required=True)

    fichier = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True,'id':"formFileMultiple",'type':'file','class':'form-control','draggable':True}),required=False)

    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=True,
        empty_label="Sélectionnez un service",
        widget=forms.Select(attrs={'class':'form-control','id':"inputService"})
    )

    adresseTravaux = forms.CharField(
        label="Adresse des travaux",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control','id':"inputAdresseTravaux", 'placeholder':"Adresse des travaux...."}),
        required=True
        )

    nom = forms.CharField(
        label="Nom de famille",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control','id':"inputNom", 'placeholder':"Nom de famille..."}),
        required=True
        )

    prenom = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control','id':"inputPrenom", 'placeholder':"Prénom..."}),
        required=True
        )
    
    tel_number = forms.IntegerField(
        label="Numéro de téléphone",
        widget=forms.NumberInput(attrs={'class':'form-control','id':"telephone1"}),
        required=True
        )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class':'form-control','id':'inputEmail4','placeholder':'email'}),
        required=True
        )
    
    adress = forms.CharField(
        label="Adresse",
        max_length=200,
        widget=forms.TextInput( attrs={'class':'form-control','id':"inputAdresse", 'placeholder':"ADRESSE DE SAINT-MEDARD-EN-JALLES"}),
        required=True
        )
    
    heure = forms.TimeField(
            widget=forms.TimeInput(attrs={'class':'form-control','min':"08:00",'datetime.timedelta.min.hours':"17:00","readonly":"readonly",'id':"inputHeure",'type':'time'},format='%H:%M'),
            required=True,
        )
    
    heureF = forms.TimeField(
            widget=forms.TimeInput(attrs={'class':'form-control','id':"inputHeureFin",'type':'time',"readonly":"readonly"},format='%H:%M'),
            required=True,
        )
    
    date = forms.DateField(
        label="Date",
        widget=forms.DateInput(attrs={'class':'form-control','id':"inputDate",'readonly':'readonly'}),
        required=True
        )
    
    nombre_person = forms.IntegerField(
        label="Nombre de Personnes",
        widget=forms.NumberInput(attrs={'class':'form-control','id':"inputNombre",'max':'2','min':'1'}),
        required=True
        )

    