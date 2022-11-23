dte=""
 $('#formFileMultiple').on('change',function(){
        OnFileValidation()
})
function OnFileValidation() {
    var image = document.getElementById("formFileMultiple");
    if (typeof (image.files) != "undefined") {
        var size = parseFloat(image.files[0].size / (1024 * 1024)).toFixed(2); 
        if(size > 2) {
            alert('Sélectionnez un fichier de moins de 2 MB');
            $("#reserver").css('display','none')
        }else{
            $("#reserver").css('display','inline')
                    }
        } else {
            alert("Ce navigateur ne supporte pas HTML5.");
        }
}

$("#inputService").on('change', function (e) {
    $('#urba').css('display', 'inline')
    $('#agentS').empty()
    $('#agentS').val(" ")
    $('#agentL').css('display', 'none')
    $('#id_urbanisme_1').prop('checked', false);
    $('#id_urbanisme_0').prop('checked', false);
})

function getAgent(url) {
    //$('#agentS').empty()
    /*$.ajax({
        type: 'GET',
        url: url,
        data: { "service": $("#inputService").val() },
        success: function (response) {
            $('#agentL').css('display', 'inline')
            response['agent'].forEach(element => {
                $('#agentS').append("<option value=" + element['id'] + ">" + element['nom'] + " " + element['prenom'] + "</option>")
            });
        },
        error: function (response) {
            console.log(response)
        }
    })*/
}

$('#id_urbanisme_1').on('click', function (e) {
    $('#agentS').empty()
    $('#agentS').val(" ")
    $('#agentL').css('display', 'none')
})

//saisie sur le champs heure de debut
$("#inputHeure").on('change', function () {
    min = $("#tmpsService").val()
    var fn = new Date("November 13, 2021 " + $("#inputHeure").val());
    fn.setMinutes(fn.getMinutes() + parseInt(min))
    $("#inputHeureFin").val(fn.getHours() + ":" + fn.getMinutes())
    $("#inputHeureFin").val(('0' + fn.getHours()).slice(-2) + ":" + ('0' + fn.getMinutes()).slice(-2))
})

$("#inputHeure").keypress(function () {
    min = $("#tmpsService").val()
    temps = $("#inputHeure").val()
    var fn = new Date("November 13, 2021 " + temps);
    fn.setMinutes(fn.getMinutes() + parseInt(min))
    $("#inputHeureFin").val(('0' + fn.getHours()).slice(-2) + ":" + ('0' + fn.getMinutes()).slice(-2))
})

//action quand on clique sur le lien de info perso
$('#myTab a[href="#personnel"]').on('click', function (e) {

if($("#id_phone_0").is(':checked') || $("#id_phone_1").is(':checked')){
   if ($("#inputHeure").val() != '' && $("#inputHeureFin").val() != '') {
        $('#myTab a[href="#personnel"]').tab('show');
        $("#warning13").css('display', 'none')
    } else {
        $("#warning13").css('display', 'inline')
        e.stopPropagation()
    } 
}else{
    $("#warning13").css('display', 'inline')
    e.stopPropagation() 
}
    
})

//action quand on clique sur le lien de horraire
$('#myTab a[href="#rdv"]').on('click', function (e) {

    if ($("#id_urbanisme_1").is(':checked') || $("#id_urbanisme_0").is(':checked')) {
        if ($("#inputService").val() != '') {
            $('#myTab a[href="#rdv"]').tab('show');
            $("#warning").css('display', 'none')
        } else {
            $("#warning").css('display', 'inline')
            e.stopPropagation()
        }
    }else{
        $("#warning").css('display', 'inline') 
        e.stopPropagation()
    }
})

//action quand on clique sur le lien de horaire
$('#myTab a[href="#horaires"]').on('click', function (e) {
    if ($("#inputDate").val() != '' && $("#inputNombre").val() != '') {
        $('#myTab a[href="#horaires"]').tab('show');
        $("#warning1").css('display', 'none')
    } else {
        $("#warning1").css('display', 'inline')
        e.stopPropagation()
    }
})

function makeid(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}

