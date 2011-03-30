from datetime import datetime, timedelta
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.core.exceptions import ValidationError

from django.http import HttpResponse, HttpResponseRedirect, Http404
from reading.models import Reading
from reading.forms import ReadingForm

# this view does not know about series, so it has to use the readings_index.html instead of index.html, and not show the readings sidebar
def list_readings(request, start_date=datetime.today(), end_date=datetime.today()+timedelta(31)):
	reading_list = Reading.objects.filter(date_and_time__gte=start_date).filter(date_and_time__lte=end_date).order_by("date_and_time")
	return render_to_response('readings_index.html', {'reading_list': reading_list }, context_instance=RequestContext(request))
	
def list_readings_month(request, num_months=1, ajax="0", index="0"):
	reading_list = Reading.objects.filter(date_and_time__gte=datetime.today()).filter(date_and_time__lte=datetime.today()+timedelta(31*int(num_months.rstrip('/')))).order_by("date_and_time")
	if index=="0":
		whether_index = False
	else:
		whether_index = True
	
	if ajax=="1": # list_readings has not styles by itself
		return render_to_response('list_readings.html', {'reading_list': reading_list, 'index': whether_index }, context_instance=RequestContext(request))
	else: # readings_index is a wrapper so the page can stand on its own
		return render_to_response('readings_index.html', {'reading_list': reading_list, 'index': whether_index }, context_instance=RequestContext(request))
	
def detail_reading(request, series_id=None, reading_id=None):
	return HttpResponse("detail")
	
@login_required
def edit_reading(request, reading_id=None):

	if request.is_ajax():
		r = get_object_or_404(Reading, pk=reading_id)
		#r.description = description or ""
		r.description = request.POST["description"]
		try:
			r.full_clean()
			r.save()
		except ValidationError, e:
			for error in e.message_dict:
				print "error=%s" % error
			messages.error(request, "There was an error validating your update.")
		return render_to_response('index.html', {}, context_instance=RequestContext(request))
			
		# need to return some 
	else:
		created_new = True;
		if reading_id:
			created_new = False;
			r = get_object_or_404(Reading, pk=reading_id)
		else:
			r = Reading()

		if request.method == "POST": # if we are receiving POST data, then we're getting the result of a form submission, so we save it to the database and show the detail template
			form = ReadingForm(request.POST, instance=r)
			if form.is_valid():
				try:
					form.save();
					messages.add_message(request, messages.SUCCESS, 'Reading %s. Thanks!' % (created_new and "Created" or "Updated"))
				
				except ValueError:
					messages.add_message(request, message.ERROR, 'Error %s reading.' % (created_new and "creating" or "updating", r.primary_name))
					return HttpResponseRedirect(reverse('edit-reading', args=(sr.id,)))
			else:
				messages.error(request, "Please correct the errors below.")
		else:
			form = ReadingForm(instance=r)
	return render_to_response('edit_reading.html', {'form': form, 'reading': r}, context_instance=RequestContext(request))
		
	
def index(request, series_id=None):
	return HttpResponse("index")