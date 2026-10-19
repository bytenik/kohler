function trace(s) {
    try {
        console.log(s);
    } catch (e) { /*alert(s)*/ }
}
$.ajaxSetup({
    cache: false
});
var hide_things = true;
var discon_string = 'Dis';
var con_string = 'Con';
var user_title = 'User:';
var config_index = 0;
var config_a = 'Configuration A';
var config_a_1 = 'Configuration A Alt 1';
var config_a_2 = 'Configuration A Alt 2';
var config_a_3 = 'Configuration A Alt 3';
var config_b = 'Configuration B';
var config_b_1 = 'Configuration B Alt 1';
var config_b_2 = 'Configuration B Alt 2';
var config_b_3 = 'Configuration B Alt 3';
var config_c = 'Configuration C';
var config_d = 'Configuration D';
var config_d_1 = 'Configuration D Alt 1';
var config_d_2 = 'Configuration D Alt 2';
var config_d_3 = 'Configuration D Alt 3';
var config_unwind = 'Retro Fit | Unwind';
var config_downpour = 'Retro Fit | Downpour';
var config_frontage = 'Retro Fit | Frontage';
var config_surround = 'Retro Fit | Surround';
var config_linear = 'Retro Fit | Linear';
var config_envelop = 'Retro Fit | Envelop';
var configv1_outlets = 0;
var configv2_outlets = 0;
var none_text = "none";
var modules_installed = 0;
var bool_light1_dimmer = true;
var bool_light2_dimmer = true;
var bool_light3_dimmer = true;
var bool_needs_save = false;
var reload = false;
var upload_requested = false;
var powerclean_On = 0;   //TF Team 07-07
var total_ftp_image_size = 0; //TF Team 08-07
var downloaded_size = 0; //TF Team 08-07
var intermittent_string = 'Intermittent'; //TF team 08-07
var ftp_start = 0;

function displayTime() {
    var str = "";
    var currentTime = new Date();
    var hours = currentTime.getHours();
    var minutes = currentTime.getMinutes();
    var seconds = currentTime.getSeconds();
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    if (seconds < 10) {
        seconds = "0" + seconds;
    }
    str += hours + ":" + minutes + ":" + seconds + " ";
    if (hours > 11) {
        str += "PM";
    } else {
        str += "AM";
    }
    return str;
}
$(function () {
    $("#tabs-Service").tabs({
        activate: function (event, ui) {
            reload = true;
            //alert('selected: '+ui.newTab.index());
            trace(displayTime());
            service_load();
            trace(displayTime());
        }
    });
    $("#tabs-Service li[role=tab]").unbind('keydown');
});
function check_updates() {
    $.ajax({
        type: "GET",
        url: "check_updates.cgi",
        data: {},
        dataType: "JSON",
        cache: false
    });
}

function update_value(indexin, valuein) {
    bool_needs_save = true;
    trace('Update Value: ' + valuein + ', Index: ' + indexin);
    $.ajax({
        type: "GET",
        url: "save_variable.cgi",
        data: {
            index: indexin,
            value: valuein
        },
        dataType: "text",
        cache: false
    });
}


function getFile(){
	$('#upload_status_wait').hide();
	$('#upload_status_done').hide();
	$('#upload_wait').hide();
	$('#file_select_name').hide();
	$('#file_upload').hide();
	upload_requested = false;
	document.getElementById("upload_filename").innerHTML = "";
    document.getElementById("upfile").click();
}

function sub(obj){
    var file = obj.value;
    var fileName = file.split("\\");
	var uploadpath = $('#upfile').val();
    var fileExtension = uploadpath.substring(uploadpath.lastIndexOf(".") + 1, uploadpath.length);
	
	if ($('#upfile').val().length == 0) {
        // write error message
        // alert("file name length is zero");
		$('#file_upload').hide();
        return false;
    }
    if (fileExtension == "hex" || fileExtension == "HEX" || fileExtension == "S19" || fileExtension == "s19") {
		$('#file_select_name').show();
		$('#file_upload').show();
		document.getElementById("upload_filename").innerHTML = fileName[fileName.length-1];
		//document.myForm.submit();
		
		event.preventDefault();
    }
    else {
        //error code - select only excel files
		//CORYO - Should we display text saying this file type can't be uploaded?
        alert("Cannot upload files of this type.");
		$('#file_upload').hide();
        return false;
    }
}

function reset_system() {
	$.ajax({
		type: "GET",
		url: "reset_factory.cgi",
		data: {},
		dataType: "text",
		cache: false,
		success: function (data) {
			window.location = "tabview.html";
		}
	});
}

function reset_users() {
    $.ajax({
        type: "GET",
        url: "reset_users.cgi",
        data: {},
        dataType: "JSON",
        cache: false,
        success: function (data) {
            window.location = "tabview.html";
        }
    });
}

/*function confirm_reset() {
	$('#dialog-confirm').dialog({
		resizable: false,
		height: 140,
		modal: true,
		draggable: false,
		dialogClass: 'main-dialog-class',
		buttons: [
			{
				text: "Yes", 
				click: function() {
					reset_system();
					$( this ).dialog( "close" );
				},
			},
			{
				text: "No", 
				click: function() {
					$( this ).dialog( "close" );
				}
			}
		]
	});
}*/ //Commented by TF-Team to remove Reset system button on 20-11-2015

