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
				success: function() {					
				}
			})
	
	    },
		control: 'textarea',
	});
	
}