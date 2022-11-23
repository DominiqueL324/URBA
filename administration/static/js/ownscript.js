//méthodes du calendrier

function clickAll(url, option) {
    
    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) { 
            Liste_del = []
            $('#contentTable').empty()
            $('#contentTable1').empty()
            $('#title1').empty()
            if (option == 1) {
                $('#title1').append("<h3>Rendez-vous En attentes</h3>")
            } else if (option == 2) {
                $('#title1').append("<h3>Rendez-vous Reportés</h3>")
            } else if (option == 4) {
                $('#title1').append("<h3>Tous les Rendez-vous</h3>")
            } else if (option == 0) {
                $('#title1').append("<h3>Rendez-vous Validés</h3>")
            } else {
                $('#title1').append("<h3>Rendez-vous Annulés</h3>")
            }
            response['rdvs'].forEach(elt => {
                vars = ""
                if (elt.etat == 'Approuve'){
                    vars = vars+'<option value="Approuvé" selected> Approuvé</option>'
                }else{
                    vars = vars + '<option value="Approuvé"> Approuvé</option>'
                }
                if(elt.etat == 'En attente'){
                    vars = vars+' <option value="En attente" selected> En attente</option>'
                }else{
                    vars = vars+'<option value="En attente"> En attente</option>'
                }
                if(elt.etat == 'Annule'){
                    vars = vars + ' <option value="Annulé" selected> Annulé</option>'
                }else{
                    vars = vars + '<option value="Annulé"> Annulé</option>'
                }
                $('#contentTable').append(
                    "<tr>\
                        <td>\
                                <label class='checkbox'>\
                                    <input type='checkbox' id='addDel"+elt.id+"' onclick='addToDelete("+elt.id+")'>\
                                </label>\
                        </td>\
                        <td>"+ elt.client + " <br> <strong>" + elt.service + "</strong></td>\
                        <td>"+ elt.date + "</td>" +
                        '<td>\
                            <div class="select is-rounded is-small">\
                                <select id="Etat'+elt.id+'" onchange="go1('+elt.id+')">'+
                                    vars+
                                '</select>\
                            </div>\
                        </td>\
                    <td> <a href="/administration/rdv/recuperer/' + elt.id + '" class="is-success button is-small" ><span><i class="fa fa-eye"></i></span></a> </td>\
                    </tr>'
                )
                $('#contentTable1').append( 
                    "<tr>\
                        <td>\
                                <label class='checkbox'>\
                                    <input type='checkbox' id='addDel"+elt.id+"' onclick='addToDelete("+elt.id+")'>\
                                </label>\
                        </td>\
                        <td>"+ elt.client + "</td>\
                        <td><strong>" + elt.service + "</strong></td>\
                        <td>"+ elt.date + "</td>" + 
                        '<td>\
                            <div class="select is-rounded is-small">\
                                <select id="Etat'+elt.id+'" onchange="go1('+elt.id+')">'+
                                    vars+
                                '</select>\
                            </div>\
                        </td>\
                        <td> <a href="/administration/rdv/recuperer/' + elt.id + '"  class="is-success button is-small" ><span><i class="fa fa-eye"></i></span></a> </td>\
                    </tr>'
                )
            });
        },
        error: function (response) {

        }
    })
}

function disponibiliteCalendar(url, option) {
    $('#evoCalendar').evoCalendar({
        firstDayOfWeek: 1,// Monday
        sidebarToggler: true,
        sidebarDisplayDefault: false,
        eventListToggler: true,
        eventDisplayDefault: false,
        todayHighlight: true,
        format: 'mm/dd/yyyy',
        titleFormat: 'MM yyyy',
        eventHeaderFormat: 'd MM, yyyy',
        language: 'fr',
        //theme: 'Midnight Blue',
    }).on('selectDate', function (newDate, oldDate) {

    });
    if (option == "RDV") {
        getRdv(url)
    } else {
        getEvent(url)
    }
}

