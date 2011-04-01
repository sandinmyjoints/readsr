# Create your views here.
import copy
from datetime import datetime, timedelta
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import logout
from django.views.generic import list_detail
from django.contrib.sites.models import Site
from django.conf import settings

from series.models import Series, Contact, Affiliate, Venue, Address
from series.forms import SeriesForm, ReadsrContactForm, RemoveSeriesContactForm, VenueForm, AffiliateForm, AddressForm
from reading.models import Reading
from city_site.models import CitySite


#below are for ContactForm
from contact_form.forms import ContactForm

# login/logout/register ####################
#def logout_user(request):
#	response = logout(request, next_page=reverse('series.views.index'))
#	return response	

# this is not used anymore. registration is handled by django-registration.
#def register(request):
#    if request.method == 'POST':
#        form = UserCreationForm(request.POST)
#        if form.is_valid():
#            new_user = form.save()
#			# need to add a successful registration message here
#            return HttpResponseRedirect(reverse('series.views.index'))
#    else:
#        form = UserCreationForm()
#    return render_to_response("registration/register.html", 
#		{ 'form': form },
#		context_instance=RequestContext(request))

# account ######################
@login_required
def account_profile(request):
	"""
	Renders the user's profile page, which contains links to update email and change password.
	Requires the user to be logged in.
	"""
	#user_series = Series.objects.filter(contact__first_name__exact=request.user.first_name).filter(contact__last_name__exact=request.user.last_name)
	user_series = Series.objects.filter(contact__user__exact=request.user)
	
	return render_to_response("registration/profile.html", { "user": request.user, "user_series": user_series }, context_instance=RequestContext(request))

#	if request.user.is_authenticated():
#		return render_to_response("registration/profile.html", { "user": request.user }, context_instance=RequestContext(request))
#	else:
#		messages.info(request, "You aren't logged in. Please log in or create an account.")
#	return render_to_response("registration/login.html", {}, context_instance=RequestContext(request))

# index and upcoming #################### 
def index(request, series_id=None, genre_id=None, start_date=datetime.today().date(), end_date=(datetime.today() + timedelta(37)).date()):
	"""
	Displays a list of readings ordered chronologically. Takes a start date and an end date.
	By default, it shows readings from all series. But if a series ID is passed in, it 
	will only return readings in the date range for that series.
	
	** Arguments **
	
	``start_date``
	 	A date from which to start display readings. Form is MM-DD-YYYY.
		Default is today. 
		Can be passed as a GET parameter.
	
	``end_date``
	 	A date at which to stop displaying readings. Form is MM-DD-YYYY.
		Default is 37 days (one month and one week) from today.
		Can be passed as a GET parameter.
		
	``series_id``
		Default is none, which will cause index to display readings from all series.
		Can be passed as a GET parameter.
		
	``genre_id``
		Default is none, which returns readings of all any and all genres. 
		
	"""
	current_site = Site.objects.get_current()
	
	if request.method == "GET":
		# if request is get, then we can get start and end dates from that
		start = request.GET.get('start', "")
		end = request.GET.get('end', "")
		series_id = request.GET.get('series_id', "")

		if not start=="" and not end=="":
			start_date = datetime.strptime(start, "%m-%d-%Y")
			end_date = datetime.strptime(end, "%m-%d-%Y")
		
		reading_list = Reading.objects.filter(series__site__exact=current_site.id).filter(date_and_time__gte=start_date).filter(date_and_time__lte=end_date)
		
		#print "series_id = %s" % series_id
		#print "Start_Date=%s end_date=%s" % (start_date, end_date)
		#print "reading_list = %s, len=%d" % (reading_list, len(reading_list))
		#print "series_list = %s, len=%d" % (series_list, len(series_list))
		print "series_id = %s" % series_id
		if series_id:
			reading_list = reading_list.filter(series__site__exact=current_site.id).filter(date_and_time__gte=start_date).filter(date_and_time__lte=end_date).filter(series__id__exact=series_id)
			series_list = Series.objects.filter(site__exact=current_site.id).filter(pk=series_id)
			#print "filtered reading_list = %s, len=%d" % (reading_list, len(reading_list))
			#print "filtered series_list = %s, len=%d" % (series_list, len(series_list))
					
	return render_to_response('index.html', {'reading_list': reading_list, 'index': True, 'start_date': start_date.strftime("%m/%d/%Y"), 'end_date': end_date.strftime("%m/%d/%Y") }, context_instance=RequestContext(request))

	# generic views way
	#try:
	#return list_detail.object_list(request, queryset=Series.objects.all(), template_name="index.html", template_object_name="series")
	#except TemplateDoesNotExist:
	#	raise Http404()