function InputServiceSelect(date_r) {
    service = $('#inputService').val()
    $('#inputHeure').val('')
    respo = ""
    $.ajax({
        type: 'GET',
        url: "rdv/crenaux/get/",
        data: { "service": service, date: date_r,"respo":respo },
        success: function (response) {
            if (response['bad'] == false) {
                content = "<option selected>............</option>"
                response['reste'].forEach(elt => {
                        content = content + "<option value = " + elt['debut'] + ">" + elt['debut'] + " - " + elt['fin'] + "</option>"
                });
                $('#creneau').empty()
                $('#creneau').append(
                    " <label for='creneauChoice'>Horaire</label>\
                    <select class='form-select form-control form-select-lg' id='creneauChoice' onchange='getval(this);'> "+ content + "</select>"
                )

            } else {

            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function configCalHeure1(evt) {
    var calendarEl = document.getElementById('calendar1');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            left: 'prev,next',
            center: 'title',
            right: 'prev,next'
        },
        initialView: 'dayGridMonth',
        events: evt,
        locales: 'fr',
        hiddenDays: [ 0, 6 ],
        eventClick: function(arg){
            loadDate(arg.event._instance.range.start.getFullYear()+"-"+('0'+(arg.event._instance.range.start.getMonth()+1)).slice(-2)+"-"+('0'+arg.event._instance.range.start.getDate()).slice(-2))
        },
        dateClick: function(info) {
            loadDate(info.dateStr)
        }
    });
    calendar.render();
} 

//action quand on clique sur suivant de la tab responsable
document.getElementById('next1').onclick = function (e) {
    if ($("#id_urbanisme_1").is(':checked') || $("#id_urbanisme_0").is(':checked')) {
        if ($("#inputService").val() != '') {
            $('#myTab a[href="#rdv"]').tab('show');
            $("#warning").css('display', 'none')
            service = $('#inputService').val()
            agent = $('#agentS').val()
            evts = []
            $.ajax({
                type: 'GET',
                url: "/rdv/rdv/jours_libre",
                data: { "service": service, "agent": agent },
                success: function (response) {
                    dt = ""
                    evts=[]
                    response['date'].forEach(elt=>{
                        evts.push({
                            title: '',
                            start: elt,
                            end: elt,
                            color: 'limegreen',
                            textColor: 'white'
                        })
                        dte=elt
                    })
                    configCalHeure1(evts)
                },
                error: function (response) {
                    console.log(response)
                }
            })
        } else {
            $("#warning").css('display', 'inline')
            e.stopPropagation()
        }
    }else{
        $("#warning").css('display', 'inline') 
        e.stopPropagation()
    }
}
//action quand on clique sur précedent de la tab horraire
document.getElementById('prev1').onclick = function () {
    $('#myTab a[href="#responsable"]').tab('show');
}

//action quand on clique sur précédent de la tab info perso
document.getElementById('prev2').onclick = function () {
    $('#myTab a[href="#horaires"]').tab('show');
}

//action quand on clique sur précédent de la tab horaires perso
document.getElementById('prev3').onclick = function () {
    $('#myTab a[href="#rdv"]').tab('show');
}

$("#telephone1").on('change', function () {
    min = $("#telephone1").val()
    min = min.toString()
    if( (min.length < 10 || min.length >10) || min.charAt(0)!= "0"){
        $("#erreurPhone").css('display','inline')
        $("#reserver").css('display','none')
        
    }else{
        $("#erreurPhone").css('display','none')
        $("#reserver").css('display','inline')
    }
})

$("#telephone1").keyup(function () {
    min = $("#telephone1").val()
    min = min.toString()
    if( (min.length < 10 || min.length >10) || min.charAt(0)!= "0"){
        $("#erreurPhone").css('display','inline')
        $("#reserver").css('display','none')
    }else{
        $("#erreurPhone").css('display','none')
        $("#reserver").css('display','inline')
    }
})

function loadDate(dt){
    
    dt = dt.split("-")
    console.log(dt)
    last_date = new Date(dt[0],dt[1],dt[2])
    month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    mois = month[(parseInt(dt['1']) - 1)]
    selected_date = new Date(mois + "/" + dt[2] + "/" + dt[0])
    console.log(selected_date)
    console.log(last_date)
    if(selected_date > last_date){
        $("#dateError").empty()
        $("#dateError").append(
            'Vous ne pouvez pas prendre de RDV après le ' + ("0"+last_date.getDate()).slice(-2) + "/" + ("0"+(last_date.getMonth()+1)).slice(-2)  + "/" + last_date.getFullYear()
            )
        return
    }
    if (selected_date.getDay() == 0 | selected_date.getDay() == 6) {
        document.getElementById("inputDate").setAttribute('value', '')
        $("#warning4").css('display', 'inline')
    } else {
        $("#warning4").css('display', 'none')
        $("#warning3").css('display', 'none')
        $("#warning2").css('display', 'none')
        $("#warning1").css('display', 'none')
        oday = new Date()
        if (oday <= selected_date) {
            $("#dateError").empty()
        } else {
            $("#dateError").empty()
            $("#dateError").append(
                'Vous ne pouvez pas prendre de RDV à cette date'
            )
            return
        }
        console.log(oday)
        if (oday > selected_date) {
            diff_temps = oday.getTime() - selected_date.getTime()
        } else {
            diff_temps = selected_date.getTime() - oday.getTime()
        }
        diff_jour = Math.round(diff_temps / (1000 * 3600 * 24));

        if (diff_jour <= 6) {
            console.log(oday)
            document.getElementById("inputDate").setAttribute('value', '')
            oday.setDate(oday.getDate() + 7)
            $("#dateError").empty()
            $("#dateError").append( 
                'Vous ne pouvez pas prendre de RDV avant le ' + ("0"+oday.getDate()).slice(-2) + "/" + ("0"+(oday.getMonth()+1)).slice(-2) + "/" + oday.getFullYear()
            )
        } else {
            $("#dateError").empty()
            document.getElementById("inputDate").setAttribute('value', dt[2]+"/"+dt[1]+"/"+dt[0])
            InputServiceSelect(dt[1]+"/"+dt[2]+"/"+dt[0])
        }
    }

}