/*function confirm_reset_defaults() {
	$('#dialog-confirm').dialog({
		resizable: false,
		height: 140,
		modal: true,
		draggable: false,
		dialogClass: 'main-dialog-class',
		buttons: [
			{
				text: "Yes", 
				click: function() {
					reset_defaults();
					$( this ).dialog( "close" );
				},
			},
			{
				text: "No", 
				click: function() {
					$( this ).dialog( "close" );
				}
			}
		]
	});
}*/  //Commented by TF-Team to remove Reset system button on 20-11-2015

//Added By TF2 - Open and Closing Dialog Box during Upload - Bug 870
/* *********************************************************************************************************************** */
function Upload_message() {
	$('#dialog-warning').dialog({
		closeOnEscape: false,
		height: "auto !important",
		width: "auto !important",
		resizable: false,
		modal: true,
		draggable: false,
		dialogClass: 'dialog-class-transparent',    /*Changed by TF2 March*16*2015 Bug - 1154 for transparent dialog box*/
	});
}

function Unload_message() {
	$('#dialog-warning').dialog("close");
}
/* *********************************************************************************************************************** */
//End of Add by TF2

function reset_defaults() {
    $.ajax({
        type: "GET",
        url: "reset_default.cgi",
        data: {},
        dataType: "JSON",
        cache: false,
        success: function (data) {
            window.location = "tabview.html";
        }
    });
}

function update_six_port_cal_code(indexin, valuein) {
	//Range check the value.
	if( (valuein >= 160) && (valuein <= 200) ) {
		if(indexin === 1) {
			//Valve1 Cal Code
            document.getElementById('valve1_cal_err').innerHTML = "";
			document.getElementById('valve1_cal_err').style.display = 'none';
			update_value(const_six_port_calibration_valve1, valuein);
		} else {
			//Valve2 Cal Code.
            document.getElementById('valve2_cal_err').innerHTML = "";
			document.getElementById('valve2_cal_err').style.display = 'none';
			update_value(const_six_port_calibration_valve2, valuein);
		}
	} else {
		//alert('Calibration Code range is 160 - 200');
		if(indexin === 1) {
            document.getElementById("valve1_cal_err").innerHTML = "Error: Calibration code range is 160 to 200";
			document.getElementById("valve1_code").value = "";
			document.getElementById('valve1_cal_err').style.display = 'block';
		} else {
            document.getElementById("valve2_cal_err").innerHTML = "Error: Calibration code range is 160 to 200";
			document.getElementById("valve2_code").value = "";
			document.getElementById('valve2_cal_err').style.display = 'block';
		}
	}
}

//**********************TF Team ftp progress bar 08-07

function progress_update() {
            var progressbar = $( "#ftpprogressbar" );
               $( "#ftpprogressbar" ).progressbar({
                  value: 0,
                  max: 100
               });
			   
            function progress() {
				var val = 0;
			val = Math.round((downloaded_size/total_ftp_image_size)*100);
            progressbar.progressbar( "value", val + 1 );
			 $("#ftp_percentage").html(val + "%");   //Added for inline percentage text
            if ( val < 99 ) {
               setTimeout( progress, 1000 );
            }
         }
         setTimeout( progress, 3000 );
      } 
	  
var ftp_upload = 0;	  
var ftp_upload_error = 0;
//**********************TF Team ftp progress bar 08-07
function loadXMLDoc() {
    trace('LoadXMLDoc');
    $.ajax({
        type: "GET",
        url: "ftp_status.cgi",
        data: {},
        dataType: "JSON",
        cache: false,
//Commented on 18-06		error: function (XMLHttpRequest, textStatus, errorThrown) {
//Commented on 18-06            alert("An error occurred getting updates from the unit - heartbeat failed. Status: " + textStatus + ", Error: " + errorThrown);
//Commented on 18-06        },
        success: function (data) {//CORYO - FTP Stats here!
		   if(data.ftp_download_error && (ftp_start == 1))
			   ftp_upload_error = 1;
            if(data.value)
            {
				$('#FTP_upload_status_done').hide();
				$('#FTP_upload_status_error').hide();
                $('#ftp_status').show();
				ftp_start = 1;
				
				 //Added by TF Team 08-07
				 if(data.ftp_file_count > 0)
				 {	 
					$('#ftpprogressbar').show(); 
					$('#filecount').show(); 
				 }	
				$("#char_start").html("Downloading Files ");
				$("#currentfile").html(data.ftp_current_file_count); //Added for inline percentage text
				$("#char_of").html(" of "); //Added for inline percentage text
				$("#totalfiles").html(data.ftp_file_count); //Added for inline percentage text
				
				if(data.ftp_file_id == 1)
					total_ftp_image_size = data.ftp_ctl_image_size;
				else if(data.ftp_file_id == 2)
					total_ftp_image_size = data.ftp_ui_image_size;
				else if(data.ftp_file_id == 7)
					total_ftp_image_size = data.ftp_prompt3_flash_size;
				else if(data.ftp_file_id == 8)
					total_ftp_image_size = data.ftp_prompt3_eeprom_size;
				
				downloaded_size = data.ftp_downloaded_size; //Added by TF Team 08-07
				progress_update();
				if((data.ftp_current_file_count == data.ftp_file_count) && (total_ftp_image_size == total_ftp_image_size))
					ftp_upload = 1;
				 //Added by TF Team 08-07	
				
            }
			else
			{
                $('#ftp_status').hide();
				$('#ftpprogressbar').hide();  //Added by TF Team 08-07
				$('#filecount').hide(); //Added by TF Team 09-07
				total_ftp_image_size = 0; //Added by TF Team 08-07
				downloaded_size = 0; //Added by TF Team 08-07
				if(ftp_upload == 1 && (ftp_upload_error == 0)) //Added by TF Team 08-07
				{
					//$('#FTP_upload_status_done').show(); //Added by TF Team 08-07	
					setTimeout( $('#FTP_upload_status_done').show(), 5000 );
					//$('#FTP_upload_status_done').hide();
				}
				if( ftp_upload_error == 1)
				{
					ftp_start = 0;
					ftp_upload_error = 0;
					setTimeout( $('#FTP_upload_status_error').show(), 5000 );
				}
				ftp_upload = 0; //Added by TF Team 08-07
            }
			if(data.upload_enable)
			{
				//Show the upload buttons.
				$('#upload_button').show();
			}
			else
			{
				//Hide the upload buttons.
				$('#upload_button').hide();
			}

			if(data.internet_status  === "dis") {
                document.getElementById("internet_status").innerHTML = "Internet Disconnected";
                $('#update_button').hide();
			} else if(data.internet_status  === "con") {
                document.getElementById("internet_status").innerHTML = "Internet Connected";
                $('#update_button').show();
			} else {
                document.getElementById("internet_status").innerHTML = "Internet Status Undefined";
                $('#update_button').hide();
			}
			
			//TODO: When the 'upload' button has been clicked, then start looking at this!
			if(upload_requested) {
				if(data.loc_upload_status == true) {
					/* $('#upload_status_wait').show(); */	//Commented by TF2- Since a Dialog Box is used to inform Update in Progress - Bug 870
					$('#upload_wait').show();
					$('#upload_status_done').hide();
					Upload_message();						//Added by TF2 - Opens the Dialog Box while uploading - Bug 870
				}
				if(data.loc_upload_status == false) {
					/* $('#upload_status_wait').hide(); */	//Commented by TF2 - Since we commented show, Hide is not required - Bug 870
					$('#upload_wait').hide();
					Unload_message();						//Added by TF2 - Closes the Dialog Box after upload finishes - Bug 870
					$('#upload_status_done').show();
				}
			} else {
				//$('#upload_status_wait').hide(); //Commented by TF2 - Since we commented show, Hide is not required - Bug 870
				$('#upload_status_done').hide();
				$('#upload_wait').hide();
			}
        }
    });
}
setInterval(function () {
    loadXMLDoc();
}, 2500);

