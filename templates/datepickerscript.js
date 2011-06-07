<script type="text/javascript">
$(function() {
	//$( "#tabs" ).tabs();
	
	$("#calendar_view").click(function() {
		change_view(false);
	});
	
	$("#list_view").click(function() {
		change_view(true);
	});
	
	function change_view(list_view) {
		// Change the view between calendar view and list view.
		// Default is list view.
		var start_date = start.datepicker("getDate");
		var end_date = end.datepicker("getDate");
		var start_month = start_date.getMonth()+1;
		var end_month = end_date.getMonth()+1;
		
		url = "http://{{ city_site.domain }}/";
		new_loc = "?" + "list_view=" + list_view + "&" + "start=" + start_month + "-" + start_date.getDate() + "-" + start_date.getFullYear() + "&" + "end=" + end_month + "-" + end_date.getDate() + "-" + end_date.getFullYear();

		$("#reading_list").load(new_loc + " #reading_list"); // pull data using ajax

		// now change the controls to reflect the new view
		if(list_view) {
			// changing to list view
			// first, hide the calendar controls
			$("#calendar_view").slideToggle(false);
			// then, show the list controls
			$("#list_view").slideToggle(true);
		}
		else {
			// changing to calendar view
			// first, hide the list view
			$("#list_view").slideToggle(false);
			// then, show the calendar controls
			$("#calendar_view").slideToggle(true);
		}
	}
	
	$("#next_week").click(function() {
		var today = new Date();
		var one_week = new Date(today.getTime()+1000*60*60*24*7);
		start.datepicker("setDate", today);
		end.datepicker("setDate", one_week);
		setNewDate();
	});

	$("#next_month").click(function() {
		var today = new Date();
		var one_week = new Date(today.getTime()+1000*60*60*24*31);
		start.datepicker("setDate", today);
		end.datepicker("setDate", one_week);
		setNewDate();
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
		setNewDate();
	}

	
	function change_end(dateText, inst) {
		validate_end(dateText, inst);
		setNewDate();
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
	
	function setNewDate() {
		// now go to a new page with this start_time and end_time
		var start_date = start.datepicker("getDate");
		var end_date = end.datepicker("getDate");
		var start_month = start_date.getMonth()+1;
		var end_month = end_date.getMonth()+1;
		url = "http://{{ city_site.domain }}/";
		new_loc = "?" + "start=" + start_month + "-" + start_date.getDate() + "-" + start_date.getFullYear() + "&" + "end=" + end_month + "-" + end_date.getDate() + "-" + end_date.getFullYear();
		//window.location.href = new_loc; // reload page--a way of doing this without using ajax
		$("#reading_list").load(new_loc + " #reading_list"); // pull data using ajax
	}

	start.datepicker("setDate", "{{ start_date }}")
	end.datepicker("setDate", "{{ end_date }}")
	
});


</script>