#def upcoming(request):
#	# need to list the actual Reading events
#	return index(request)

# about ##############################
def about(request, form_class=ContactForm, template_name='about.html', success_url=None, extra_context=None, fail_silently=False, message_success=False):
	"""
	Displays some information about the website.
	Also displays a contact form which can be used to send an email to site managers.
	"""
	# Uses the series_list to display the sidebar. Is there another way do to this?
	return contact_form_view(request, form_class=form_class, template_name=template_name, success_url=success_url, fail_silently=fail_silently, message_success=message_success)
	
def contact_form_view(request, form_class, template_name, success_url=None, extra_context=None, fail_silently=False, message_success=False):
	"""
	Displays a contact form which can be used to send an email to site managers.
	If message is successfully sent, queues a message for the user and returns them to
	the site index page.
	"""
	if success_url is None:
		success_url = reverse('series.views.index')
	if request.method == 'POST': # if user is submitting a message through the contact form
		form = form_class(data=request.POST, files=request.FILES,request=request) 
		if form.is_valid():
			form.save(fail_silently=fail_silently) 
			messages.success(request, "Your message was sent.")
			return HttpResponseRedirect(success_url)  
		else:
			messages.error(request, "Could not send your message.")
	else: 
		form = form_class(request=request) # if no message, has been submitted, present a blank form

	if extra_context is None: 
		extra_context = {} 
	context = RequestContext(request) 
	for key, value in extra_context.items():
		context[key] = callable(value) and value() or value

	return render_to_response(template_name, { 'form': form }, context_instance=context)
	
def generic_edit_view(request, edit_object, form_class, template_name, success_url=None, extra_context=None):
	"""
	Allows editing of any kind of object.
	"""
	if success_url is None:
		success_url = reverse('series.views.index')
	if request.method == 'POST': # if user is submitting a message through the contact form
		form = form_class(data=request.POST, instance=edit_object) 
		if form.is_valid():
			form.save() 
			messages.success(request, "Updated.")
			return HttpResponseRedirect(success_url)  
		else:
			messages.error(request, "Could not update.")
	else: 
		form = form_class(instance=edit_object) 
		
	if extra_context is None: 
		extra_context = {} 
	context = RequestContext(request) 
	for key, value in extra_context.items():
		context[key] = callable(value) and value() or value

	return render_to_response(template_name, { 'form': form }, context_instance=context)
	

# series ####################

def detail_series(request, series_id):
	"""
	Displays a page about one particular series object, and a list of all its readings 
	that happen today or in the future.
	"""
	sr = get_object_or_404(Series, pk=series_id)
	reading_list=Reading.objects.filter(date_and_time__gte=datetime.today()).filter(series=series_id)
	#print "reading_list = %s, reading_list length = %d" % (reading_list, len(reading_list))
	
	return render_to_response('detail_series.html', {'series': sr, 'reading_list': reading_list}, context_instance=RequestContext(request))
	
