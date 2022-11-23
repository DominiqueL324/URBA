from django.shortcuts import render, redirect
from rdv.form import RdvForm


def home(request):
    formulaire = RdvForm() 
    context = {
        'form': formulaire,
    }
    return render(request,'home.html',context)

def login(request):
    return redirect('administration:login')