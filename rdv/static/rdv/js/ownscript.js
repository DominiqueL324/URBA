/**/

function Ownchecker() {
    document.getElementById('warning').style.display = "none"
    var nom = document.getElementById('inputNom').value
    var prenom = document.getElementById('inputPrenom').value;
    var tel = document.getElementById('telephone').value;
    var email = document.getElementById('inputEmail4').value;
    var adresse = document.getElementById('inputAdresse').value;
    var condition = document.getElementById('flexCheckDefault');
    const rbs_phone = document.querySelectorAll('input[name="phone"]');
    const rbs_urba = document.querySelectorAll('input[name="urbanisme"]');
    var s_phone = false
    var s_urba = false
    for (const rb of rbs_phone) {
        if (rb.checked) {
            s_phone = true
            break;
        }
    }
    for (const rb of rbs_urba) {
        if (rb.checked) {
            s_urba = true
            break;
        }
    }
    $(".monform input[type='text'], .monform input[type='email'], .monform input[type='tel']").each(function () {
        if ($(this).val() === '') {
            $(this).addClass('is-invalid')
        } else {
            $(this).removeClass('is-invalid')
        }
    });

    if (nom && prenom && tel && email && adresse && condition.checked) {
        if (s_phone == true && s_urba == true) {
            document.getElementById('warning').style.display = "none"
            $('#myTab a[href="#responsable"]').tab('show');
        } else {
            document.getElementById('warning').style.display = "inline"
        }
    } else {
        document.getElementById('warning').style.display = "inline"
    }
}
//action quand on clique sur suivant de la tab horraire
/*document.getElementById('next2').onclick = function(e){

    if($("#inputDate").val()!='' || $("#inputHeure").val()!='' || $("#inputNombre").val()!='' ){
        $('#myTab a[href="#personnel"]').tab('show');
        $("#warning1").css('display','none')
    }else{
        $("#warning1").css('display','inline')
        e.stopPropagation()
    }
}*/
function myFunction() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];
        td1 = tr[i].getElementsByTagName("td")[1];
        if (td || td1) {
            txtValue = td.textContent || td.innerText;
            txtValue1 = td1.textContent || td1.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1 || txtValue1.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }

        }
    }
}

