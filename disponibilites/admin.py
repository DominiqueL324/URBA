from django.contrib import admin
from .models import Evenement

# Register your models here.

@admin.register(Evenement)
class ResponsableAdmin(admin.ModelAdmin):

    search_fields=['name','date_d','date_f']

    list_filter=[]
    #les champs à afficher
    fieldsets = [
        (None, {'fields':['name','date_d','date_f','type_e','descriptions','color','everyYear','responsable']})
    ]

    #fields=["nom","prenom","email",'telephone']


    