function getRdv(url) {
    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            response["evt"].forEach(function (item) {
                $("#evoCalendar").evoCalendar('addCalendarEvent', item);
            })
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function getEvent(url) {
    $.ajax({
        type: 'GET',
        url: url,
        success: function (response) {
            //console.log(response["evt"])
            response["evt"].forEach(function (item) {
                console.log(item)
                $("#evoCalendar").evoCalendar('addCalendarEvent', [
                    {
                        'id': "event" + item.id,
                        'name': item.name,
                        'date': [item.date_d, item.date_f],
                        'type': item.type_e,
                        'color': item.color,
                        'everyYear': false,
                        'description': item.descriptions + "<a href='/administration/conge/recuperer/" + item.id + "' class=' is-success button is-small' ><span><i class='fa fa-eye'></i></span></a>\
                        <a id='delete1' href='/administration/conge/supprimer/"+item.id +"' class=' is-danger button is-small'><span><i class='fas fa-trash'></i></span></a>"

                    }
                ]);
            })
        },
        error: function (response) {
            console.log(response)
        }
    })
}

//mise à jour de l'état d'un RDV
function go1(id) {
    valeure = $('#Etat'+id).val()
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
        url: '/administration/rdv/update',
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

//recupération des jours spécifique au chargement de la page
function getJSonLoad(url,man=0) {
    evt = []
    $.ajax({
        type: 'GET',
        url: url,
        data:{man:man},
        success: function (response) {
            response['js'].forEach(elt => {
                if(elt.clef != "recurrence"){
                    e = {
                    'id': elt.id,
                    'title': elt.title,
                    'start': elt.start,
                    'end': elt.end,
                    'color': elt.color,
                    'allDay': false,
                }
                }else{
                    e = {
                    'id': elt.id ,
                    'title': "R "+elt.title,
                    'startTime': elt.startTime, 
                    'endTime': elt.endTime,
                    'startRecur': elt.startRecur,
                    'endRecur' : elt.endRecur,
                    'daysOfWeek': elt.daysOfWeek,
                    'color': elt.color,
                }
            }
            evt.push(e)  
            })
            configCalHeure(evt)
            miseEnformeCalendrierSemaine()
        },
        error: function (response) {
            console.log(response)
        }
    })
}

//récupération des jours spécifiques pour Adjoint/superviseur
function getRdvAdjoinSuperviseur(url,man=0){
    evt = []
    $.ajax({
        type: 'GET',
        url: url,
        data:{man:man},
        success: function (response) {
            response['liste'].forEach(elt => {
                        e = {
                        'id': elt.id,
                        'title': elt.titre,
                        'start': elt.debut,
                        'end': elt.fin,
                        'color': elt.couler,
                        'allDay': false
                    }
                evt.push(e)
            })
            configCalHeure1(evt)
            miseEnformeCalendrierSemaine()
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function configCalHeure(evts) {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        initialView: 'timeGridWeek',
        selectMirror: true,
        events: evts,
        locales: 'fr',
        slotMinTime: "08:00:00",
        slotMaxTime: "18:00:00",
        hiddenDays: [ 0, 6 ],
        eventClick: function (arg) {
             console.log(arg.event._def.publicId)
             if (confirm('Voulez vous vraiment  supprimer  cet horaire??')) {
                  $.ajax({
                            type: 'GET',
                            url: 'delete',
                            data: { 'id': arg.event._def.publicId },
                            success: function (response) {
                                window.location.replace("/administration/jours_specifiques/")
                            },
                            error: function (response) {
                                alert("Echec veuillez reéssayer plus tard")
                                console.log(response)
                            }
                        })
            }
        }
    });
    calendar.render();
}

//Fin des méthodes du calendrier

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

function dateChangeEvent(date_s, url) {
    dt = date_s.split("-")
    month = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Decembre']
    mois = month[(parseInt(dt['1']) - 1)]
    selected_date = new Date(mois + "/" + dt[0] + "/" + dt[2])
    if (selected_date.getDay() == 0 | selected_date.getDay() == 6) {
        $("inputDate").val('')
        $("#warningWeekend").css('display', 'inline')
        $('#creneau').empty()
        $('#inputHeure').val('')
        return 0
    } else {
        $("#warningWeekend").css('display', 'none')
        oday = new Date()
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
            //InputServiceSelect(url, selected_date.getDay())
        }
    }
}

function InputServiceSelect(url, day) {
    service = $('#inputService').val()
    $('#inputHeure').val('')
    $.ajax({
        type: 'GET',
        url: url,
        data: { "service": service },
        success: function (response) {
            if (response['bad'] == false) {
                content = "<option selected>............</option>"
                if (day == 1) {
                    response['lundi'].forEach(elt => {
                        content = content + "<option value = " + elt['debut'] + ">" + elt['debut'] + " - " + elt['fin'] + "</option>"
                    });
                    $('#creneau').empty()
                    $('#creneau').append(
                        "   <div class='column is-4'>\
                                <label>Créneaux horaires</label>\
                            </div>\
                            <div class='column'>\
                                <div class='select is-small'>\
                                    <select id='creneauChoice' onchange='getval(this);'> "+ content + "</select>\
                                </div>\
                            </div>"
                    )
                } else {
                    response['reste'].forEach(elt => {
                        content = content + "<option value = " + elt['debut'] + ">" + elt['debut'] + " - " + elt['fin'] + "</option>"
                    });
                    $('#creneau').empty()
                    $('#creneau').append(
                        "   <div class='column is-4'>\
                                <label>Créneaux horaires</label>\
                            </div>\
                            <div class='column'>\
                                <div class='select is-small'>\
                                    <select id='creneauChoice' onchange='getval(this);'> "+ content + "</select>\
                                </div>\
                            </div>"
                    )

                }
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
}

function Delete(url, option) {
    if (option == "RDV") {
        $("#delete").attr("href", url);
    } else if (option == "conge") {
        $("#delete1").attr("href", url);
    } else if (option == "responsable") {
        $("#delete2").attr("href", url);
    } else if (option == "service") {
        $("#delete3").attr("href", url);
    } else if (option == "ADM") {
        $("#deleteAdm").attr("href", url);
    } else {

    }
}


function changeInput(val) {
    if (val == "date") {
        $('#dataSearchFieldDashboard').empty()
        $('#dataSearchFieldDashboard').append(
            "<input type='date' id='dahsBoardDataSearchField' class='w-100 input is-small' />"
        )
    } else if (val == 'administre') {
        $('#dataSearchFieldDashboard').empty()
        $('#dataSearchFieldDashboard').append(
            "<input type='email' id='dahsBoardDataSearchField' class='w-100 input is-small' placeholder='mail aministré' />"
        )
    }
    else if (val == 'service') {
        $('#dataSearchFieldDashboard').empty()
        $('#dataSearchFieldDashboard').append(
            "<input type='text' id='dahsBoardDataSearchField' class='w-100 input is-small' placeholder='Nom du service' />"
        )
    } else {
        $('#dataSearchFieldDashboard').empty()
    }
}

function getRdvBySearch(url) {
    valeur = $('#dahsBoardDataSearchField').val()
    attribut = $('#filterDashboard').val()
    $.ajax({
        type: 'GET',
        url: url,
        data: { 'valeur': valeur, "attribut": attribut },
        success: function (response) {
            $('#contentTable').empty()
            $('#title1').empty()
            $('#title1').append("<h3>Tous mes Rendez-vous par " + attribut + ": " + valeur + " </h3>")
            response['rdvs'].forEach(elt => {
                vars = ""
                if (elt.etat == 'Approuve'){
                    vars = vars+'<option value="Approuvé" selected> Approuvé</option>'
                }else{
                    vars = vars + '<option value="Approuvé"> Approuvé</option>'
                }
                if(elt.etat == 'En attente'){
                    vars = vars+' <option value="En attente" selected> En attente</option>'
                }else{
                    vars = vars+'<option value="En attente"> En attente</option>'
                }
                if(elt.etat == 'Annule'){
                    vars = vars + ' <option value="Annulé" selected> Annulé</option>'
                }else{
                    vars = vars + '<option value="Annulé"> Annulé</option>'
                }
                $('#contentTable').append(
                    "<tr>\
                        <td>"+ elt.client + " <br> <strong>" + elt.service + "</strong></td>\
                        <td>"+ elt.date + "</td>" +
                        '<td>\
                            <div class="select is-rounded is-small">\
                                <select id="Etat'+elt.id+'" onchange="go1('+elt.id+')">'+
                                    vars+
                                '</select>\
                            </div>\
                        </td>\
                        <td>\
                    <td> <a href="/administration/rdv/recuperer/' + elt.id + '" class="is-success button is-small" ><span><i class="fa fa-eye"></i></span></a> </td>\
                    </tr>'
                )
            });
        },
        error: function (response) {

        }
    })
}

//recherche de RDV par date
function findRdvBydate(url) {
    debut = $('#datedebSearchRdv').val()
    fin = $('#dateFinSearchRdv').val()
    $.ajax({
        type: 'GET',
        url: url,
        data: { 'debut': debut, "fin": fin },
        success: function (response) {
            $('#contentTable1').empty()
            $('#title1').empty()
            $('#title1').append("<h3>Tous mes Rendez-vous du " + debut + " au  " + fin + " </h3>")
            response['rdvs'].forEach(elt => {
                vars = ""
                if (elt.etat == 'Approuve'){
                    vars = vars+'<option value="Approuvé" selected> Approuvé</option>'
                }else{
                    vars = vars + '<option value="Approuvé"> Approuvé</option>'
                }
                if(elt.etat == 'En attente'){
                    vars = vars+' <option value="En attente" selected> En attente</option>'
                }else{
                    vars = vars+'<option value="En attente"> En attente</option>'
                }
                if(elt.etat == 'Annule'){
                    vars = vars + ' <option value="Annulé" selected> Annulé</option>'
                }else{
                    vars = vars + '<option value="Annulé"> Annulé</option>'
                }
                $('#contentTable1').append(
                    "<tr>\
                        <td>"+ elt.client + "</td>\
                        <td> " + elt.service + "</td>\
                        <td>"+ elt.date + "</td>" +
                        '<td>\
                            <div class="select is-rounded is-small">\
                                <select id="Etat'+elt.id+'" onchange="go1('+elt.id+')">'+
                                    vars+
                                '</select>\
                            </div>\
                        </td>\
                        <td> <a href="recuperer/' + elt.id + '" class="is-success button is-small" ><span><i class="fa fa-eye"></i></span></a> </td>\
                    </tr>'
                )
            });
        },
        error: function (response) {

        }
    })
}

function changeInputAdministre(val) {
    if (val == "nom") {
        $('#dataSearchFieldAdministre').empty()
        $('#dataSearchFieldAdministre').append(
            "<input type='text' id='administreDataSearchField' class='w-100 input is-small' placeholder='Nom administre' />"
        )
    } else if (val == 'email') {
        $('#dataSearchFieldAdministre').empty()
        $('#dataSearchFieldAdministre').append(
            "<input type='email' id='administreDataSearchField' class='w-100 input is-small' placeholder='mail aministré' />"
        )
    }
    else {
        $('#dataSearchFieldAdministre').empty()
    }
}

function getAdministreBySearch(url) {
    valeur = $('#administreDataSearchField').val()
    attribut = $('#filterAdministre').val()
    $.ajax({
        type: 'GET',
        url: url,
        data: { 'valeur': valeur, "attribut": attribut },
        success: function (response) {
            Liste_del = []
            $('#contentTable2').empty()
            $('#title2').empty()
            $('#title2').append("<h3>Tous mes Adminstrés par " + attribut + ": " + valeur + " </h3>")
            response['administre'].forEach(elt => {
                $('#contentTable2').append(
                    "<tr>\
                        <td>\
                            <label class='checkbox'>\
                                <input type='checkbox' id='addDel"+elt.id+"' onclick='addToDelete("+elt.id+")'>\
                            </label>\
                        </td>\
                        <td>"+ elt.nom + "</td>\
                        <td>"+ elt.prenom + "</td>\
                        <td> <strong>" + elt.email + "</strong>" +
                    '<td> <a href="recuperer/' + elt.id + '" class="is-success button is-small" ><span><i class="fa fa-eye"></i></span></a> </td>\
                    </tr>'
                )
            });
        },
        error: function (response) {

        }
    })
}

function miseEnformeCalendrierSemaine(){

    $('.fc-timegrid-axis-cushion').css('display','none')
            $(".fc-dayGridMonth-button").text(" ");
            $(".fc-dayGridMonth-button").text("Mois");

            $(".fc-timeGridWeek-button").text(" ");
            $(".fc-timeGridWeek-button").text("Semaine");

            $(".fc-today-button").text(" ")
            $(".fc-today-button").text("Aujourd'hui")

            $(".fc-timeGridDay-button").text(" ")
            $(".fc-timeGridDay-button").text("Jours")

            $(".fc-dayGridMonth-button").on('click',function(){
                $(".fc-dayGridMonth-button").text(" ");
                $(".fc-dayGridMonth-button").text("Mois");
                $(".fc-timeGridDay-button").text(" ")
                $(".fc-timeGridDay-button").text("Jours")
                $(".fc-timeGridWeek-button").text(" ");
                $(".fc-timeGridWeek-button").text("Semaine");
                $('.fc-timegrid-axis-cushion').css('display','none')

                $(".fc-today-button").text(" ")
                $(".fc-today-button").text("Aujourd'hui")
            })

            $(".fc-timeGridWeek-button").on('click',function(){
                $(".fc-dayGridMonth-button").text(" ");
                $(".fc-dayGridMonth-button").text("Mois");
                $(".fc-timeGridDay-button").text(" ")
                $(".fc-timeGridDay-button").text("Jours")
                $(".fc-timeGridWeek-button").text(" ");
                $(".fc-timeGridWeek-button").text("Semaine");
                $('.fc-timegrid-axis-cushion').css('display','none')

                $(".fc-today-button").text(" ")
                $(".fc-today-button").text("Aujourd'hui")
            })

            $('.fc-prev-button').on('click',function(){
                $(".fc-dayGridMonth-button").text(" ");
                $(".fc-dayGridMonth-button").text("Mois");
                $(".fc-timeGridDay-button").text(" ")
                $(".fc-timeGridDay-button").text("Jours")
                $(".fc-timeGridWeek-button").text(" ");
                $(".fc-timeGridWeek-button").text("Semaine");
                $('.fc-timegrid-axis-cushion').css('display','none')

                $(".fc-today-button").text(" ")
                $(".fc-today-button").text("Aujourd'hui")
            })

            $('.fc-next-button').on('click',function(){
                $(".fc-dayGridMonth-button").text(" ");
                $(".fc-dayGridMonth-button").text("Mois");
                $(".fc-timeGridDay-button").text(" ")
                $(".fc-timeGridDay-button").text("Jours")
                $(".fc-timeGridWeek-button").text(" ");
                $(".fc-timeGridWeek-button").text("Semaine");
                $('.fc-timegrid-axis-cushion').css('display','none')

                $(".fc-today-button").text(" ")
                $(".fc-today-button").text("Aujourd'hui")
            })

            $(".fc-timeGridDay-button").on('click',function(){
                $(".fc-dayGridMonth-button").text(" ");
                $(".fc-dayGridMonth-button").text("Mois");
                $(".fc-timeGridDay-button").text(" ")
                $(".fc-timeGridDay-button").text("Jours")
                $(".fc-timeGridWeek-button").text(" ");
                $(".fc-timeGridWeek-button").text("Semaine");
                $('.fc-timegrid-axis-cushion').css('display','none')

                $(".fc-today-button").text(" ")
                $(".fc-today-button").text("Aujourd'hui")
            })

}

function configCalHeure1(evts) {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        initialView: 'timeGridWeek',
        selectMirror: true,
        events: evts,
        locales: 'fr',
        slotMinTime: "08:00:00",
        slotMaxTime: "18:00:00",
        hiddenDays: [ 0, 6 ],
        eventClick: function (arg) {
            alert("Informations du RDV\n" + arg.event._def.title +"\nheure de début : " + ('0'+arg.el.fcSeg.start.getUTCHours()).slice(-2) + " H: " + ('0'+arg.el.fcSeg.start.getMinutes()).slice(-2) + " Min\nheure de fin : " +('0'+arg.el.fcSeg.end.getUTCHours()).slice(-2) + " H:" + ('0'+arg.el.fcSeg.end.getMinutes()).slice(-2) + " Min")
        }
    });
    calendar.render();
}