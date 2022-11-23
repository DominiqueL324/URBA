from django import forms
from django.forms import ModelChoiceField
from rdv.models import Responsable

class LoginForm(forms.Form):

    login = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class':'form-control','id':'text','placeholder':'Nom d\'utilisateur....'}),
        required=True
        )
    
    mdp = forms.CharField(
        label="Mot de passe",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'form-control','id':"mdp", 'placeholder':"Mot de passe..."}),
        required=True
        )

class EventForm(forms.Form):

    responsable = forms.ModelChoiceField(
        queryset=Responsable.objects.all(),
        required=False,
        empty_label="Sélectionnez un agent",
        widget=forms.Select(attrs={'class':'input is-small','id':"inputResponsable"})
    )

    name = forms.CharField(
        label="Nom de  l'évènement",
        max_length=200,
        widget=forms.TextInput(attrs={'class':'input is-small','id':'nameEvent'}),
        required=True

    )
    description = forms.CharField(
        label="Description de l'évènement",
        max_length=1000,
        widget=forms.Textarea(attrs={'class':'input is-small','id':'descEvent','style':'height:150px;'}),
        required=False
    )

    date_d = forms.DateField(
        label="Date de début",
        widget=forms.DateInput(attrs={'class':'input is-small','id':"dateDebEvent","type":"date"}),
        required=True
        )
    
    date_f = forms.DateField(
        label="Date de Fin",
        widget=forms.DateInput(attrs={'class':'input is-small','id':"dateEndEvent","type":"date"}),
        required=True
        )
    
    color = forms.CharField(
        label="Couleur",
        widget=forms.TextInput(attrs={'class':'input is-small','id':"colorEvent","type":"color","value":"#ff0000",'style':'height:40px;'}),
        required=False
        )

class ResponsableForm(forms.Form):

    nom = forms.CharField(
        label="Nom de famille",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"nom"}),
        required=True
        )
    
    couleur_off = forms.CharField(
        label="Couleur de jours off",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"couleur_off",'type': 'color'}),
        required=False
        )

    couleur_js = forms.CharField(
        label="Couleur de jours Spécifiques",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"couleur_js",'type': 'color'}),
        required=False
        )

    prenom = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"prenom"}),
        required=True
        )
    
    tel_number = forms.IntegerField(
            label="Téléphone",
            widget=forms.NumberInput(attrs={'class':'input is-big','id':"telephone1"}),
            required=True
        )

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

    nom_d_utilisateur_zimbra = forms.CharField(
        label="Nom d'utilisateur zimbra",
        max_length=100,
        widget=forms.TextInput(attrs={'class':'input is-small','id':"usernameZ"}),
        required=True
        )

    mdpZ = forms.CharField(
        label="Mot de passe Zimbra",
        max_length=200,
        widget=forms.PasswordInput( attrs={'class':'input is-small','id':"mdpZ", 'placeholder':"Mot de passe Zimbra..."}),
        required=False
        )
    