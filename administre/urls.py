from django.urls import path
from . import views

app_name="administre"

urlpatterns = [
    path('', views.loginPage, name="login"),
    path('connexion', views.connectAdministre, name="login_go"),
    path('edit/profile/', views.getEditProfilForm, name="edit"),
    path('dashboard/', views.Dashboard, name="dashboard"),
    path('edit/profile/go/<int:id>', views.editProfile, name="edit_go"),
    path('edit/rdv/go/<int:id>', views.editRdv, name="edit_rdv_go"),
    path('edit/rdv/<int:id>', views.getRdvToEdit, name="edit_rdv"),
    path('details/rdv/<int:id>', views.getRdvToShow, name="show_rdv"),
    path('file/delete/', views.deleteFile, name="delete_file"),
    path('recover/step1', views.recoverStep1, name="recover_step1"),
    path('recover/check/step1', views.recoverCheckAccess, name="recover_check"),
    path('recover/step2', views.recoverFinalStep, name="recover_final"),
    path('logout', views.logout, name="logout"),
]