from django.urls import path
from . import views

app_name="rdv"

urlpatterns = [
    path('', views.home, name="home_rdv"),
    path('nouveau/', views.prendre_rdv, name="nouveau"),
    path('add/', views.AddRdv ,name='add'),
    path('responsable/get/', views.GetResponsable, name="responsableget"),
    path('good/<int:id>',views.updateZimbraCal,name="good"),
    path('crenaux/get/',views.getCreneaux,name="get_creneau_ajax"),
    path('rdv/get/heures',views.GetHorairesDuJour,name="get_heure_ajax"),
    path('rdv/get/agent',views.GetResponsableService,name="get_agent_ajax"), 
    path('rdv/jours_libre', views.buildFreeDate,name="jours_libre"),
    path('rdv/agent_libre', views.checkIfAgentBusy,name="agent_libre"),
    path('rdv/creneau_libre', views.checkIfCreneauAvailable,name="creneau_libre"),
    path('rdv/adresseT', views.getAllAdresse,name="adresseTravaux"),
]