function Next2Click(url, e) {
    if (parseInt($("#inputNombre").val()) < 0) {
        $("#dateError").empty()
        $("#dateError").append(
            'Le nombre de personnes est invalide'
        )
        return
    } else {
        $("#dateError").empty() 
    }
    if ($("#inputDate").val() != '' && $("#inputNombre").val() != '') {
        //$('#myTab a[href="#horaires"]').tab('show');
        //configCalHeure($("#inputDate").val()) 
        $("#warning1").css('display', 'none')
    } else {
        $("#warning1").css('display', 'inline')
        e.stopPropagation()
        return
    }
    service = $('#inputService').val()
    date_r = $('#inputDate').val()
    $.ajax({
        type: 'GET',
        url: url,
        data: { "service": service, "date": date_r },
        success: function (response) {
            $("#tmpsService").val(response["duree"])
            if (response["contenu"] == 0) {
                if ($("#inputDate").val() != '' && $("#inputNombre").val() != '') {
                    $('#myTab a[href="#horaires"]').tab('show');
                    //InputServiceSelect("/rdv/crenaux/get/",date_r)
                    configCalHeure(response['start_date'], response['rdv'])
                    $('.fc-timegrid-axis-cushion').css('display','none')
                    $("#warning1").css('display', 'none')
                } else {
                    $("#warning1").css('display', 'inline')
                    e.stopPropagation()
                }
                $("#warning2").css('display', 'none')
                $("#warning3").css('display', 'none')
            } else if (response["contenu"] == 1) {
                $("#warning2").css('display', 'inline')
                e.stopPropagation()
            }
            else if (response["contenu"] == -2) {
                $("#warning3").css('display', 'inline')
                e.stopPropagation()
            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}

//quand on clique sur next de Horaires
function Next3Click(url, e) {
    if (!$("#id_phone_0").is(':checked') && !$("#id_phone_1").is(':checked')) {
        $("#warning7").css('display', 'inline')
        return
    } else {
        $("#warning7").css('display', 'none')
    }
    if ($("#inputHeure").val() != '' && $("#inputHeureFin").val() != '') {
        var test = false
        phone = false
        date_r = $('#inputDate').val().split('/')
        date_r = date_r[2]+"-"+(date_r[1])+"-"+date_r[0]
        $("#warning14").css('display', 'none') 
        date_r = $('#inputDate').val() 
        $.ajax({
            type: 'GET',
            url: url,
            data: { "date": date_r, service: $("#inputService").val() },
            success: function (response) {
                var stt = new Date("November 13, 2021 " + $("#inputHeure").val());
                var fn = new Date("November 13, 2021 " + $("#inputHeureFin").val());
                pauseD = new Date("November 13, 2021 " + "12:01:00");
                ouverture = new Date("November 13, 2021 " + "08:00:00");
                fermeture = new Date("November 13, 2021 " + "17:00:00");
                pauseF = new Date("November 13, 2021 " + "12:59:00");
                var heureD = stt.getTime()
                var heureF = fn.getTime()
                //controle des heure d'ouverture et de fermeture
                if (heureD < ouverture.getTime() || heureD >= fermeture.getTime() || heureF > fermeture.getTime()) {
                    $("#warning10").css('display', 'inline')
                    return
                }
                //controle de chevauchement pause
                if ((heureD >= pauseD && heureD <= pauseF) || (heureF >= pauseD && heureF <= pauseF)) {
                    $("#warning5").css('display', 'inline')
                    return
                }
                //if (response['reccurence'] == 0 && response['lineaire'] == 0) {
                    //controle de chevauchement téléphonique
                    console.log(response['rdvF'])
                    console.log(response['rdvP'])
                    if ($("#id_phone_0").is(':checked')) {
                        response['rdvF'].forEach(elt => {
                            var deb = new Date("November 13, 2021 " + elt['start']);
                            var fin = new Date("November 13, 2021 " + elt['end']);
                            fn.setMinutes(fn.getMinutes()-2)
                            heureF = fn.getTime()
                            fin.setMinutes(fin.getMinutes()-2)
                            if ((heureD >= deb.getTime() && heureD <= fin.getTime()) || (heureF >= deb.getTime() && heureF <= fin.getTime())) {
                                test = true
                                $("#warning5").css('display', 'none')
                                $("#warning6").css('display', 'none')
                                $("#warning8").css('display', 'none')
                                $("#warning9").css('display', 'inline')
                                return
                            }
                        });
                    //controle de chevauchement physique
                    } else if ($("#id_phone_1").is(':checked')) {
                        response['rdvP'].forEach(elt => {
                            var deb = new Date("November 13, 2021 " + elt['start']);
                            var fin = new Date("November 13, 2021 " + elt['end']);
                            fn.setMinutes(fn.getMinutes()-2)
                            heureF = fn.getTime()
                            fin.setMinutes(fin.getMinutes()-2)
                            if ((heureD >= deb.getTime() && heureD <= fin.getTime()) || (heureF >= deb.getTime() && heureF <= fin.getTime())) {
                                console.log(deb)
                                test = true
                                $("#warning9").css('display', 'none')
                                $("#warning5").css('display', 'none')
                                $("#warning8").css('display', 'none')
                                $("#warning6").css('display', 'inline')
                                return
                            }
                        });
                    }
                console.log(test)
                if (test == false) {
                    $('#myTab a[href="#personnel"]').tab('show');
                    $("#warning9").css('display', 'none')
                    $("#warning5").css('display', 'none')
                    $("#warning6").css('display', 'none')
                    $("#warning8").css('display', 'none')
                } else {
                    return
                }
            },
            error: function (response) {
                console.log(response)
            }
        });
    } else {
        $("#warning8").css('display', 'inline')
        return
    }
}

function configCalendar(url) {
    $('#evoCalendar').evoCalendar({
        firstDayOfWeek: 1,// Monday
        sidebarToggler: true,
        sidebarDisplayDefault: false,
        eventListToggler: false,
        eventDisplayDefault: false,
        todayHighlight: true,
        format: 'mm/dd/yyyy',
        titleFormat: 'dd MM, yyyy',
        eventHeaderFormat: 'd MM, yyyy',
        language: 'fr',
        //disabledDate: ["August/16/2021","August/18/2021"],
    }).on('selectDate', function (newDate, oldDate) {
        dt = oldDate.split("/")
        month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        mois = month[(parseInt(dt['0']) - 1)]
        selected_date = new Date(mois + "/" + dt[1] + "/" + dt[2])
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
            if (oday > selected_date) {
                diff_temps = oday.getTime() - selected_date.getTime()
            } else {
                diff_temps = selected_date.getTime() - oday.getTime()
            }
            diff_jour = Math.round(diff_temps / (1000 * 3600 * 24));

            if (diff_jour < 6) {
                document.getElementById("inputDate").setAttribute('value', '')
                oday.setDate(oday.getDate() + 7)
                $("#dateError").empty()
                $("#dateError").append(
                    'Vous ne pouvez pas prendre de RDV avant le ' + oday.getDate() + "/" + (oday.getMonth() + 1) + "/" + oday.getFullYear()
                )
            } else {
                $("#dateError").empty()
                document.getElementById("inputDate").setAttribute('value', dt[1]+"/"+dt[0]+"/"+dt[2])
                InputServiceSelect(url, oldDate)
            }
        }
 
    });
}

function loadBusyDay(){
    date = new Date()
    date.setDate(date.getDate() + 7)
    dateF = new Date(date.getFullYear().toString(),11,1)
    console.log(date)
    console.log(dateF)
    console.log(date.getFullYear().toString()+"-"+("0"+(date.getMonth()+1)).slice(-2)+"-"+("0"+date.getDate()).slice(-2) , dateF.getFullYear().toString()+"-"+("0"+(dateF.getMonth()+1)).slice(-2)+"-"+("0"+dateF.getDay()).slice(-2))
    //console.log('"'+'January/'+debut.getDate().toString()+'/'+debut.getFullYear().toString()+'"', 'August/'+date.getDate().toString()+'/'+date.getFullYear().toString())
    //while(dateF.getMonth()<=11 && dateF.getDate()<=31){}
    $("#evoCalendar").evoCalendar('addCalendarEvent', [
        {
            'id': "event" + 12,
            'name': 'item.name',
            'date': [ date.getFullYear().toString()+"-"+("0"+(date.getMonth()+1)).slice(-2)+"-"+("0"+date.getDate()).slice(-2) , dateF.getFullYear().toString()+"-"+("0"+(dateF.getMonth()+1)).slice(-2)+"-"+("0"+dateF.getDate()).slice(-2) ],
            'type': 'item.type_e',
            'color': 'green',
            'everyYear': false,
            'description': ""

        }
    ]);
}

function getval(sel) {
    $('#inputHeure').val(sel.value)
    min = $("#tmpsService").val()
    var fn = new Date("November 13, 2021 " + $("#inputHeure").val());
    fn.setMinutes(fn.getMinutes() + parseInt(min))
    $("#inputHeureFin").val(fn.getHours() + ":" + fn.getMinutes())
    $("#inputHeureFin").val(('0' + fn.getHours()).slice(-2) + ":" + ('0' + fn.getMinutes()).slice(-2))
    date_r = $('#inputDate').val()
    $.ajax({
        type: 'GET',
        url: "rdv/rdv/creneau_libre",
        data: { "service": service, "date": date_r,"fin":$("#inputHeureFin").val(),"debut":$("#inputHeure").val() },
        success: function (response) {
           if(response['reponse'] == "ok"){
                $('#next3').css('display','inline')
                $('#warning17').css('display','none')
           }else if((response['reponse'] == "bad")){
                $('#next3').css('display','none')
                $('#warning17').css('display','inline')
           }else{

           }
        },
        error: function (response) {
            console.log(response)
        }
    })
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
            //console.log(arg.el.fcSeg.start.getHours()+":"+arg.el.fcSeg.start.getMinutes()+"___"+arg.el.fcSeg.end.getHours()+":"+arg.el.fcSeg.end.getMinutes())
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

$("#inputEmail4").on("keyup", function () {
    val = $("#inputEmail4").val()
    $.ajax({
        type: 'GET',
        url: '/rdv/rdv/adresseT',
        data: { "administre": val },
        success: function (response) {
            $('#adresseT').empty()
            if (response['adresses'] != "0") {
                $('#adresseT').append('<option value="*">*****</option>')
                response['adresses'].forEach(elt => {
                    $('#adresseT').append('<option value=' + elt['adresse'] + '> ' + elt['adresse'] + ' </option>')
                })
            }
        },
        error: function (response) {
        }
    })
})
$('#adresseT').on('change',function(){
    if($("#adresseT").val()!= "*"){
        $("#inputAdresseTravaux").val($("#adresseT").val())
    }else{
        $("#inputAdresseTravaux").val('');
    }
})

 







