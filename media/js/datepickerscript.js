
// put the handlers on the elements to be clicked	
$("#calendar_view").click(function(e) {
	e.preventDefault();
	change_view(false);
});

$("#list_view").click(function(e) {
	e.preventDefault();
	change_view(true);
});

$('a[href$="PreviousYear"]').click(function(e) {
	alert("clicked prev year");
});

function change_view(list_view) {
	// Change the view between calendar view and list view.
	// Default is list view.
	var start_date = start.datepicker("getDate");
	var end_date = end.datepicker("getDate");
	
	// need to add one to month because ?
	start_date.setMonth(start_date.getMonth()+1);
	end_date.setMonth(end_date.getMonth()+1);
	
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


	url = "http://{{ city_site.domain }}/";
	new_loc = "?" + "list_view=" + list_view + "&" + "start=" + start_date.getMonth() + "-" + start_date.getDate() + "-" + start_date.getFullYear() + "&" + "end=" + end_date.getMonth() + "-" + end_date.getDate() + "-" + end_date.getFullYear();
	alert("new_loc is " + new_loc);
	$("#load_image").fadeIn("fast");
	$("#reading_list").fadeOut("fast");
	$("#reading_list").load(new_loc + " #reading_list", function() {
		// callback function
		$("#load_image").fadeOut("fast");
	}); // pull data using ajax
	$("#reading_list").fadeIn("fast");

	// now change the controls to reflect the new view
	if(list_view) {
		// changing to list view
		// first, hide the calendar controls
		$(".calendar_controls").fadeOut("fast", function() {
			// now get the full month of data for the calendar
			
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

$("#next_week").click(function(e) {
	// if 
	e.preventDefault();
	var today = new Date();
	var one_week = new Date(today.getTime()+1000*60*60*24*7);
	start.datepicker("setDate", today);
	end.datepicker("setDate", one_week);
	setNewDate(start.datepicker("getDate"), end.datepicker("getDate"));
});

$("#next_month").click(function(e) {
	e.preventDefault();
	var today = new Date();
	var one_week = new Date(today.getTime()+1000*60*60*24*31);
	start.datepicker("setDate", today);
	end.datepicker("setDate", one_week);
	setNewDate(start.datepicker("getDate"), end.datepicker("getDate"));
});

var start = $( "#datepicker_start" ).datepicker({
	autoSize: true,
	onSelect: change_start 
});

var end = $( "#datepicker_end" ).datepicker({
	autoSize: true,
	onSelect: change_end
});

function change_start(dateText, inst) {
	// first make sure the dates make sense
	validate_start(dateText, inst);
	var start_date = start.datepicker("getDate");
	var end_date = end.datepicker("getDate");
	start_date.setMonth(start_date.getMonth()+1);
	end_date.setMonth(end_Date.getMonth()+1);
	
	setNewDate(start_date, end_date);	
}

function change_end(dateText, inst) {
	
	validate_end(dateText, inst);
	var start_date = start.datepicker("getDate");
	var end_date = end.datepicker("getDate");
	start_date.setMonth(start_date.getMonth()+1);
	end_date.setMonth(end_date.getMonth()+1);
	
	setNewDate(start_date, end_date);
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

function setNewDate(start_date, end_date) {
	url = "http://{{ city_site.domain }}/";
	new_loc = "?" + "start=" + start_date.getMonth() + "-" + start_date.getDate() + "-" + start_date.getFullYear() + "&" + "end=" + end_date.getMonth() + "-" + end_date.getDate() + "-" + end_date.getFullYear();
	//window.location.href = new_loc; // reload page--a way of doing this without using ajax
	$("#reading_list").load(new_loc + " #reading_list"); // pull data using ajax
}