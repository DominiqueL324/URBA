from django.urls import path
from . import views

app_name="disponibilites"

urlpatterns = [
    path('', views.LoginPage, name="login"),
    path('logout', views.logoutUser, name="logout"),
    path('dashboard', views.dashboard ,name='dashboard'),
    path('dashboard/rdv', views.getMyRdv ,name='dashboard_rdv'),
    path('dashboard/rdv/validate/<int:id>', views.validate ,name='validate'),
    path('dashboard/rdv/validate/go/<int:id>', views.validerRdv ,name='validate_go'),
    path('dashboard/event/add', views.gotToAddEventPage,name='event_add'),
    path('dashboard/event', views.getMyEvent,name='dashboard_evt'),
    path('dashboard/event/add/go', views.AddEvenement,name='event_add_go'),
    path('dashboard/event/get', views.GetEvenement,name='event_get'),
    path('dashboard/event/get/rdv', views.GetEventForAdministrateCalendar,name='event_get_for_rdv'),
    path('connexion', views.authentication, name="authenticate"),
    path('notifications/get/<int:vue_chk>', views.getNotification, name="notifications"),
    path('notifications/valdate/<int:id>', views.ValidateNotif, name="notifications_vldt"),
    path('notifications', views.dashboardNotif, name="notifications_see"),
    path('agent/edit', views.goToEditAgent, name="edit_agent"),
    path('agent/edit/go', views.editAgent, name="edit_agent_go"),

    #filtre
    path('conge/user/<int:id>', views.GetEvenementSingle, name="get_jour_off_single"),
]