hide_service_tab();

function service_load() {
    trace('Service Load Start');
    $.ajax({
        type: "GET",
        url: "values.cgi",
        data: {},
        dataType: "JSON",
        cache: false,
        success: function (data) {
            hide_things = data.hide_all;
            if (hide_things) {
				// removing control.html functionality until release 2
				
				if(data.shower_on || data.steam_running)    //Added steam_running by TF Team 10-07
				{
					location.href = "control.html";
				}
                if (data.num_interface !== 0) {
                    //If there are no interfaces, there is no control
                    
                    if(!(data.rainpanel_installed 
                        || data.bridge_installed 
                        || data.amp_installed
                        || data.steam_installed
                        || data.valve1_installed
                        || data.valve2_installed
                        || data.music_installed ) )
                        {
                            $('#control_div').hide();
                            $('#control-tab').hide();
                        }
						else
						{
                            $('#control_div').show();
                            $('#control-tab').show();
                        }
                } else {
                    $('#control-tab').hide();
                }
				
                //diagnostics tab load
                if (data.ui1_con_string !== "not_seen") {
                    $('#amulet_con').html(data.ui1_con_string === "dis" ? discon_string : con_string);
                    $('#int1_con_div').show();
                } else {
                    $('#int1_con_div').hide();
                }
                if (data.ui2_con_string !== "not_seen") {
                    $('#coproc_con').html(data.ui2_con_string === "dis" ? discon_string : con_string);
                    $('#int2_con_div').show();
                } else {
                    $('#int2_con_div').hide();
                }
                if (data.ui3_con_string !== "not_seen") {
                    $('#lang_con').html(data.ui3_con_string === "dis" ? discon_string : con_string);
                    $('#int3_con_div').show();
                } else {
                    $('#int3_con_div').hide();
                }
                $('#controller_con').html(data.controller_con_string === "dis" ? discon_string : con_string);

				/************************************************************/
				if(data.valve_1_con_string == "intermittent")
				{
					$('#valve1_con').html(intermittent_string);
					$('#valve1_con_div').show();
				}
				else if (data.valve_1_con_string !== "not_seen") 
                {
                    $('#valve1_con').html(data.valve_1_con_string === "dis" ? discon_string : con_string);
                    $('#valve1_con_div').show();
                } else {
                    $('#valve1_con_div').hide();
                }
				
				if(data.valve_2_con_string == "intermittent")
				{
					$('#valve2_con').html(intermittent_string);
					$('#valve2_con_div').show();
				}
				else if (data.valve_2_con_string !== "not_seen") {
                    $('#valve2_con').html(data.valve_2_con_string === "dis" ? discon_string : con_string);
                    $('#valve2_con_div').show();
                } else {
                    $('#valve2_con_div').hide();
                }
				
				if(data.music_module_con_string == "intermittent")
				{
					$('#music_con').html(intermittent_string);
					$('#music_con_div').show();
				}
				else if (data.music_module_con_string !== "not_seen") {
                    $('#music_con').html(data.music_module_con_string === "dis" ? discon_string : con_string);
                    $('#music_con_div').show();
                } else {
                    $('#music_con_div').hide();
                }
				
				
				 if(data.lighting_con_string == "intermittent")
				{
					$('#lighting_con').html(intermittent_string);
					$('#light_con_div').show();
				}
				else if (data.lighting_con_string !== "not_seen") {
                    $('#lighting_con').html(data.lighting_con_string === "dis" ? discon_string : con_string);
                    $('#light_con_div').show();
                } else {
                    $('#light_con_div').hide();
                }
				
				 if(data.steam_con_string == "intermittent")
				{
					$('#steam_con').html(intermittent_string);
					$('#steam_con_div').show();
				}
				 else if (data.steam_con_string !== "not_seen") {
                    $('#steam_con').html(data.steam_con_string === "dis" ? discon_string : con_string);
                    $('#steam_con_div').show();
                } else {
                    $('#steam_con_div').hide();
                }
				
				if(data.amp_con_string == "intermittent")
				{
					$('#amp_con').html(intermittent_string);
					$('#amp_con_div').show();
				}
				else if (data.amp_con_string !== "not_seen") {
                    $('#amp_con').html(data.amp_con_string === "dis" ? discon_string : con_string);
                    $('#amp_con_div').show();
                } else {
                    $('#amp_con_div').hide();
                }
				
				
				if(data.watertile_con_string == "intermittent")
				{
					$('#watertile_con').html(intermittent_string);
					$('#rain_con_div').show();
				}
				else if (data.watertile_con_string !== "not_seen") {
                    $('#watertile_con').html(data.watertile_con_string === "dis" ? discon_string : con_string);
                    $('#rain_con_div').show();
                } else {
                    $('#rain_con_div').hide();
                }
				
				
				if(data.watertile2_con_string == "intermittent")
				{
					$('#watertile2_con').html(intermittent_string);
					$('#rain2_con_div').show();
				}
				else if (data.watertile2_con_string !== "not_seen") {
                    $('#watertile2_con').html(data.watertile2_con_string === "dis" ? discon_string : con_string);
                    $('#rain2_con_div').show();
                } else {
                    $('#rain2_con_div').hide();
                }
				/*************************************************************/
				
				
				/*
				
                if (data.valve_1_con_string !== "not_seen") 
                {
                    $('#valve1_con').html(data.valve_1_con_string === "dis" ? discon_string : con_string);
                    $('#valve1_con_div').show();
                } else {
                    $('#valve1_con_div').hide();
                }
                if (data.valve_2_con_string !== "not_seen") {
                    $('#valve2_con').html(data.valve_2_con_string === "dis" ? discon_string : con_string);
                    $('#valve2_con_div').show();
                } else {
                    $('#valve2_con_div').hide();
                }
                $('#controller_con').html(data.controller_con_string === "dis" ? discon_string : con_string);
                if (data.music_module_con_string !== "not_seen") {
                    $('#music_con').html(data.music_module_con_string === "dis" ? discon_string : con_string);
                    $('#music_con_div').show();
                } else {
                    $('#music_con_div').hide();
                }
                if (data.lighting_con_string !== "not_seen") {
                    $('#lighting_con').html(data.lighting_con_string === "dis" ? discon_string : con_string);
                    $('#light_con_div').show();
                } else {
                    $('#light_con_div').hide();
                }
                if (data.steam_con_string !== "not_seen") {
                    $('#steam_con').html(data.steam_con_string === "dis" ? discon_string : con_string);
                    $('#steam_con_div').show();
                } else {
                    $('#steam_con_div').hide();
                }
                if (data.amp_con_string !== "not_seen") {
                    $('#amp_con').html(data.amp_con_string === "dis" ? discon_string : con_string);
                    $('#amp_con_div').show();
                } else {
                    $('#amp_con_div').hide();
                }
                if (data.watertile_con_string !== "not_seen") {
                    $('#watertile_con').html(data.watertile_con_string === "dis" ? discon_string : con_string);
                    $('#rain_con_div').show();
                } else {
                    $('#rain_con_div').hide();
                }
				*/
				/*Add by TF2 March*20*2015 - Bug 967, To show/hide second watertile rain panel*/
				/*
				if (data.watertile2_con_string !== "not_seen") {
                    $('#watertile2_con').html(data.watertile2_con_string === "dis" ? discon_string : con_string);
                    $('#rain2_con_div').show();
                } else {
                    $('#rain2_con_div').hide();
                }
				*/
				/*End of Add by TF2 March*20*2015 - Bug 967*/ 
				
				if (data.num_outlets === 6 || data.v2_num_outlets === 6) {
					$('#calibration_codes').show();
				} else {
					//There are no six ports, so don't show 'six port valve service'
					$('#calibration_codes').hide();
				}
				
				if (data.num_outlets === 6) {
					$('#sixport_calibration_1').show();
					document.getElementById('valve1_code').value = data.v1_cal_code;
				} else {
					$('#sixport_calibration_1').hide();
					document.getElementById('valve1_code').value = "";
				}
				
				if (data.v2_num_outlets === 6) {
					$('#sixport_calibration_2').show();
					document.getElementById('valve2_code').value = data.v2_cal_code;
				} else {
					$('#sixport_calibration_2').hide();
					document.getElementById('valve2_code').value = "";
				}
				
				document.getElementById('valve1_cal_err').style.display = 'none';
				document.getElementById('valve2_cal_err').style.display = 'none';			
				
				if(data.upload_enable)
				{
					//Show the upload buttons.
					$('#upload_button').show(); 
				}
				else
				{
					//Hide the upload buttons.
					$('#upload_button').hide();
				}

				if(data.const_hospitality!="")
				{
				    document.getElementById("hospitality_code").value = data.const_hospitality;
				} else {
					document.getElementById("hospitality_code").value = "";					
				}
				
				if(data.saved_defaults) {
					$("#reset_default").show();
					$("#reset_title").show();
				} else {
					$("#reset_default").hide();
					$("#reset_title").hide();
				}
								
				$('#upload_status_wait').hide();
				$('#upload_status_done').hide();
				$('#upload_wait').hide();
				upload_requested = false;
            }
        }
    });
}

