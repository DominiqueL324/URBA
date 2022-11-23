Liste_del = []
//evenement de formulaire de recherche des responsables
function changeInputResponsable(val) {
    if (val == "nom") {
        $('#dataSearchFieldResponsable').empty()
        $('#dataSearchFieldResponsable').append(
            "<input type='text' id='responsableDataSearchField' class='w-100 input is-small' placeholder='Nom Responsable' />"
        )
    } else if (val == 'email') {
        $('#dataSearchFieldResponsable').empty()
        $('#dataSearchFieldResponsable').append(
            "<input type='email' id='responsableDataSearchField' class='w-100 input is-small' placeholder='mail Responsable' />"
        )
    }
    else {
        $('#dataSearchFieldResponsable').empty()
    }
}

//recupération de responsable par recherche
function getResponsableBySearch(url) {
    valeur = $('#responsableDataSearchField').val()
    attribut = $('#filterResponsable').val()
    $.ajax({
        type: 'GET',
        url: url,
        data: { 'valeur': valeur, "attribut": attribut },
        success: function (response) {
            $('#contentTableResponsable').empty()
            response['responsable'].forEach(elt => {
                $('#contentTableResponsable').append(
                    "<tr>\
                    <td>\
                        <label class='checkbox'>\
                            <input type='checkbox' id='addDel"+elt.id+"' onclick='addToDelete("+elt.id+")'>\
                        </label>\
                    </td>\
                    <th>1</th>\
                    <td> "+ elt.username + " </td>\
                    <td> "+ elt.email + " </td>\
                    <td> "+ elt.first_name + " </td>\
                    <td> "+ elt.last_name + " </td>\
                    <td><a href='recuperer/"+ elt.id + "'\class='is-success button is-small'><span><i class='fa fa-eye'></i></span></a>\
                    </td>\
                </tr>"
                )
            });
        },
        error: function (response) {

        }
    })
}

//recherche de rdv par date
function findRdvBydateAdmin(url) {
    debut = $('#debut').val()
    fin = $('#fin').val()
    $.ajax({
        type: 'GET',
        url: url,
        data: { 'debut': debut, "fin": fin },
        success: function (response) {
            $('#contentTableResponsable1').empty()
            response['rdvs'].forEach(elt => {
                $('#contentTableResponsable1').append(
                    "<tr>\
                        <td>"+ elt.client + "</td>\
                        <td> " + elt.email + "</td>\
                        <td> " + elt.service + "</td>\
                        <td>"+ elt.date + "</td>" + '\
                    </tr>'
                )
            });
        },
        error: function (response) {

        }
    })
}