@login_required	
def edit_series(request, series_id=None):
	"""
	Creates a new series if no series_id is passed in.
	Edits an existing series if a series_id is passed in.
	"""
	# if there is a reading_id, then we are editing an existing Reading
	if series_id:
		sr = get_object_or_404(Series, pk=series_id)
	else: # otherwise, we are creating a new Series
		sr = Series()
		
	if request.method == 'POST': # if we are receiving POST data, then we're getting the result of a form submission, so we save it to the database and show the detail template
		form = SeriesForm(request.POST, instance=sr)
		sr.site = CitySite.objects.get(pk=settings.SITE_ID) # site can only be the current site
		old_sr = copy.deepcopy(sr) # need to create a copy because is_valid() will trigger model validation, which will update the model object with the new time values
		if form.is_valid():
			new_reading_list = []
			created_new = create_new_readings_list = False
			if not sr.id:
				# We are creating a new reading series, so create all its reading events for a year.
				created_new = True
				if sr.regular:
					create_new_readings_list = True

			# We are updating an exist reading series, so need to check if its time or regularity changed. 				
			# Loop through items in sr and compare them to items in form.cleaned_data
			# to see if any of the date/times have changed. 
			# If so, we will need to update its reading events.
			elif old_sr.regular != form.cleaned_data["regular"] or old_sr.day_of_week != form.cleaned_data["day_of_week"]	or old_sr.week_within_month != form.cleaned_data["week_within_month"] or old_sr.irregular_date_description != form.cleaned_data["irregular_date_description"] or old_sr.time != form.cleaned_data["time"] or old_sr.regular != form.cleaned_data["regular"] :
				# For now, we hose all the items if the series changed regularity
				# If what is being changed is the date, then				
				# go into the db and hose all future readings.
				# Then insert new readings to replace them.
				# Need to warn the user this will delete all existing readings.
				# Would be nice to someday fix it so it updates readings more intelligently, 
				# but not sure what that would entail.
				future_readings = Reading.objects.filter(series=sr.id).filter(date_and_time__gte=datetime.today()).delete()
				if sr.regular:
					create_new_readings_list = True
					
			# If the series has a regular time, day of the week, and week of the month, and
			# it is new or its time has changed, then create new reading objects for the new year
			if create_new_readings_list: 
				new_reading_list = new_series_readings(sr)
				
			try:
				form.save()
				# Now that the new series is saved, tell all the new readings what its id is, and save them to the db
				for reading in new_reading_list:
					reading.series = sr
					reading.save()
					
				#updated_reading = form.save(commit=False)
				#updated_reading.save()
				#form.save_m2m()
				# add a successful series creation message 
				messages.add_message(request, messages.SUCCESS, '%s %s. Thanks!' % (created_new and "Created" or "Updated", sr.primary_name))
				
			except ValueError:
				messages.add_message(request, message.ERROR, 'Error %s %s.' % (created_new and "creating" or "updating", sr.primary_name))
				return HttpResponseRedirect(reverse('edit-series', args=(sr.id,)))
			return HttpResponseRedirect(reverse('detail-series', args=(sr.id,)))
		else:
			messages.error(request, "Please correct the errors below.")
			
	else: # otherwise, we create a blank form and show it in the edit template
		form = SeriesForm(instance=sr)
	return render_to_response('edit_series.html', {'form': form, 'series': sr}, context_instance=RequestContext(request))
	
def new_series_readings(sr, years=1):
	"""
	Returns a list of Reading objects for a given Series for a number of years ahead.
	
	** Arguments **
	
	``years``
	 	The number of years to create Reading objects for for this series.
	"""
	
	new_reading_list = []
	if not sr:
		return new_reading_list
		
	for reading_day in sr.reading_days_ahead_by_month(12*years):
		r = Reading()
		r.date_and_time = datetime.combine(reading_day, sr.time)
		# we can't save r here because sr.id is null because it hasn't been saved yet, so
		# add r to the list of readings to be saved after sr is saved.
		new_reading_list.append(r)

	return new_reading_list

# old remove_series, hopefully I fixed it
#def remove_series(request, series_id=None):
#	extra_context = {'series': sr}
	#form_class.series_name.clean(sr.primary_name)
#	return contact_form_view(request, form_class=RemoveSeriesContactForm, template_name="remove_series.html", extra_context=extra_context)
	
@login_required
def remove_series(request, template_name="remove_series.html", series_id=None, success_url=None, extra_context=None, fail_silently=False, message_success=False):
	"""
	Displays a  form which can be used to requet removal of a series.
	The request is emailed to site managers. If they decide to remove the series, that
	can be done through the admin site.
	"""
	sr = get_object_or_404(Series, pk=series_id)
	
	if success_url is None:
		success_url = reverse('series.views.index')
	if request.method == 'POST': # if user is submitting a message through the contact form

		# add the series to the context for the form so that it will be available to the email templates.
		form = RemoveSeriesContactForm(data=request.POST, files=request.FILES,request=request, username=request.user.username) 
		if form.is_valid():
			form.save(fail_silently=fail_silently) 
			messages.success(request, "Your message was sent.")
			return HttpResponseRedirect(success_url)  
		else:
			messages.error(request, "Could not send your message.")
	else: 
		form = RemoveSeriesContactForm(request=request, initial={ 'series_id': sr.id, 'series_primary_name': sr.primary_name, 'username': request.user.username, 'email': request.user.email, 'name': request.user.get_full_name() })

	if extra_context is None: 
		extra_context = {'series': sr} 
	context = RequestContext(request) 
	for key, value in extra_context.items():
		context[key] = callable(value) and value() or value

	return render_to_response(template_name, { 'form': form, 'user': request.user }, context_instance=context)
	
