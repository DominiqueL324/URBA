from django.urls import path
from . import views

app_name="administration"

urlpatterns = [
    path('connexion/', views.LoginPage, name="login"),
    path('deconnexion/', views.logoutUser, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('connexion/go', views.authentication, name="login_go"),
    
    path('rdv/', views.dashboardRDV, name="rdv_dashboard"),
    path('rdv/ajouter/', views.goToAddRdv ,name='rdv_add'),
    path('rdv/ajouter/go', views.addRdv ,name='rdv_add_go'),
    path('rdv/recuperer/<int:id>', views.getRdvToEdit, name="rdv_get_edit"),
    path('rdv/modifier/<int:id>',views.editRdv,name="rdv_edit"),
    path('rdv/supprimer/<int:id>',views.deleteRdv,name="rdv_delete"),
    path('rdv/update',views.updateRdv,name="rdv_update"),
    path('rdv/supprimer/many',views.deleteManyRdv,name="delete_many_rdv"),
    
    path('conges/', views.dashboardConges ,name='conges'), 
    path('conge/ajouter', views.goToAddConge ,name='conges_add'),
    path('conge/ajouter/go', views.addConges ,name='conges_add_go'),
    path('conge/recuperer/<int:id>', views.getCongeToEdit ,name='conges_edit'),
    path('conge/modifier/<int:id>', views.editConge ,name='conges_edit_go'),
    path('conge/supprimer/<int:id>', views.deleteConge ,name='conges_delete'),

    path('administre/', views.dashboardAdministre, name="administre_dashboard"),
    path('administre/ajouter/', views.goToAddAministre ,name='administre_add'),
    path('administre/ajouter/ajax', views.addAdministreAjax ,name='administre_add_ajax'),
    path('administre/ajouter/go', views.addAdministre ,name='administre_add_go'),
    path('administre/recuperer/<int:id>', views.getAdministreToEdit, name="administre_get_edit"),
    path('administre/modifier/<int:id>',views.editAdministre,name="administre_edit"),
    path('administre/supprimer/<int:id>',views.deleteAdministre,name="administre_delete"),

    path('adjoint/', views.dashboardAdSu, name="adjoint_dashboard"),
    path('adjoint/ajouter/', views.goToAddAdjoint ,name='adjoint_add'),
    path('adjoint/ajouter/go', views.addAdjointSu ,name='adjoint_add_go'),
    path('adjoint/recuperer/<int:id>', views.getAdjointToEdit, name="adjoint_get_edit"),
    path('adjoint/modifier/<int:id>',views.editAdjointSup,name="adjoint_edit"),
    path('adjoint/supprimer/<int:id>',views.deleteAdjoint,name= "adjoint_delete"),

    path('service/', views.dashboardService, name="service_dashboard"),
    path('service/delete/responsable/<int:id>', views.deleteResponsableService, name="service_delete_responsable"),
    path('service/ajouter/', views.goToAddService ,name='service_add_go'),
    path('service/ajouter/go', views.addService ,name='service_add'),
    path('service/recuperer/<int:id>', views.getServiceToEdit, name="service_get_edit"),
    path('service/modifier/<int:id>',views.editService,name="service_edit"),
    path('service/supprimer/<int:id>',views.deleteService,name="service_delete"), 

    path('agent/', views.dashboardResponsable, name="responsable_dashboard"),
    path('agent/ajouter/', views.goToAddResponsable ,name='responsable_add'),
    path('agent/ajouter/go', views.addResponsable ,name='responsable_add_go'),
    path('agent/recuperer/<int:id>', views.getResponsableToEdit, name="responsable_get_edit"),
    path('agent/modifier/<int:id>',views.editResponsable,name="responsable_edit"),
    path('agent/supprimer/<int:id>',views.deleteResponsable,name="responsable_delete"),
    path('agent/ajax/search',views.getResponsableBynameOrEmail,name="get_responsable_ajax"),
    path('agent/ajax/get',views.getRespoofServiceForEditRdv,name="get_responsable_ajax_to_edit"),

    path('rdv/ajax/get/<int:en_attente>',views.getRdvAjax,name="get_rdv_ajax"),
    path('rdv/ajax/get/search/',views.getRdvForSearchField,name="get_rdv_ajax_form"),
    path('rdv/ajax/get/search/date',views.getRdvBetweenDate,name="get_rdv_ajax_form_date"),
    path('rdv/ajax/evt/',views.getRdvByAjax,name="get_rdv_evt"),
    path('administre/ajax/get/search',views.getAdministreBynameOrEmail,name="get_administre_ajax"),
    
    path('rdv/export/excel/go',views.exportExcel,name="get_in_excel_go"),
    path('rdv/export/excel',views.gotToExportExcel,name="get_in_excel"),
    path('rdv/import/excel',views.importFromExcelFiles,name="bring_in_excel"),
    path('rdv/upload/excel',views.uploadEmptyMode,name="upload_model"),

    #jours spécifiques

    path('jours_specifiques/',views.dashboardJS,name="joursSpecifiques_dashboard"),
    path('jours_specifiques/nouveau',views.goToAddJS,name="joursSpecifiques_add_go"),
    path('jours_specifiques/nouveau/add',views.addJoursSpecifique,name="joursSpecifiques_add"),
    path('jours_specifiques/get/onload',views.getSpecificsDays,name="joursSpecifiques_get_onload"),
    path('jours_specifiques/nouveau/recurrence/add',views.addJoursSpecifiqueRecurence,name="joursSpecifiques_recurrence_add"),
    path('jours_specifiques/delete',views.deleteJS,name="joursSpecifiques_delete"),

    #administrateur

    path('administrateur/',views.dashboardAdmin,name="administrateur_dashboard"),
    path('administrateur/nouveau',views.goToAddAdmin,name="administrateur_add_go"),
    path('administrateur/nouveau/add',views.addAdmin,name="administrateur_add"),
    path('administrateur/recuperer/<int:id>',views.getAdminToEdit,name="administrateur_get_edit"),
    path('administrateur/edit/<int:id>',views.editAdmin,name="administrateur_edit"),
    path('administrateur/delete/<int:id>',views.deleteAdmin,name="administrateur_delete"),

    #recuparation login pass

    path('recuperation/',views.getAcces,name="recuperation"),
    path('recuperation/check',views.checkEmailAndPhon,name="recuperation_check"),
    path('recuperation/edit/<int:id>',views.editPass,name="recuperation_edit"),

    #admi/Adjoint/Sup dashboard
    path('recuperation/dashboard/admin',views.getRDvForAdjSup,name="rdv_dashboard_admin"),
    #Agenda
    path('agenda/',views.dashBoardAgenda,name="agenda"),
    path('administre/ajax/all',views.getAllAdministre,name="administre_all"),
    path('agenda/rdv/add',views.addRdvAjax,name="agenda_rdv_add"),
    path('jours_specifiques/get_hours/agenda',views.getJsHoursForAgenda,name="joursSpecifiques_hours_agenda"),



    #notifications
    path('notifications/',views.dashBoardNotification,name="notifications"),
    path('notifications/add',views.addNotificationMails,name="notifications_add"),
    path('notifications/get/cas',views.getLastNotification,name="notifications_get_cas"),

    #sauvegarde et restauration
    path('sauvegarde_restauration/',views.dashboardBackup,name="backup"),
    path('sauvegarde_restauration/save',views.saveDb,name="backup_save"),
    path('sauvegarde_restauration/restor',views.restorDb,name="backup_restor"),
]