//Exporter Ajax
function ExportAjax(url) {
    debut = $('#debut').val()
    fin = $('#fin').val()
    if (!$('#debut').val() || !$('#fin').val()) {
        alert('Les dates sont Obligatoires')
        return
    }
    $.ajax({
        type: 'GET',
        url: url,
        data: { 'debut': debut, "fin": fin },
        xhrFields: { responseType: 'blob' },
        success: function (response) {
            var a = document.createElement('a');
            var url = window.URL.createObjectURL(response);
            a.href = url;
            a.download = 'RDV_.xls';
            document.body.append(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        },
        error: function (response) {

        }
    })
}

//suppression
function DeleteAdmin(url, option) {
    if (option == "ADJ") {
        $("#deleteAdj").attr("href", url);
    }
}

//change state of rdv
function go(id, url, valeure) {
    if( valeure == "Annulé"){
        valeure = "Annule"
    }
    if( valeure == "Reporté"){
        valeure = "Reporte"
    }
    if( valeure == "Approuvé"){
        valeure = "Approuve" 
    }
    $.ajax({
        type: 'GET',
        url: url,
        data: { 'valeure': valeure, "id": id },
        success: function (response) {
            if (response['bon'] == 1) {
                alert("Etat du rendez-vous modifier avec success")
            } else {
                alert("Echec de la modification")
            }
        },
        error: function (response) {

        }
    })
}

//ajouter un administré new RDV
function addAdministreJs(url) {
    nom = $('#nom').val()
    prenom = $('#prenom').val()
    phone = $('#phone').val()
    mail = $('#mail').val()
    adresse = $('#adresse').val()
    if (nom.length === 0 || prenom.length === 0 || phone.length === 0 || mail.length === 0 || adresse.length === 0 ) {
        $('#alert').css('display', 'inline')
        return
    } else {
        $('#alert').css('display', 'none')
    }
    $('#waiter').css('display','inline')
    $.ajax({
        type: 'POST',
        url: url,
        data: { csrfmiddlewaretoken:$("input[name='csrfmiddlewaretoken']").val(),adresse: $('#adresse').val(), nom: $('#nom').val(), prenom: $('#prenom').val(), phone: $('#phone').val(), mail: $('#mail').val() },
        success: function (response) {
            if (response['erreur'] == 0) {
                $('#waiter').css('display','none')
                $('#modal').removeClass("is-active")
                $("#inputAdministre").prepend(
                    "<option value=" +response['id']+ ">" + response['nom'] + " " + response['prenom'] + "</option>"
                )
            }else{
                alert(response['erreur'])
            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}
//charger la liste de responsable pour prise de RDV (Ajax)
function loadResponsable(id,url){
    $.ajax({
        type: 'GET',
        url: url,
        data: { rdv:id,service:" "},
        success: function (response) {
            if (response['erreur'] == 0) {
                $("#respo").empty()
                response['respo'].forEach(elt=>{
                    $("#respo").append(
                        "<option value="+elt.id+">" + elt.nom + " " + elt.prenom + "</option>"
                    )
                })
            }else{
                alert(response['erreur'])
            }
        },
        error: function (response) { 
            console.log(response)
        }
    })
}

//charge la listed eresponsable du service selectionné lors de l'ajout du service
function serviceChange(url){
    $.ajax({
        type: 'GET',
        url: url,
        data: { service:$("#inputService").val(),rdv:" "},
        success: function (response) {
            if (response['erreur'] == 0) {
                $("#respo").empty()
                response['respo'].forEach(elt=>{
                    $("#respo").append(
                        "<option value="+elt.id+">" + elt.nom + " " + elt.prenom + "</option>"
                    )
                })
            }else{
                alert(response['erreur'])
            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function getAllAgent(url){
    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            if (response['erreur'] == 0) {
                $("#fiterA").empty()
                $("#fiterA").append(
                    "<option value=-1>Tous les agents</option>"
                )
                response['respo'].forEach(elt=>{
                    $("#fiterA").append(
                        "<option value="+elt.id+" style='color:"+elt.couleur+";'>" + elt.nom + " " + elt.prenom + "</option>"
                    )
                })
            }else{
                alert(response['erreur']) 
            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function addToDelete(id){
    var i;
    for (i = 0; i < Liste_del.length; ++i) {
        if(Liste_del[i]==id){
            Liste_del.splice(i,1)
            console.log(Liste_del)
            return
        }
    }
    Liste_del.splice(1,0,id)
    console.log(Liste_del)
}
function goDelete(url,id){
    if(Liste_del.length<=0){
        alert('Sélectionnez au moins un élément à supprimer')
    }else{
        if (confirm('Voulez vous vraiment supprimer ces éléments??')) {
            $("#deleteMessage").css("display","inline")
            ls = JSON.stringify(Liste_del)
            $.ajax({
                type: 'GET',
                url: url,
                dataType: "json",
                data:  {liste:ls,id:id},
                success: function (response) {
                    $("#deleteMessage").css("display","none")
                    Liste_del = []
                    if (id == "RDV"){
                        window.location.replace("/administration/rdv")
                    }else if(id=="ADMNS"){
                        window.location.replace("/administration/administre")
                    }else if(id=="ADMNT"){
                        window.location.replace("/administration/administrateur")
                    }else if(id=="SERVICE"){
                        window.location.replace("/administration/service")
                    }else if(id=="RSP"){
                        window.location.replace("/administration/agent")
                    }else if(id=="ADJ"){
                        window.location.replace("/administration/adjoint")
                    }else{
                        window.location.replace("/administration/dashboard")
                    }
                    
                },
                error: function (response) {
                    console.log(response)
                }
            })
        } 
       

    }
}

$("#telephone1").on('change', function () {
    min = $("#telephone1").val()
    min = min.toString()
    if( (min.length < 10 || min.length >10) || min.charAt(0)!= "0"){
        $("#erreurPhone").css('display','inline')
        $("#go").css('display','none')
        
    }else{
        $("#erreurPhone").css('display','none')
        $("#go").css('display','inline')
    }
})

$("#telephone1").keyup(function () {
    min = $("#telephone1").val()
    min = min.toString()
    if( (min.length < 10 || min.length >10) || min.charAt(0)!= "0"){
        $("#erreurPhone").css('display','inline')
        $("#go").css('display','none')
    }else{
        $("#erreurPhone").css('display','none')
        $("#go").css('display','inline')
    }
})

$("#administreI").on("change", function () {
    id = $("#administreI").val()
    $.ajax({
        type: 'GET',
        url: '/rdv/rdv/adresseT',
        data: { "id": id},
        success: function (response) {
            $('#adresseI').empty()
            if (response['adresses'] != "0") {
                $('#adresseI').append('<option value="*">*****</option>')
                response['adresses'].forEach(elt => {
                    $('#adresseI').append('<option value=' +elt['adresse']+ '> ' + elt['adresse'] + ' </option>')
                })
            }
        },
        error: function (response) {
        }
    })
})

$('#adresseI').on('change',function(){
    //alert($("#adresseI option:selected").text())
    if($("#adresseI").val()!= "*"){
        $("#adresseTravauxInput").val($("#adresseI option:selected").text())
    }else{
        $("#adresseTravauxInput").val('');
    }
})