# contact ####################
def contact_list(request):
	return list_detail.object_list(request, queryset=Contact.objects.all(), template_name="generic_list.html")
	
def detail_contact(request, contact_id):
	c = get_object_or_404(Contact, pk=contact_id)
	return render_to_response('detail_contact.html', {'contact': c}, context_instance=RequestContext(request))
	
@login_required
def edit_contact(request, contact_id=None):
	if contact_id:
		c = get_object_or_404(Contact, pk=contact_id)
	else:
		c = Contact()
	if request.method == 'POST':
		form = ReadsrContactForm(request.POST, instance=c)
		if form.is_valid():
			try:
				form.save()
				messages.success(request, 'Updated %' % c)
			except ValueError:
				# need to figure out how to display more about this error
				messages.error(request, 'ValueError')
				return HttpResponseRedirect(reverse('series.views.detail_contact', args=(c.id,)))
	else:
		form = ReadsrContactForm(instance=c)	
	return render_to_response('edit_contact.html', {'form': form, 'contact': c}, context_instance=RequestContext(request))

# venue ########################
def venue_list(request):
	return list_detail.object_list(request, queryset=Venue.objects.all(), template_name="generic_list.html")

@login_required
def edit_venue(request, venue_id=None, success_url=None, extra_context=None):
	"""
	Allows editing of a venue.
	"""
	if venue_id:
		venue = get_object_or_404(Venue, pk=venue_id)
		venue_form = VenueForm({
			'id': venue.id,
			'name': venue.name,
			'address': venue.address,
			'phone': venue.phone,
			'website': venue.website,
			'in_dc': venue.in_dc
		})
		address = venue.address
		address_form = AddressForm({
			'street_address': address.street_address,
			'city': address.city_name,
			'state': address.state,
			'zipcode': address.zip_code
		})
	else:
		venue = Venue()
		venue_form = VenueForm()
		address = Address()
		address_form = AddressForm()

	success_url = request.REQUEST.get("next", 'series.views.index')
	print "Success_url is %s" % success_url
	
	if request.method == 'POST': # if user is submitting a message through the contact form
		venue_form = VenueForm(data=request.POST) 
		address_form = AddressForm(data=request.POST)
		if venue_form.is_valid() and address_form.is_valid():
			#venue_form.save() 
			#address_form.save()
			address.street_address = address_form.cleaned_data["street_address"]
			address.city_name = address_form.cleaned_data["city"]
			address.state = address_form.cleaned_data["state"]
			address.zip_code = address_form.cleaned_data["zipcode"]
			address.save()
			
			venue.address = address
			venue.name = venue_form.cleaned_data["name"]
			venue.phone = venue_form.cleaned_data["phone"]
			venue.in_dc = venue_form.cleaned_data["in_dc"]
			venue.website = venue_form.cleaned_data["website"]
			
			venue.save()
			
			messages.success(request, "Venue updated.")
			# need to get the success_url out of the query string? or could it be in the post
			return HttpResponseRedirect(success_url)  
		else:
			messages.error(request, "Could not update venue.")
		
	# need to figure out how to pass the success_url as next url in query string
	if extra_context is None: 
		extra_context = { } 
	context = RequestContext(request) 
	for key, value in extra_context.items():
		context[key] = callable(value) and value() or value

	return render_to_response("edit_venue.html", { 'venue_form': venue_form, 'address_form': address_form }, context_instance=context)
	
def detail_venue(request, venue_id):
	"""
	Show the details of a venue, including a list of all the series happening there.
	"""
	
	series_list = Series.objects.filter(venue=venue_id)
	extra_context = { 'series_list': series_list }
	print "series_list = %s" % series_list
	# probably no point in using the generic view any more--might as well do render to response
	return list_detail.object_detail(request, queryset=Venue.objects.filter(id__exact=venue_id), object_id=venue_id, template_name="detail_venue.html", template_object_name="venue", extra_context=extra_context)
	
# affiliation ##################	
def affiliate_list(request):
	return list_detail.object_list(request, queryset=Affiliate.objects.all(), template_name="generic_list.html")

@login_required
def edit_affiliate(request, affiliate_id=None):
	if affiliate_id:
		affiliate = get_object_or_404(Affiliate, pk=affiliate_id)
	else:
		affiliate = Affiliate()
	return generic_edit_view(request, edit_object=affiliate, form_class=AffiliateForm, template_name="generic_form.html")

