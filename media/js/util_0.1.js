/* util.js
 * -------
 * Helpful functions.
 * Version 0.1
 */ 

/*
 * Some initial UI stuff to take care of.
 */
var start;
var end;
$(document).ready(function() {

	// Only show the city chooser submit buttom if js is not enabled
	$("input.city_chooser").hide(); 

	// Change the city_site automatically.
	$("#choose_city").change(function(e) {
		e.preventDefault();
		window.location.href = "http://" + e.target.value;

	});
	
	// Javascript's setMonth and getMonth are 0-indexed

	// Set the dates for the datepicker
	start = $( "#datepicker_start" ).datepicker({
		autoSize: false,
		onSelect: change_start_list_view 
	});

	end = $( "#datepicker_end" ).datepicker({
		autoSize: false,
		onSelect: change_end_list_view
	});
	
	if(start.length && end.length) {
		start.datepicker("setDate", start_date);
		end.datepicker("setDate", end_date);
	}
	
	// put the handlers on the buttons to be clicked, and prevent them from
	// the default action, submitting the form. If js is disabled, they will 
	// submit the form so the page still works, albeit without the nice
	// UI elements.
	$("#calendar_view").click(function(e) {
		e.preventDefault();
		change_view(false);
	});
	
	$("#list_view").click(function(e) {
		e.preventDefault();
		change_view(true);
	});

	// Calendar view controls
	$('a[href$="CalPreviousYear"]').click(function(e) {
		e.preventDefault();
		var start_date = start.datepicker("getDate");
		start_date.setYear(start_date.getFullYear()-1);
		var end_date = new Date(start_date.getFullYear(), start_date.getMonth()+1, 1, 0, 0, 0);

		loadReadingList(start_date, end_date, false);	
	});

	$('a[href$="CalPreviousMonth"]').click(function(e) {
		e.preventDefault();
		var start_date = start.datepicker("getDate");
		start_date.setMonth(start_date.getMonth()-1);
		var end_date = new Date(start_date.getFullYear(), start_date.getMonth()+1, 1, 0, 0, 0);

		loadReadingList(start_date, end_date, false);	
	});

	$('a[href$="CalNextMonth"]').click(function(e) {
		e.preventDefault();
		var start_date = start.datepicker("getDate");
		start_date.setMonth(start_date.getMonth()+1);
		var end_date = new Date(start_date.getFullYear(), start_date.getMonth()+1, 1, 0, 0, 0);

		loadReadingList(start_date, end_date, false);	
	});

	$('a[href$="CalNextYear"]').click(function(e) {
		e.preventDefault();
		var start_date = start.datepicker("getDate");
		start_date.setYear(start_date.getFullYear()+1);
		var end_date = new Date(start_date.getFullYear(), start_date.getMonth()+1, 1, 0, 0, 0);

		loadReadingList(start_date, end_date, false);	
	});
	
	// List controls 
	$("#one_week").click(function(e) {
		e.preventDefault();
		var today = new Date();
		var one_week = new Date(today.getTime()+1000*60*60*24*7);
		loadReadingList(today, one_week, true);
	});

	$("#one_month").click(function(e) {
		e.preventDefault();
		var today = new Date();
		var one_month = new Date(today.getTime()+1000*60*60*24*31);
		loadReadingList(today, one_month, true);
	});
		
}); // end document.ready()
 
/*
 * Include the CSRF token for ajax requests.
 */
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

/*
 * Bind any editable elements to inlineEdit.
 */
function bind_editable_descriptions(url) {
	// this has to run when the document is ready the first time, and also
	// every time a page loads new data via ajax
	$(".edit_reading_description").inlineEdit({
		buttonText: 'Update',
		placeholder: 'Add details about this reading.',
	    save: function(e, data) {
			$.ajax({
				type: 'POST',
				url: url,
				data: { 'reading_id': this.id, 'description': data.value },
                success: function(data, textStatus, jqXHR) { 
                    var response = $.parseJSON(jqXHR.responseText);
                    $("#" + response.id).text(response.description);                 
                },
				error: function(jqXHR, textStatus, errorThrown) {
				    alert("in error, textSTatus is " + textStatus);
				}
			})
	
	    },
		control: 'textarea',
	});
}