function validate_hospitality(evt) {
  var theEvent = evt || window.event;
  var key = theEvent.keyCode || theEvent.which;

  //allow backspace key
  if (key == 8) { 
    return;
  }

  key = String.fromCharCode( key );
  var regex = /^[A-Za-z0-9]+$/;
  if( !regex.test(key) ) {
    theEvent.returnValue = false;
    if(theEvent.preventDefault) {	
	  theEvent.preventDefault();
	}
  }
}

function language() {
    trace('Languages');
    //<%languages%>
    var words;
    $.ajax({
        type: "GET",
        url: "languages.cgi",
        data: {},
        dataType: "JSON",
        cache: false,
        success: function (data) {
            words = data;
            discon_string = words.discon_string;
            con_string = words.con_string;
            user_title = words.user_title;
            //main page text
            none_text = words.noneText;
            config_a = words.conA;
            config_a_1 = words.conAAlt1;
            config_a_2 = words.conAAlt2;
            config_a_3 = words.conAAlt3;
            config_b = words.conB;
            config_b_1 = words.conBAlt1;
            config_b_2 = words.conBAlt2;
            config_b_3 = words.conBAlt3;
            config_c = words.conC;
            config_d = words.conD;
            config_d_1 = words.conDAlt1;
            config_d_2 = words.conDAlt2;
            config_d_3 = words.conDAlt3;
            config_unwind = words.conCUnwind;
            config_downpour = words.conCDownpour;
            config_frontage = words.conCFrontage;
            config_surround = words.conCSurround;
            config_linear = words.conCLinear;
            config_envelop = words.conCEnvelop;
            $("#interface1_beep option").eq(0).text(words.silent_text);
            $("#interface1_beep option").eq(1).text(words.quiet_text);
            $("#interface1_beep option").eq(2).text(words.loud_text);
            $("#interface2_beep option").eq(0).text(words.silent_text);
            $("#interface2_beep option").eq(1).text(words.quiet_text);
            $("#interface2_beep option").eq(2).text(words.loud_text);
            $("#interface3_beep option").eq(0).text(words.silent_text);
            $("#interface3_beep option").eq(1).text(words.quiet_text);
            $("#interface3_beep option").eq(2).text(words.loud_text);
            $("#interface1_auto_dim option").eq(0).text(words.off_word_text);
            $("#interface1_auto_dim option").eq(1).text(words.one_minute_text);
            $("#interface1_auto_dim option").eq(2).text(words.five_minute_text);
            $("#interface2_auto_dim option").eq(0).text(words.off_word_text);
            $("#interface2_auto_dim option").eq(1).text(words.one_minute_text);
            $("#interface2_auto_dim option").eq(2).text(words.five_minute_text);
            $("#interface3_auto_dim option").eq(0).text(words.off_word_text);
            $("#interface3_auto_dim option").eq(1).text(words.one_minute_text);
            $("#interface3_auto_dim option").eq(2).text(words.five_minute_text);
            $("#interface1_start_screen option").eq(0).text(words.home_text);
            $("#interface1_start_screen option").eq(1).text(words.quick_text);
            $("#interface1_start_screen option").eq(2).text(words.users_text);
            $("#interface1_start_screen option").eq(3).text(words.valve1_text);
            $("#interface1_start_screen option").eq(4).text(words.valve2_text);
            $("#interface1_start_screen option").eq(5).text(words.music_text);
            $("#interface1_start_screen option").eq(6).text(words.lighting_text);
            $("#interface2_start_screen option").eq(0).text(words.home_text);
            $("#interface2_start_screen option").eq(1).text(words.quick_text);
            $("#interface2_start_screen option").eq(2).text(words.users_text);
            $("#interface2_start_screen option").eq(3).text(words.valve1_text);
            $("#interface2_start_screen option").eq(4).text(words.valve2_text);
            $("#interface2_start_screen option").eq(5).text(words.music_text);
            $("#interface2_start_screen option").eq(6).text(words.lighting_text);
            $("#interface3_start_screen option").eq(0).text(words.home_text);
            $("#interface3_start_screen option").eq(1).text(words.quick_text);
            $("#interface3_start_screen option").eq(2).text(words.users_text);
            $("#interface3_start_screen option").eq(3).text(words.valve1_text);
            $("#interface3_start_screen option").eq(4).text(words.valve2_text);
            $("#interface3_start_screen option").eq(5).text(words.music_text);
            $("#interface3_start_screen option").eq(6).text(words.lighting_text);
            //selects
            $("#effect_speed_select option").eq(0).text(words.slow_text);
            $("#effect_speed_select option").eq(1).text(words.medium_text);
            $("#effect_speed_select option").eq(2).text(words.fast_text);
            $("#white_color_select option").eq(0).text(words.warm_text);
            $("#white_color_select option").eq(1).text(words.neutral_text);
            $("#white_color_select option").eq(2).text(words.cool_text);
            $("#fade_speed_select option").eq(0).text(words.slow_text);
            $("#fade_speed_select option").eq(1).text(words.medium_text);
            $("#fade_speed_select option").eq(2).text(words.fast_text);
            $("#fade_1 option").eq(0).text(words.noneText);
            $("#fade_1 option").eq(1).text(words.slow_text);
            $("#fade_1 option").eq(2).text(words.medium_text);
            $("#fade_1 option").eq(3).text(words.fast_text);
            $("#fade_2 option").eq(0).text(words.noneText);
            $("#fade_2 option").eq(1).text(words.slow_text);
            $("#fade_2 option").eq(2).text(words.medium_text);
            $("#fade_2 option").eq(3).text(words.fast_text);
            $("#fade_3 option").eq(0).text(words.noneText);
            $("#fade_3 option").eq(1).text(words.slow_text);
            $("#fade_3 option").eq(2).text(words.medium_text);
            $("#fade_3 option").eq(3).text(words.fast_text);
            //music text 
            $("#music_repeat_select option").eq(0).text(words.all_word_string);
            $("#music_repeat_select option").eq(1).text(words.one_word_string);
            //system text 
            $("#lang option").eq(0).text(words.eng_lang_text);
            $("#lang option").eq(1).text(words.ara_lang_text);
            $("#lang option").eq(2).text(words.schi_lang_text);
            $("#lang option").eq(3).text(words.mchi_lang_text);
            $("#lang option").eq(4).text(words.brit_lang_text);
            $("#lang option").eq(5).text(words.ger_lang_text);
            $("#lang option").eq(6).text(words.ita_lang_text);
            $("#lang option").eq(7).text(words.jap_lang_text);
            $("#lang option").eq(8).text(words.kor_lang_text);
            $("#lang option").eq(9).text(words.por_lang_text);
            $("#lang option").eq(10).text(words.rus_lang_text);
            $("#lang option").eq(11).text(words.tha_lang_text);
            $("#lang option").eq(12).text(words.fre_lang_text);
            $("#lang option").eq(13).text(words.spa_lang_text);
            $("#contact_2_open option").eq(0).text(words.noneText);
            $("#contact_2_open option").eq(1).text(words.turn_shower_on_text);
            $("#contact_2_open option").eq(2).text(words.shower_off_text);
            $("#contact_2_open option").eq(3).text(words.turn_everything_off_text);
            $("#contact_2_open option").eq(4).text(words.preset_1_text);
            $("#contact_2_open option").eq(5).text(words.preset_2_text);
            $("#contact_2_open option").eq(6).text(words.preset_3_text);
            $("#contact_2_open option").eq(7).text(words.preset_4_text);
            $("#contact_2_open option").eq(8).text(words.preset_5_text);
            $("#contact_2_open option").eq(9).text(words.preset_6_text);
            $("#contact_1_open option").eq(0).text(words.noneText);
            $("#contact_1_open option").eq(1).text(words.turn_shower_on_text);
            $("#contact_1_open option").eq(2).text(words.shower_off_text);
            $("#contact_1_open option").eq(3).text(words.turn_everything_off_text);
            $("#contact_1_open option").eq(4).text(words.preset_1_text);
            $("#contact_1_open option").eq(5).text(words.preset_2_text);
            $("#contact_1_open option").eq(6).text(words.preset_3_text);
            $("#contact_1_open option").eq(7).text(words.preset_4_text);
            $("#contact_1_open option").eq(8).text(words.preset_5_text);
            $("#contact_1_open option").eq(9).text(words.preset_6_text);
            $("#contact_2_closed option").eq(0).text(words.noneText);
            $("#contact_2_closed option").eq(1).text(words.turn_shower_on_text);
            $("#contact_2_closed option").eq(2).text(words.shower_off_text);
            $("#contact_2_closed option").eq(3).text(words.turn_everything_off_text);
            $("#contact_2_closed option").eq(4).text(words.preset_1_text);
            $("#contact_2_closed option").eq(5).text(words.preset_2_text);
            $("#contact_2_closed option").eq(6).text(words.preset_3_text);
            $("#contact_2_closed option").eq(7).text(words.preset_4_text);
            $("#contact_2_closed option").eq(8).text(words.preset_5_text);
            $("#contact_2_closed option").eq(9).text(words.preset_6_text);
            $("#contact_1_closed option").eq(0).text(words.noneText);
            $("#contact_1_closed option").eq(1).text(words.turn_shower_on_text);
            $("#contact_1_closed option").eq(2).text(words.shower_off_text);
            $("#contact_1_closed option").eq(3).text(words.turn_everything_off_text);
            $("#contact_1_closed option").eq(4).text(words.preset_1_text);
            $("#contact_1_closed option").eq(5).text(words.preset_2_text);
            $("#contact_1_closed option").eq(6).text(words.preset_3_text);
            $("#contact_1_closed option").eq(7).text(words.preset_4_text);
            $("#contact_1_closed option").eq(8).text(words.preset_5_text);
            $("#contact_1_closed option").eq(9).text(words.preset_6_text);
            $("#relay2_on_trigger option").eq(0).text(words.noneText);
            $("#relay2_on_trigger option").eq(1).text(words.contact_1_close_text);
            $("#relay2_on_trigger option").eq(2).text(words.contact_1_open_text);
            $("#relay2_on_trigger option").eq(3).text(words.contact_2_close_text);
            $("#relay2_on_trigger option").eq(4).text(words.contact_2_open_text);
            $("#relay2_on_trigger option").eq(5).text(words.shower_on_text);
            $("#relay2_on_trigger option").eq(6).text(words.shower_off_text);
            $("#relay2_on_trigger option").eq(7).text(words.anything_on_text);
            $("#relay2_on_trigger option").eq(8).text(words.everything_off_text);
            $("#relay1_on_trigger option").eq(0).text(words.noneText);
            $("#relay1_on_trigger option").eq(1).text(words.contact_1_close_text);
            $("#relay1_on_trigger option").eq(2).text(words.contact_1_open_text);
            $("#relay1_on_trigger option").eq(3).text(words.contact_2_close_text);
            $("#relay1_on_trigger option").eq(4).text(words.contact_2_open_text);
            $("#relay1_on_trigger option").eq(5).text(words.shower_on_text);
            $("#relay1_on_trigger option").eq(6).text(words.shower_off_text);
            $("#relay1_on_trigger option").eq(7).text(words.anything_on_text);
            $("#relay1_on_trigger option").eq(8).text(words.everything_off_text);
            $("#relay2_off_trigger option").eq(0).text(words.noneText);
            $("#relay2_off_trigger option").eq(1).text(words.contact_1_close_text);
            $("#relay2_off_trigger option").eq(2).text(words.contact_1_open_text);
            $("#relay2_off_trigger option").eq(3).text(words.contact_2_close_text);
            $("#relay2_off_trigger option").eq(4).text(words.contact_2_open_text);
            $("#relay2_off_trigger option").eq(5).text(words.shower_on_text);
            $("#relay2_off_trigger option").eq(6).text(words.shower_off_text);
            $("#relay2_off_trigger option").eq(7).text(words.anything_on_text);
            $("#relay2_off_trigger option").eq(8).text(words.everything_off_text);
            $("#relay1_off_trigger option").eq(0).text(words.noneText);
            $("#relay1_off_trigger option").eq(1).text(words.contact_1_close_text);
            $("#relay1_off_trigger option").eq(2).text(words.contact_1_open_text);
            $("#relay1_off_trigger option").eq(3).text(words.contact_2_close_text);
            $("#relay1_off_trigger option").eq(4).text(words.contact_2_open_text);
            $("#relay1_off_trigger option").eq(5).text(words.shower_on_text);
            $("#relay1_off_trigger option").eq(6).text(words.shower_off_text);
            $("#relay1_off_trigger option").eq(7).text(words.anything_on_text);
            $("#relay1_off_trigger option").eq(8).text(words.everything_off_text);
            //TODO: button
            $('#save_current').val(words.save_current_text);
            //update text
            $('#select_file_btn').val(words.select_file_string);
            $('#update_button').val(words.update_string);
            $('.startButton').val(words.startText);
            $('.stopButton').val(words.stopText);
            $('.offButton').val(words.offText);
            $('.onButton').val(words.onText);
            $("#valve1_outlet_0_ramp option").eq(0).text(words.low_text);
            $("#valve1_outlet_0_ramp option").eq(1).text(words.medium_text);
            $("#valve1_outlet_0_ramp option").eq(2).text(words.high_text);
            $("#valve1_outlet_1_ramp option").eq(0).text(words.low_text);
            $("#valve1_outlet_1_ramp option").eq(1).text(words.medium_text);
            $("#valve1_outlet_1_ramp option").eq(2).text(words.high_text);
            $("#valve1_outlet_2_ramp option").eq(0).text(words.low_text);
            $("#valve1_outlet_2_ramp option").eq(1).text(words.medium_text);
            $("#valve1_outlet_2_ramp option").eq(2).text(words.high_text);
            $("#valve2_outlet_0_ramp option").eq(0).text(words.low_text);
            $("#valve2_outlet_0_ramp option").eq(1).text(words.medium_text);
            $("#valve2_outlet_0_ramp option").eq(2).text(words.high_text);
            $("#valve2_outlet_1_ramp option").eq(0).text(words.low_text);
            $("#valve2_outlet_1_ramp option").eq(1).text(words.medium_text);
            $("#valve2_outlet_1_ramp option").eq(2).text(words.high_text);
            $("#valve2_outlet_2_ramp option").eq(0).text(words.low_text);
            $("#valve2_outlet_2_ramp option").eq(1).text(words.medium_text);
            $("#valve2_outlet_2_ramp option").eq(2).text(words.high_text);
            $("#valve1_outlet_0_flow option").eq(0).text(words.slow_text);
            $("#valve1_outlet_0_flow option").eq(1).text(words.medium_text);
            $("#valve1_outlet_0_flow option").eq(2).text(words.high_text);
            $("#valve1_outlet_1_flow option").eq(0).text(words.slow_text);
            $("#valve1_outlet_1_flow option").eq(1).text(words.medium_text);
            $("#valve1_outlet_1_flow option").eq(2).text(words.high_text);
            $("#valve1_outlet_2_flow option").eq(0).text(words.slow_text);
            $("#valve1_outlet_2_flow option").eq(1).text(words.medium_text);
            $("#valve1_outlet_2_flow option").eq(2).text(words.high_text);
            $("#valve2_outlet_0_flow option").eq(0).text(words.slow_text);
            $("#valve2_outlet_0_flow option").eq(1).text(words.medium_text);
            $("#valve2_outlet_0_flow option").eq(2).text(words.high_text);
            $("#valve2_outlet_1_flow option").eq(0).text(words.slow_text);
            $("#valve2_outlet_1_flow option").eq(1).text(words.medium_text);
            $("#valve2_outlet_1_flow option").eq(2).text(words.high_text);
            $("#valve2_outlet_2_flow option").eq(0).text(words.slow_text);
            $("#valve2_outlet_2_flow option").eq(1).text(words.medium_text);
            $("#valve2_outlet_2_flow option").eq(2).text(words.high_text);
            $("#massage_select_1 option").eq(0).text(words.noneText);
            $("#massage_select_1 option").eq(1).text(words.waveText);
            $("#massage_select_1 option").eq(2).text(words.singleText);
            $("#massage_select_1 option").eq(3).text(words.customText);
            $("#massage_select_2 option").eq(0).text(words.noneText);
            $("#massage_select_2 option").eq(1).text(words.waveText);
            $("#massage_select_2 option").eq(2).text(words.singleText);
            $("#massage_select_2 option").eq(3).text(words.customText);
            $("#chroma_experience option").eq(0).text(words.colorCycleExpText);
            $("#chroma_experience option").eq(1).text(words.warmExpText);
            $("#chroma_experience option").eq(2).text(words.CoolExpText);
            $("#chroma_experience option").eq(3).text(words.riseExptext);
            $("#chroma_experience option").eq(4).text(words.setExptext);
            $("#chroma_experience option").eq(5).text(words.cloudsExptext);
            $("#chroma_experience option").eq(6).text(words.relfectExptext);
            $("#chroma_experience option").eq(7).text(words.thunderExptext);
            //$("#chroma_color option").eq(0).text(words.dialChroText);
            $("#chroma_color option").eq(0).text(words.redChroText);
            $("#chroma_color option").eq(30).text(words.orangeChroText);
            $("#chroma_color option").eq(60).text(words.yelChroText);
            $("#chroma_color option").eq(115).text(words.greChroText);
            $("#chroma_color option").eq(235).text(words.blueChroText);
            $("#chroma_color option").eq(305).text(words.purpleChroText);
            $("#chroma_color option").eq(270).text(words.violetChroText);
            $("#chroma_color option").eq(330).text(words.pinkChroText);
            $("#chroma_color option").eq(-1).text(words.whiteChroText);
            $('.new_light_modual').val(words.new_light_modual_text);
            $('.del_light_modual').val(words.del_light_modual_text);
            $('.clear_users').val(words.clear_users_text);
            $('.reset_system_button').val(words.reset_system_button);
            $('.reset_users_button').val(words.reset_users_button);
            $('.reset_default_button').val(words.reset_default_button);
			$('.cal_code_err_string').val(words.cal_code_err_string);
			$('.reset_string').val(words.reset_string);
			$('.networkTabString').val(words.networkTabString);
			$('.controller_ip_string').val(words.controller_ip_string);
			$('.controller_gateway_string').val(words.controller_gateway_string);
			$('.controller_mac_string').val(words.controller_mac_string);
            
            $('#upload_string').val(words.upload_string);
            $.each(data, function (key, val) {
                if(key!=="")
                {
                    try {
                        $('.' + key).html(val);
                    } catch (e) {
                        trace('Language Error: ' + key + ' ' + val + ' ' + e.message);
                    }
                }
            });
        }
    });
}
function reset_fault_logs() //Added by Tf-team on 09-10-2015 for clearing fault logs in 
{
	$.get("reset_fault.cgi",
	{
	},
	function(data, textStatus)
	{
			////alert("Response from server: " + data);
	});
}

