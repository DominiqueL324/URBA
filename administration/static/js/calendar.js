var Liste_Evt = []
id = 0
agent = 0
duree = 0
debut = new Date()
fin = new Date()

function configCalHeureAdd() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            left: 'prev,next',
            center: 'title',
            right: 'prev,next',
        },
        //initialDate: date_s,
        initialView: 'dayGridMonth',
        selectable: true,
        selectMirror: true,
        locales: 'fr',
        slotMinTime: "08:00:00",
        slotMaxTime: "18:00:00",
        hiddenDays: [ 0, 6 ],
        //events: evt,
        select: function (arg) {
            
           /* oday = new Date()
            selected_date = arg.start
            if (oday > selected_date) {
                alert('Plus de jours spécifiques possible à cette date')
                return
            } else {
                diff_temps = selected_date.getTime() - oday.getTime()
            }
            diff_jour = Math.round(diff_temps / (1000 * 3600 * 24));
            if (diff_jour < 6) {
                oday.setDate(oday.getDate() + 7)
                alert('Vous ne pouvez pas enregistrer un jour spécifique avant le ' + oday.getDate() + "/" + (oday.getMonth() + 1) + "/" + oday.getFullYear())
                return
            }*/

            if ($("#heuerD").val() != '' && $("#heuerF").val() != '') {
                id = id + 1
                evt = {
                    id: id,
                    title: " ",
                    start: arg.startStr + "T" + $("#heuerD").val() + ":00",
                    end: arg.startStr + "T" + $("#heuerF").val() + ":00",
                    allDay: false,
                }
                calendar.addEvent(evt)
                evt = {
                    id: id,
                    title: " ",
                    start: arg.startStr,
                    startTime: $("#heuerD").val() + ":00",
                    endTime: $("#heuerF").val() + ":00",
                    allDay: false,
                }
                Liste_Evt.push(evt)
            } else {
                alert('Horaires invalides')
            }
            console.log(Liste_Evt)
            calendar.unselect()
        },
        eventClick: function (arg) {
            if (confirm('Confirmez vous la suppréssion??')) {
                for (var i = 0; i < Liste_Evt.length; i++) {
                    if (Liste_Evt[i].id == arg.event.id) {
                        Liste_Evt.splice(i, 1)
                        arg.event.remove()
                    }
                }
                console.log(Liste_Evt)
            }
        }
    });
    calendar.render();
}

//ajout d'un jours spécifique non consécutif
function validerClick(url, val) {
    test = $('#serv').val()// c'est un tableau
    if ($("#heuerD").val().split(":")[0]=="12"  ){
        alert("Pas de travail durant les heures de pause")
        return
    }
    
    if ($("#heuerD").val() != '' && $("#heuerF").val() != '' && $('#serv').val() != '') {
        $('#warning1').css('display', 'none')
        if (Liste_Evt.length < 1) {
            $('#warning2').css('display', 'inline')
            return
        }
        evts = JSON.stringify(Liste_Evt)
        tests = JSON.stringify(test)
        $.ajax({
            type: 'POST',
            url: url,
            data: { evt: evts, service: tests, "csrfmiddlewaretoken": val },
            success: function (response) {
                window.location.replace("/administration/jours_specifiques/")
            },
            error: function (response) {
                alert("Echec veuillez reéssayer plus tard")
                console.log(response)
            }
        })

        Liste_Evt.push(evt)
    } else {
        $('#warning1').css('display', 'inline')
    }
}

//ajout d'un jour spécifique réccurent
function validerClickRecurrent(url,val){
    id=0
    evt = {}
    if ($("#heuerDR").val().split(":")[0]=="12" ){
        alert("Pas de travail durant les heures de pause")
        return
    }
   if ($("#heuerDR").val() != '' && $("#heuerFR").val() != '' && $('#dateDR').val() != '' && $('#serviceR').val() != '' && $('#jour').val() != '') {
       id = id + 1
       if( $('#dateDR').val() != ''){
            evt = {
                id: id,
                title: " ",
                daysOfWeek: $('#jour').val(),
                startRecur: $('#dateDR').val(),
                endRecur: $('#dateFR').val(),
                startTime:  $("#heuerDR").val() + ":00",
                endTime:  $("#heuerFR").val() + ":00",
            }  
       }else{
           evt = {
                id: id,
                title: " ",
                daysOfWeek: $('#jour').val(),
                startRecur: $('#dateDR').val(),
                startTime:  $("#heuerDR").val() + ":00",
                endTime: $("#heuerFR").val() + ":00",
            } 
       }
        evts = JSON.stringify(evt)
        days = JSON.stringify($('#jour').val())
        services = JSON.stringify($('#serviceR').val())
       $.ajax({
            type: 'POST',
            url: url,
            data: { evt: evts, service:  services,day:days, "csrfmiddlewaretoken": val },
            success: function (response) {
                window.location.replace("/administration/jours_specifiques/")
            },
            error: function (response) {
                alert("Echec veuillez reéssayer plus tard")
                console.log(response)
            }
        })
        
   } else {
       $('#warning3').css('display', 'inline')
       return;
   }
}