// functions for date/calendar control changing
function change_view(list_view) {
	// Change the view between calendar view and list view.
	// Default is list view.

	var start_date = start.datepicker("getDate");
	var end_date = end.datepicker("getDate");
		
	if(!list_view) {
		// was list view, now changing to calendar view
		// for calendar view, need to start at the beginning of the month, so day is always 1
		
		var start_month = start_date.getMonth(); 
		var start_year = start_date.getFullYear();
		var start_date = new Date(start_year, start_month, 1, 0, 0, 0);
		if(start_month == 2) {
			end_day = 28;		
		} else if(start_month == 1 || start_month == 3 || start_month == 5 || start_month == 7 || start_month == 8 || start_month == 10 || start_month == 12) {
			end_day = 31;
		}
		else {
			end_day = 30;
		}
		var end_date = new Date(start_year, start_month, end_day, 0, 0, 0);		
	}

	loadReadingList(start_date, end_date, list_view);
	
	// now change the controls to reflect the new view
	if(list_view) {
		// changing to list view
		// first, hide the calendar controls
		$(".calendar_controls").fadeOut("fast", function() {
			// then, show the list controls
			$(".list_controls").fadeIn("fast");
		});
	}
	else {
		// changing to calendar view
		// first, hide the list controls
		$(".list_controls").fadeOut("fast", function() {
			// then, show the calendar controls
			$(".calendar_controls").fadeIn("fast");				
		});
	}
}

function change_start_list_view(dateText, inst) {
	// first make sure the dates make sense
	validate_start(dateText, inst);
	var start_date = start.datepicker("getDate");
	var end_date = end.datepicker("getDate");
	start_date.setMonth(start_date.getMonth());
	end_date.setMonth(end_date.getMonth());
	
	loadReadingList(start_date, end_date, true);	
}

function change_end_list_view(dateText, inst) {
	
	validate_end(dateText, inst);
	var start_date = start.datepicker("getDate");
	var end_date = end.datepicker("getDate");
	start_date.setMonth(start_date.getMonth());
	end_date.setMonth(end_date.getMonth());
	
	loadReadingList(start_date, end_date, true);
}

function validate_start(dateText, inst) {
	/* need to check if start_date is after end_date.
	if so, then make end_date start_date + 1 day. */
	day_milliseconds = 1000*60*60*24;
	var start_date = start.datepicker("getDate");
	var end_date = end.datepicker("getDate");
	if (start_date > end_date) {
		end.datepicker("setDate", new Date(start_date.getTime()+day_milliseconds))
	}		
}

function validate_end(dateText, inst) {
	/* need to check if end_date is before start_date.
	if so, then make start_date end_date - 1 day. */
	day_milliseconds = 1000*60*60*24;
	var start_date = start.datepicker("getDate");
	var end_date = end.datepicker("getDate");
	if (end_date < start_date) {
		start.datepicker("setDate", new Date(end_date.getTime()-day_milliseconds))
	}		
}

function loadReadingList(start_date, end_date, list_view) {
	// always sync the datepickers with whatever date range we are loading
	start.datepicker("setDate", start_date);
	end.datepicker("setDate", end_date);

	// js's Date object's months are zero-indexed, so add one when passing
	// them to the view
	url = "http://{{ city_site.domain }}/";
	new_loc = "?" +"list_view=" + list_view + "&" + "start=" + (start_date.getMonth()+1) + "-" + start_date.getDate() + "-" + start_date.getFullYear() + "&" + "end=" + (end_date.getMonth()+1) + "-" + end_date.getDate() + "-" + end_date.getFullYear();
	//alert(new_loc);

	var load_image = $("load_image");
	var reading_list = $("#reading_list");
	load_image.fadeIn("fast");
	reading_list.fadeOut("fast");
	$("#reading_list").load(new_loc + " #reading_list", function(response, status, xhr) {
		if(status == "error") {
			var msg = "Sorry, there was an error: ";
		 	$("#messages").append("<p>" + msg + xhr.status + " " + xhr.statusText + "</p>");
			return;
		}
		else {
			load_image.fadeOut("fast");
			reading_list.fadeIn("fast");
		}
		// call the function to make the reading description of the newly
		// pulled readings editable. 
		bind_editable_descriptions();
		
	}
	); // pull data using ajax
	
	if(!list_view) {
		// if calendar view, set the cal_name 
		var month = "January";
		switch(start_date.getMonth()) {
			case 1:
			month = "February";
			break;
			case 2:
			month = "March";
			break;
			case 3:
			month = "April";
			break;
			case 4:
			month = "May";
			break;
			case 5:
			month = "June";
			break;
			case 6:
			month = "July";
			break;
			case 7:
			month = "August";
			break;
			case 8:
			month = "September";
			break;
			case 9:
			month = "October";
			break;
			case 10:
			month = "November";
			break;
			case 11:
			month = "December";
		}
		$("#cal_name").text(month + " " + start_date.getFullYear());
	}
}