function hide_service_tab() {
    trace('hide Load Start');
	//CORYO - Don't allow control to load for phase 1 - jump to settings.
	//location.href = "settings.html";
	
    $.ajax({
        type: "GET",
        url: "system_info.cgi",
        data: {},
        dataType: "JSON",
        cache: false,
       success: function (data) {
		if(data.devices_running == true) {    //Added steam_running by TF Team 10-07
	    	    	location.href = "control.html";
				}				
	   }
	});
	setTimeout(function () {
                hide_service_tab();
    	    }, 1200);
}

//Added By TF2 for power clean pop up - TF2*March 2nd 2015 - Bug 279
/* *********************************************************************************************************************** */
function Upload_powerclean_message() {
	$('#dialog-steam-powerclean').dialog({
		closeOnEscape: false,
		height: "auto !important",
		width: "auto !important",
		resizable: false,
		modal: true,
		draggable: false,
		dialogClass: 'main-dialog-class',
	});
}

function Unload_powerclean_message() {
	$('#dialog-steam-powerclean').dialog("close");
}

function powerclean_check_load() {
	$.ajax({
			type: "GET",
			url: "powerclean_check.cgi",
			data: {},
			dataType: "JSON",
			cache: false,
			
			success: function (data) {
			
				if(data.powerclean == 1)
				{
					$('#dialog-steam-powerclean').dialog({
						closeOnEscape: false,
						height: "auto !important",
						width: "auto !important",
						resizable: false,
						modal: true,
						draggable: false,
						dialogClass: 'main-dialog-class',
					});
					powerclean_On = 1; //TF Team 07-07
				}
				else if((data.powerclean == 0) && (powerclean_On == 1)) //TF Team 07-07
				{
					$('#dialog-steam-powerclean').dialog("close");
					powerclean_On = 0; //TF Team 07-07
				}
        	}
		});	
			setTimeout(function () {
            powerclean_check_load();
            }, 1000);
	
}
/* *********************************************************************************************************************** */
//End of Add by TF2 - TF2*March 2nd 2015 - Bug 279 - Power clean pop up