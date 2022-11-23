var cas = ""
function full(cible){
    if(cible == "rdv_add"){
        cas = "ajout_rdv"
        $("#divRdv").css('display','inline')
        $("#divAgent").css('display','inline')
        $("#divService").css('display','inline')
        $("#divAdministre").css('display','inline')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        setActive("nrdv")
    }else if(cible=="rdv_accept"){
        $("#divRdv").css('display','inline')
        $("#divAgent").css('display','inline')
        $("#divService").css('display','inline')
        $("#divAdministre").css('display','inline')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "rdv_valide"
        setActive("ardv")
    }else if(cible=='rdv_waiting'){
        $("#divRdv").css('display','inline')
        $("#divAgent").css('display','inline')
        $("#divService").css('display','inline')
        $("#divAdministre").css('display','inline')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "rdv_en_attente"
        setActive("eardv")
    }else if(cible=='rdv_abort'){
        $("#divRdv").css('display','inline')
        $("#divAgent").css('display','inline')
        $("#divService").css('display','inline')
        $("#divAdministre").css('display','inline')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "rdv_annule"
        setActive("anrdv")
    }else if(cible=='administre_add'){
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','none')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','inline')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "ajout_administre"
        setActive("nadm")
    }else if(cible=='administre_edit'){
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','none')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','inline')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "modification_administre"
        setActive("edam")
    }else if(cible=='agent_add'){
        setActive("aag")
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','inline')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','none')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "ajout_agent"
    }else if(cible=='agent_edit'){
        $('.ql-editor').html("")
        $('.ql-editor').html(
            "<p>Chers <strong>%agent_nom% %agent_prenom%</strong> </p><p>votre compte a été modifié dans l'application URBA votre login est <strong>%agent_login%</strong> et votre mot de passe <strong>%agent_mot_de_passe%</strong></p><p>connectez-vous pour modifier ces informations</p>"
        )
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','inline')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','none')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "modification_agent"
        setActive("eag")
    }else if(cible=='sup_add'){
        setActive("asup")
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','none')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','none')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','inline')
        $("#divAdministrateur").css('display','none')
        cas = "ajout_superviseur"
    }else if(cible=='sup_edit'){
        setActive("esup")
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','none')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','none')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','inline')
        $("#divAdministrateur").css('display','none')
        cas = "modification_superviseur"
    }else if(cible=='adj_add'){
        setActive("aadd")
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','none')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','none')
        $("#divAdjoint").css('display','inline')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "ajout_adjoint"
    }else if(cible=='adj_edit'){
        setActive("eadd")
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','none')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','none')
        $("#divAdjoint").css('display','inline')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','none')
        cas = "modification_adjoint"
    }else if(cible=='admin_add'){
        setActive("aadmin")
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','none')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','none')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','inline')
        cas = "ajout_administrateur"
    }else if(cible=='admin_edit'){
        setActive("eadmin")
        $("#divRdv").css('display','none')
        $("#divAgent").css('display','none')
        $("#divService").css('display','none')
        $("#divAdministre").css('display','none')
        $("#divAdjoint").css('display','none')
        $("#divSuperviseur").css('display','none')
        $("#divAdministrateur").css('display','inline')
        cas = "modification_administrateur"
    }else{

    }
    $.ajax({
        type: "GET",
        url: "/administration/notifications/get/cas",
        data: {cas:cas},
        success: function(response){
            if(response['notification']!=0){
                $('.ql-editor').html("")
                $('#subject').val("")
                response['notification'].forEach(element => {
                    $('.ql-editor').html(element.body)
                    $('#subject').val(element.sujet)
                });
            }else{
                $('#subject').val("")
                $('.ql-editor').html(
                    "<strong> Aucune notification pour le cas "+cas+"</strong>"
                )
            }
        },
        error: function(response){
            alert("Erreur de récupération veuillez reéssayer plus tard")
        }
    })
}

function copySelectedValue(id){
    txt = $('#'+id).val()
    copyText(txt);
    $('#'+id).val("")
    $('#copy').css('display','inline')
    setTimeout(function(){
        $('#copy').css('display','none')
    },1000);
}

function copyText(text) {
    navigator.clipboard.writeText(text);
}

function goSave(url){
    $("#warning1").css('display','none')
    if($('#subject').val().length <= 0 || $('.ql-editor').html().length<=0){
        $("#warning1").css('display','inline')
        return
    }
    //alert($('.ql-editor').val()) 
    $.ajax({
        type: "POST",
        url: url,
        data:{csrfmiddlewaretoken:$("input[name='csrfmiddlewaretoken']").val(),sujet:$('#subject').val(),body:$('.ql-editor').html(),cas:cas},
        success: function(response){
            cas = ""
            window.location.replace("/administration/dashboard/")
        },
        error: function(response){
            alert("Erreur d'ajout veuillez reéssayer plus tard")
        }
    })
}

function setActive(active_own){
    liste = ["ardv","nrdv","eardv","anrdv","nadm","edam","aag","eag","asup","esup","aadd","eadd","aadmin","eadmin"]
    liste.forEach(elt => {
        if(elt == active_own){
            $('#'+active_own).addClass('active');
        }else{
            $('#'+elt).removeClass('active');
        }
    })
}