//<<<<<<<<<<<<<<<<<<<<<<<<module Agenda Agent

//initialisation du calendrier
function calendrierAgenda(evts,url1){
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            left: 'prev,next',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }, 
        //initialDate: date_s,
        initialView: 'dayGridMonth',
        locales: 'fr',
        slotMinTime: "08:00:00",
        slotMaxTime: "18:00:00",
        events: evts,
        hiddenDays: [ 0, 6 ],
        select: function (arg) {
        },
        eventClick: function (arg) {
            $.ajax({
                type: 'GET',
                url: '/administration/jours_specifiques/get_hours/agenda', 
                data:{'id':arg.event._def.publicId},
                success: function (response) {
                    response['heures'].forEach(elt=>{
                    console.log(arg)
                    debut =null
                    fin= null
                    debut = new Date(arg.event._instance.range.start.getFullYear(), arg.event._instance.range.start.getMonth(),  arg.event._instance.range.start.getDate(), elt.debutH,elt.debutM, 0)
                    fin = new Date(arg.event._instance.range.end.getFullYear(), arg.event._instance.range.end.getMonth(), arg.event._instance.range.end.getDate(),elt.finH,elt.finM, 0)
                    agent = arg.event._def.publicId
                    $('#dateR').val(arg.event._instance.range.start.getFullYear()+"-"+('0'+(arg.event._instance.range.start.getMonth()+1)).slice(-2)+"-"+('0'+arg.event._instance.range.start.getDate()).slice(-2))
                    clearForm()
                    $("#debut").empty()
                    $("#fin").empty()
                    $('#debut').text('Minimum '+('0'+debut.getHours()).slice(-2)+":"+('0'+debut.getMinutes()).slice(-2))
                    $('#fin').text('Maximun '+('0'+fin.getHours()).slice(-2)+":"+('0'+fin.getMinutes()).slice(-2))
                    $('#serviceI').val(arg.event._def.title )
                    $('#ModalCenter').modal('show')
                    getAllAdministres(url1)
                    })
                },
                error: function (response) {
                    calert("Erreur durant la récupération des données veuillez reéssayer plus tard")
                    clearForm()
                    $('#ModalCenter').modal('hide')
                }
            })
        }
    });
    calendar.render();
}
//initialisation des évènements
function getAllJoursSpecifiques(url,url1,man=0){
    evt=[]
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
            calendrierAgenda(evt,url1)
            miseEnformeCalendrierSemaine()
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function getAllAdministres(url){
    $.ajax({
        type: 'GET',
        url: url,
        cache: false,
        data:{id:agent},
        success: function (response) {
            duree = response['temps']
            $('#responsableI').val(response['agent'])
            $('#administreI').empty()
            $('#administreI').append(
                '<option value="">---------------</option>'
            )
            response['administres'].forEach(elt => { 
                $('#administreI').append(
                    '<option value='+elt.id+'>'+elt.nom+'</option>'
                )
            })
        },
        error: function (response) {
            console.log(response)
        }
    })  
}
//evenement sur le changement d'heure
$("#heureDI").on('change', function () {
    min = duree
    var fn = new Date("November 13, 2021 " + $("#heureDI").val());
    fn.setMinutes(fn.getMinutes() + parseInt(min))
    $("#heureFI").val(('0' + fn.getHours()).slice(-2) + ":" + ('0' + fn.getMinutes()).slice(-2))
})
 
$("#heureDI").keypress(function () {
    min = duree
    temps = $("#heureDI").val()
    var fn = new Date("November 13, 2021 " + temps);
    fn.setMinutes(fn.getMinutes() + parseInt(min))
    $("#heureFI").val(('0' + fn.getHours()).slice(-2) + ":" + ('0' + fn.getMinutes()).slice(-2))
})

//netotyage du formulaire d'ajout
function clearForm(){
    $("#heureDI").val("")
    $("#heureFI").val("")
    $("#telephoniqueI").val("")
    $("#administreI").val("")
    document.getElementById('fichiers').value = null
    $("#warning1").css('display', 'none')
    $("#warning5").css('display', 'none')
    $("#warning2").css('display', 'none')
    $("#warning3").css('display', 'none')
    $("#warning4").css('display', 'none')
    $("#warning6").css('display', 'none')
    $('#waiter').css('display','none')
}

//clique sur le bouton d'ajout de RDV
function saveRdv(url){
    $("#warning2").css('display', 'none')
    $("#warning4").css('display', 'none')
    $("#warning3").css('display', 'none')
    $("#warning1").css('display', 'none')
    $("#warning6").css('display', 'none')
    $("#warning5").css('display', 'none')
    $('#waiter').css('display','inline')
    //controle de tous les champs obligatoire
    if($("#heureDI").length==0 || $("#personneI").length==0 || $('#telephoniqueI').val()=="" || $('#administreI').val()==""){
        $("#warning2").css('display', 'none')
        $("#warning1").css('display', 'inline')
        $("#warning3").css('display', 'none')
        $("#warning4").css('display', 'none')
        $("#warning6").css('display', 'none')
        $("#warning5").css('display', 'none')
        $('#waiter').css('display','none')
        return
    }
    var heureD = new Date("November 13, 2021 " + $("#heureDI").val());
    var heureF = new Date("November 13, 2021 " + $("#heureFI").val());
    pauseD = new Date("November 13, 2021 " + "12:01:00").getTime();
    pauseF = new Date("November 13, 2021 " + "12:59:00").getTime();

    d = new Date().setHours(heureD.getHours(),heureD.getMinutes(),"00")
    f = new Date().setHours(heureF.getHours(),heureF.getMinutes(),"00")
    evd = new Date().setHours(debut.getHours(),debut.getMinutes(),"00")
    evf = new Date().setHours(fin.getHours(),fin.getMinutes(),"00")
    console.log(d)
    console.log(f)
    console.log(evd)
    console.log(evf)
    //controle des heure d'ouverture et de fermeture
    if (d < evd || f > evf) {
        $("#warning2").css('display', 'inline')
        $("#warning4").css('display', 'none')
        $("#warning3").css('display', 'none')
        $("#warning1").css('display', 'none')
        $("#warning5").css('display', 'none')
        $("#warning6").css('display', 'none')
        $('#waiter').css('display','none')
        $("#warning6").css('display', 'none')
        return
    }
    //controle de chevauchement pause
    if ((heureD >= pauseD && heureD <= pauseF) || (heureF >= pauseD && heureF <= pauseF)) {
        $("#warning2").css('display', 'none')
        $("#warning1").css('display', 'none')
        $("#warning3").css('display', 'none')
        $("#warning4").css('display', 'inline')
        $("#warning5").css('display', 'none')
        $('#waiter').css('display','none')
        $("#warning6").css('display', 'none')
        return
    }
    if($("#personneI").val()>2 || $("#personneI").val()<0){
        $("#warning2").css('display', 'none')
        $("#warning1").css('display', 'none')
        $("#warning3").css('display', 'none')
        $("#warning4").css('display', 'none')
        $("#warning6").css('display', 'none')
        $("#warning5").css('display', 'inline')
        $('#waiter').css('display','none')
        return
    }
    /*datas = {
            "js": agent,
            "administre":$("#administreI").val(),
            "telephone":$("#telephoniqueI").val(),
            "debut": $('#heureDI').val(),
            "fin": $('#heureFI').val(),
            "csrfmiddlewaretoken":$("input[name='csrfmiddlewaretoken']").val(),
            "date": $('#dateR').val(),
            "personne": $("#personneI").val(),
        }*/
    var formdata = new FormData()
    files_ = []
    var files_obj = document.getElementById('fichiers').files
    formdata.append("js", agent)
    formdata.append("administre", $("#administreI").val())
    formdata.append("telephone", $("#telephoniqueI").val())
    formdata.append("debut", $("#heureDI").val())
    formdata.append("fin", $("#heureFI").val())
    formdata.append("csrfmiddlewaretoken", $("input[name='csrfmiddlewaretoken']").val())
    formdata.append("date", $("#dateR").val())
    formdata.append("personne", $("#personneI").val())
    formdata.append("adresseTravauxInput", $("#adresseTravauxInput").val())
    k=0
    if(files_obj.length > 0){
        for(i=0;i<files_obj.length;i++){
            formdata.append("fichiers"+i,files_obj[i])
            k=k+1
        }
    }
    formdata.append("taille",k)

    //console.log()
    $.ajax({
        type: "POST",
        url: url,
        data:formdata,
        cache : false,
        processData: false,
        contentType: false,
        success: function(response){
            if(response['good']==1){
                clearForm()
                $('#ModalCenter').modal('hide')
                window.location.replace("/administration/agenda/")
            }
            if(response['existant']==1){
                $("#warning2").css('display', 'none')
                $("#warning1").css('display', 'none')
                $("#warning3").css('display', 'none')
                $("#warning4").css('display', 'none')
                $("#warning6").css('display', 'inline')
                $("#warning5").css('display', 'none')
                $('#waiter').css('display','none')
                return
            }
            
        },
        error: function(response){
            alert('Erreur d\'insertion veuillez reéssayer plus tard')
            console.log(response)
        }
    })
    
}


