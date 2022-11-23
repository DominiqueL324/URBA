function loadEvent(url,service,date_r,date_r1){
    $.ajax({
            type: 'GET',
            url: url,
            data: { "service": service, "date": date_r },
            success: function(response){
                if (response["contenu"] == 0){
                    $("#tmpsService").val(response["duree"])
                    $("#inputDate").prop('readonly',false)
                    $("#inputDate").val(date_r1)
                    configCalHeure(response['start_date'], response['rdv'])
                    $('.fc-timegrid-axis-cushion').css('display','none')
                }
                date_r = date_r.split('/')[1]+'/'+date_r.split('/')[0]+'/'+date_r.split('/')[2]
                InputServiceSelect(date_r)
            },
            error:function(response){ 
                console.log(response) 
            } 

    })
}

function InputServiceSelect(date_r) { 
    service = $('#inputService').val()
    $('#inputHeure').val('')
    respo = ""
    $.ajax({
        type: 'GET',
        url: "/rdv/crenaux/get/",
        data: { "service": service, date: date_r,"respo":respo,"rdv":$('#rdv').val() },
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

function getval(sel) {
    $('#inputHeure').val(sel.value)
    min = $("#tmpsService").val()
    var fn = new Date("November 13, 2021 " + $("#inputHeure").val());
    fn.setMinutes(fn.getMinutes() + parseInt(min))
    $("#inputHeureFin").val(fn.getHours() + ":" + fn.getMinutes())
    $("#inputHeureFin").val(('0' + fn.getHours()).slice(-2) + ":" + ('0' + fn.getMinutes()).slice(-2))
}

function removeFile(id,idr,url){
    $.ajax({
        type: 'GET',
        url: url,
        data: { "id": id,"rdv":idr },
        success: function (response) {
            window.location.replace(""+response['id']);
        },
        error: function(response){
            console.log(response)
        }
    });
}

function configCalHeure(date_s, evt) {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            left: '',
            center: 'title',
            right: ''
        },
        initialDate: date_s,
        initialView: 'timeGridDay',
        events: evt,
        locales: 'fr',
        slotMinTime: "08:00:00",
        slotMaxTime: "18:00:00",
        eventClick: function (arg) {
            if (arg.event.title == " ") {

            } else if (arg.event.title == "Heure spécifique d'ouverture du service") {

            } else {
                alert("Horaire déjà occupée par un RDV allant de \n" + "heure de début : " + ('0'+arg.el.fcSeg.start.getUTCHours()).slice(-2) + " H: " + ('0'+arg.el.fcSeg.start.getMinutes()).slice(-2) + " Min\nheure de fin : " +('0'+arg.el.fcSeg.end.getUTCHours()).slice(-2) + " H:" + ('0'+arg.el.fcSeg.end.getMinutes()).slice(-2) + " Min")
            }
        }
    });
    calendar.addEvent({
        title: ' ',
        daysOfWeek: "['1,2,3,4,5']",
        startRecur: "2021-01-01",
        startTime: "12:00:00",
        endTime: "13:00:00",
        color: '#555',
        textColor: 'white'
    })
    calendar.render();
} 

function getAgent(url,service) {
   /* $('#agentS').empty()
    $.ajax({
        type: 'GET',
        url: url,
        data: { "service": service },
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

var tst = false

function go(url){
    if($("#inputHeure").val() != '' && $("#inputHeureFin").val() != '') {
        tst = $.ajax({
            type: 'GET',
            url: url,
            data: { "date": date_r, service: $("#inputService").val() },
            success: function (response) {
                var stt = new Date("November 13, 2021 " + $("#inputHeure").val());
                var fn = new Date("November 13, 2021 " + $("#inputHeureFin").val());
                pauseD = new Date("November 13, 2021 " + "12:00:00");
                ouverture = new Date("November 13, 2021 " + "08:00:00");
                fermeture = new Date("November 13, 2021 " + "17:00:00");
                pauseF = new Date("November 13, 2021 " + "14:00:00");
                var heureD = stt.getTime()
                var heureF = fn.getTime()
                //controle des heure d'ouverture et de fermeture
                if (heureD < ouverture.getTime() || heureD >= fermeture.getTime() || heureF > fermeture.getTime()) {
                    $("#warning1").css('display', 'inline')
                    return 0;
                }
                //controle de chevauchement pause
                if ((heureD >= pauseD && heureD <= pauseF) || (heureF >= pauseD && heureF <= pauseF)) {
                    $("#warning2").css('display', 'inline')
                    return 0;
                }
                
                    //controle de chevauchement téléphonique
                if ($("#id_phone_0").is(':checked')) {
                        response['rdvF'].forEach(elt => {
                            var deb = new Date("November 13, 2021 " + elt['start']);
                            var fin = new Date("November 13, 2021 " + elt['end']);
                            if ((heureD >= deb.getTime() && heureD <= fin.getTime()) || (heureF >= deb.getTime() && heureF <= fin.getTime())) {
                                    test = true
                                    $("#warning1").css('display', 'none')
                                    $("#warning2").css('display', 'none')
                                    $("#warning3").css('display', 'inline')
                                    return ;
                            }
                        });
                    //controle de chevauchement physique
                } else if ($("#id_phone_1").is(':checked')) {
                        response['rdvP'].forEach(elt => {
                            var deb = new Date("November 13, 2021 " + elt['start']);
                            var fin = new Date("November 13, 2021 " + elt['end']);
                            if ((heureD >= deb.getTime() && heureD <= fin.getTime()) || (heureF >= deb.getTime() && heureF <= fin.getTime())) {
                                    test = true
                                    $("#warning1").css('display', 'none')
                                    $("#warning2").css('display', 'none')
                                    $("#warning3").css('display', 'none')
                                    $("#warning4").css('display', 'inline')
                                    return ;
                                }
                            });
                }
                    
                },
                error: function (response) {
                    console.log(response)
                }
            });
    }else{
    }
    console.log(tst)
    return 0
}