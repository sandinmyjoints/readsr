import copy
import string
import calendar
import dateutil
from datetime import datetime, timedelta
from urlparse import urlparse

from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import logout
from django.contrib.sites.models import Site
from django.views.generic import list_detail
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory

from profiles.views import profile_detail as profile_profile_detail
from profiles.views import create_profile as profile_create_profile
from profiles.views import edit_profile as profile_edit_profile

import tweepy
from bitly import bitly

from swingtime.models import Event, EventType
#from swingtime.forms import MultipleOccurrenceForm
from swingtime.views import event_view, add_event

from series.util import get_tweepy_api
from series.models import Series, Affiliate, Venue, Address, SeriesTweet
from series.forms import SeriesForm, ReadsrContactForm, RemoveSeriesContactForm, VenueForm, AffiliateForm, AddressForm, ProfileForm, ReadingMultipleOccurrenceForm
from reading.models import Reading
from city_site.models import CitySite
from contact_form.forms import ContactForm

def splash(request):
    """
    Present a splash screen that shows all the cities that Readsr is currently tracking.
    """
    
    current_site = Site.objects.get_current()
    return render_to_response('splash.html', { 'sites_list': Site.objects.exclude(id__exact=current_site.id) }, context_instance=RequestContext(request))

def about(request, form_class=ContactForm, success_url=None, extra_context=None, fail_silently=False, message_success=False):
    """
    About

    Displays some information about the website.
    Also displays a contact form which can be used to send an email to site managers.
    """
    return contact_form_view(request, form_class, template_name="about.html")
    
def contact_form_view(request, form_class, template_name, success_url=None, extra_context=None, fail_silently=False, message_success=False):
    """
    Contact Form

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
   
def list_series(request):
    try:
        series_list = Series.objects.filter(site__exact=settings.SITE_ID)
        
        return render_to_response("list_all_series.html", { 'series_list': series_list }, context_instance=RequestContext(request))
        
    except Site.DoesNotExist:
        raise Http404
    

@login_required
def create_series(request, extra_context=None):
    """
    Creates a new series.
    """

    dtstart = None
    if request.method == 'POST':
        print "POST. request.user.pk is %s, request.user is %s" % (request.user.pk, request.user)
        
        event_form = SeriesForm(request.POST) 
        recurrence_form = ReadingMultipleOccurrenceForm(request.POST)
        #import pdb; pdb.set_trace()
        if event_form.is_valid() and recurrence_form.is_valid():
            # We are creating a new reading series, so give it the current user as the contact
            sr = event_form.save(commit=False)
            sr.contact = request.user
            sr.event_type = EventType.objects.get(pk=1)
            sr.site = CitySite.objects.get(pk=settings.SITE_ID)
            sr.save()
            recurrence_form.save(sr)
            
            # We are creating a new reading series, so if it is a regular reading series,
            # create all its reading events for a year.
            new_reading_list = []
            if sr.regular:
                need_to_create_new_readings_list = True
            # TODO fill this in using occurrences            
            
            
            tweet_or_not = True 
            tweet_message = ["New series: %s!" % sr.title] 
            
            if tweet_or_not:
                send_tweet(request, sr=sr, tweet_message=tweet_message)
            
            return HttpResponseRedirect(sr.get_absolute_url())
        else: # not valid
            print "\n".join(["form is not valid.", "event_form errors = %s" % event_form.errors, "recurrence_form errors = %s" % recurrence_form.errors])
    else: # not POST
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except:
                pass
                
        if dtstart == None:
            today = datetime.today().date()
            dtstart = datetime(today.year, today.month, today.day, 17, 0, 0)

        print "not POST. request.user.pk is %s, request.user is %s, dtstart is %s" % (request.user.pk, request.user, dtstart)
        event_form = SeriesForm()
        recurrence_form = ReadingMultipleOccurrenceForm(initial=dict(dtstart=dtstart))
        #import pdb; pdb.set_trace()

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
        
    return render_to_response(
        "add_series.html",
        dict(dtstart=dtstart, event_form=event_form, recurrence_form=recurrence_form),
        context_instance=context
    )
    
@login_required 
def edit_series(request, series_id=None):
    """
    Edits an existing series and its recurring occurrence.
    """


    '''
    View an ``Event`` instance and optionally update either the event or its
    occurrences.

    Context parameters:

    event
        the event keyed by ``pk``
        
    event_form
        a form object for updating the event
        
    recurrence_form
        a form object for adding occurrences
    '''
	
	# TODO add tweets back to this
	
    event = get_object_or_404(Series, pk=series_id)
    event_form = recurrence_form = None
    if request.method == 'POST':
        if '_update' in request.POST:
            event_form = SeriesForm(request.POST, instance=event)
            if event_form.is_valid():
                event_form.save(event)
                return HttpResponseRedirect(request.path)
        elif '_add' in request.POST:
            recurrence_form = ReadingMultipleOccurrenceForm(request.POST)
            if recurrence_form.is_valid():
                recurrence_form.save(event)
                return HttpResponseRedirect(request.path)
        else:
            return HttpResponseBadRequest('Bad Request')

    event_form = event_form or SeriesForm(instance=event)
    if not recurrence_form:
        recurrence_form = ReadingMultipleOccurrenceForm(
            initial=dict(dtstart=datetime.now())
        )
            
    return render_to_response(
        "edit_series.html", 
        dict(event=event, event_form=event_form, recurrence_form=recurrence_form),
        context_instance=RequestContext(request)
    )
	
	
            
    if request.method == 'POST': # If we are receiving POST data, then we're getting the result of a form submission, so we save it to the database and show the detail template
        form = SeriesForm(request.POST, instance=sr)
        recurrence_form = MultipleOccurrenceForm(request.POST, instance=event)
        tweet_or_not = False # Start assuming we won't tweet, but if any of the changes occur that trigger a tweet, this value will change to true.
        tweet_message = [] # Start with an empty tweet message.
        
        # For updating existing series, need to create a copy here because is_valid() will trigger 
        # model validation, which will update the model object with the new values
        # and we won't be able to tell what changed to determine whether we should tweet or not.
        # (A new series won't use old_sr for anything.)
        old_sr = copy.deepcopy(sr) 

        if form.is_valid():
            print "form is valid"
            new_reading_list = []
            need_to_create_new_readings_list = False

            # We are updating an existing series.                 
            # Depending on what changed, we may want to tweet about it, so start constructing
            # a tweet message.
            tweet_message.append("%s has been updated!" % old_sr.title)
            tweet_or_not = False # Only particular updates trigger a tweet, so set this to false for now.
            
            # If the name has changed, tweet about it:
            if form.cleaned_data["title"] != old_sr.title:
                tweet_or_not = True
                tweet_message.append("New name: %s" % sr.title)
            
            # We are updating an existing reading series, so need to check if its time or regularity changed.               
            # Loop through items in sr and compare them to items in form.cleaned_data
            # to see if any of the date/times have changed.                 
            if old_sr.regular != form.cleaned_data["regular"] \
                or old_sr.day_of_week != form.cleaned_data["day_of_week"] \
                or old_sr.week_within_month != form.cleaned_data["week_within_month"] \
                or old_sr.irregular_date_description != form.cleaned_data["irregular_date_description"] \
                or old_sr.time != form.cleaned_data["time"] :
                # Hose all the reading events if the series changed regularity, day of week, week 
                # within month, irregular date description, or time.
                # Then insert new readings to replace them.
                # Future enhancement: update readings more intelligently, 
                # but would need to think about what that would entail.
                future_readings = Reading.objects.filter(series=sr.id).filter(start_time__gte=datetime.today()).delete()
                if sr.regular:
                    need_to_create_new_readings_list = True
                
                tweet_or_not = True
                tweet_message.append("New time.")

            if old_sr.venue.id != form.cleaned_data["venue"].id:
                # The location has changed, so add that to the tweet.
                tweet_or_not = True
                tweet_message.append("New venue: %s" % form.cleaned_data["venue"])                                    
                
            try:
                # Commenting the below out pending changes now that we're using Swingtime
                series_form.save()
                occurrence_form.save()
                # 
                # # If the series has a regular time, day of the week, and week of the month, and
                # # it is new or its time has changed, then create new reading objects for a year ahead.
                # # TODO: Set a date at which to refresh the reading list for the next year, when 
                # # the ones created here run out.
                # if need_to_create_new_readings_list: 
                #     new_reading_list = sr.get_future_readings(1)
                # for reading in new_reading_list:
                #     reading.save()

                if tweet_or_not:
                    send_tweet(request, sr=sr, tweet_message=tweet_message)
                
            # Handle possible errors from tweep and bitly
            except ValueError, ex:
                messages.add_message(request, messages.ERROR, 'Value error %s %s. Error: %s' % (created_new and "creating" or "updating", sr.title, ex))
                if sr.id:
                    return HttpResponseRedirect(reverse('edit-series', args=(sr.id,)))
                else:
                    return HttpResponseRedirect(reverse('create-series'))
            except IOError, ex:
                messages.add_message(request, messages.ERROR, 'Error %s %s. Could not tweet: %s' % (created_new and "creating" or "updating", sr.title, ex))
            finally:
                # Add a successful series creation message. TODO this doesn't really come after the event has been saved now that we are using swingtime's add_event view 
                messages.add_message(request, messages.SUCCESS, '%s %s. Thanks!' % (created_new and "Created" or "Updated", sr.title))

                return HttpResponseRedirect(sr.get_absolute_url())

        else:
            print "form is not valid. errors = %s" % form.errors
            messages.error(request, "Please correct the errors below.")
            return render_to_response('edit_series.html', { 'series_form': series_form, 'recurrence_form': recurrence_form, 'series': sr }, context_instance=RequestContext(request))
    
    # Handle the case where the request method is not POST
    print "edit_series not POST, series_id is %s" % (series_id, )
    series_form = SeriesForm(instance=sr)
    recurrence_form = MultipleOccurrenceForm(instance=event)
    return render_to_response('edit_series.html', { 'series_form': series_form, 'recurrence_form': recurrence_form, 'series': sr }, context_instance=RequestContext(request))
    
def send_tweet(request, tweet_message=[], sr=None):
    # Tweet and save the tweet to the db.
    api = bitly.Api(settings.BITLY_USER, settings.BITLY_KEY) 
    url = request.build_absolute_uri().replace("/edit", "")
    res = api.shorten(url)
    tweet_message.append("%s" % res)
    send_msg = ' '.join(tweet_message)

    try:
        api = get_tweepy_api()
        api.update_status(send_msg)
        last_msg = api.user_timeline(count=1)[0]
        SeriesTweet.objects.create(
            series = sr,
            tweet = send_msg,
            bitly_url = res,
            twitter_status_id = last_msg.id
        )

    except tweepy.TweepError as terror:
        if settings.DEBUG:
            print "tweep error: %s" % terror
    
@login_required
def remove_series(request, template_name="remove_series.html", series_id=None, success_url=None, extra_context=None, fail_silently=False, message_success=False):
    """
    Displays a form which can be used to requet removal of a series.
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
        form = RemoveSeriesContactForm(request=request, initial={ 'series_id': sr.id, 'series_primary_name': sr.title, 'username': request.user.username, 'email': request.user.email, 'name': request.user.get_full_name() })

    if extra_context is None: 
        extra_context = { 'series': sr } 
    context = RequestContext(request) 
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name, { 'form': form, 'user': request.user }, context_instance=context)
        
def contact_detail(request, contact_id):
    """
    Contact

    Presents the details of a particular contact.
    """
    c = get_object_or_404(User, pk=contact_id)
    return render_to_response('contact_detail.html', {'contact': c}, context_instance=RequestContext(request))
    
def venue_list(request):
    """
    Venue List

    Lists all the venues on the site. 
    """
    return list_detail.object_list(request, queryset=Venue.objects.all(), template_name="generic_list.html")

@login_required
def edit_venue(request, venue_id=None, success_url=None, extra_context=None):
    """
    Edit Venue

    Allows editing of a venue object.
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
    
    if request.method == 'POST': # if user is submitting a message through the contact form
        venue_form = VenueForm(data=request.POST) 
        address_form = AddressForm(data=request.POST)
        if venue_form.is_valid() and address_form.is_valid():
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

            return HttpResponseRedirect(success_url)  
        else:
            messages.error(request, "Could not update venue.")
        
    if extra_context is None: 
        extra_context = { } 
    context = RequestContext(request) 
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response("edit_venue.html", { 'venue_form': venue_form, 'address_form': address_form }, context_instance=context)
    
def venue_detail(request, venue_id):
    """
    Show the details of a venue, including a list of all the series happening there.
    """
    series_list = Series.objects.all()
    venue_series_list = series_list.filter(venue=venue_id)
    return render_to_response("venue_detail.html", { 'venue': Venue.objects.get(pk=venue_id), 'series_list': series_list, 'venue_series_list': venue_series_list}, context_instance=RequestContext(request))
    
def affiliate_list(request):
    """
    Affiliate List
    
    List all the affiliate objects.
    """
    return list_detail.object_list(request, queryset=Affiliate.objects.all(), template_name="generic_list.html")

@login_required
def edit_affiliate(request, affiliate_id=None):
    """
    Edit Affiliate
    """
    
    if affiliate_id:
        affiliate = get_object_or_404(Affiliate, pk=affiliate_id)
    else:
        affiliate = Affiliate()

    return generic_edit_view(request, edit_object=affiliate, form_class=AffiliateForm, template_name="generic_form.html")

def site_redirect(request):
    """
    Site_redirect is used for switching between different city_sites when javascript is disabled.
    """
    if request.method == "GET":
        new_site = request.GET.get('new_site', None)
        if not new_site.startswith("http://"):
            new_site = "".join(["http://", new_site])
        return redirect(urlparse(new_site).geturl())
 
@login_required
def profile_detail(request, username):
    """
    Renders the user's profile page, which contains links to update email and change password.
    Requires the user to be logged in.
    """

    user_owned_series = Series.objects.filter(contact__exact=request.user)

    return profile_profile_detail(request, username, extra_context={ 'user_series': user_owned_series })

@login_required
def create_profile(request):
    """
    Create the profile via django-profiles.
    """
    
    return profile_create_profile(request)

@login_required 
def edit_profile(request):
    """
    Edit the profile via django-profiles, but 
    using the custom form class ProfileForm and passing in a list
    of series that this user owns.
    """
    
    user_owned_series = Series.objects.filter(contact__exact=request.user)
    return profile_edit_profile(request, form_class=ProfileForm, extra_context={ 'user_series': user_owned_series })

def index(request, series_id=None, genre_id=None, list_view=True, start_date=datetime.today().date(), end_date=(datetime.today() + timedelta(37)).date()):
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
        If series_id is supplied, index will only display the readings for that particular
        series. 
        Can be passed as a GET parameter.

    ``genre_id``
        Default is none, which returns readings of all any and all genres. 

    ``list_view``
        Whether to show in list view or in calendar view.

    """

    current_site = Site.objects.get_current()

    # Start assuming client's js is enabled. We will get a value that indicates otherwise
    # through the submitted form if it is not.
    # The template will use this value to decide whether to show some extra information
    # that would otherwise be shown using js (start date and end date).
    js_available = True

    # If we're on the generic www.readsrs.com site, show the splash screen with
    # a list of available cities.
    if current_site.id == settings.WWW_SITE:
        return splash(request)

    if request.method == "GET":
        # If request is get, then we can extract start and end dates from that.
        start = request.GET.get('start', "")
        end = request.GET.get('end', "")
        series_id = request.GET.get('series_id', series_id)
        # If js is enabled, list_view will be true or false coming from the js AJAX.
        list_view = request.GET.get('list_view', "True")
        if settings.DEBUG:
            print "method is get, list_view is %s, start out of GET is %s, end is %s" % (list_view, start, end)

        # If list_view is "Calendar" or "List", then the client is not using js. We know
        # this because they submitted a form, rather than the js capturing the event
        # and preventing it from submitting, and sending true or false via AJAX.
        if list_view == "Calendar":
            # js is disabled
            list_view = False
            js_available = False
        elif list_view == "List":
            # js is disabled
            list_view = True
            js_available = False
        elif list_view == "false":
            list_view = False
        else:
            list_view = True

        if not start=="" and not end=="":
            try:
                if string.find(start, "-") > -1:
                    start_date = datetime.strptime(start, "%m-%d-%Y")
                    end_date = datetime.strptime(end, "%m-%d-%Y")
                else:
                    start_date = datetime.strptime(start, "%m/%d/%Y")
                    end_date = datetime.strptime(end, "%m/%d/%Y")

            except ValueError:
                # Raise an error if neither of those date formats works
                raise Http404

            if not list_view and not js_available:
                # this means we are using calendar but without the input
                # validation occuring in js, so set the start date to
                # the first of the month and the end date to
                # one month after the start date.
                start_date = start_date.replace(day=1)
                end_date = start_date + dateutil.relativedelta.relativedelta(months=1)
                # end_date = end_date.replace(month=start_date.month, day=calendar.monthrange(start_date.year, start_date.month)[1], year=start_date.year)    

        else:
            # If neither dates are supplied, default to a range of today + one month.
            start_date = datetime.today()
            end_date = start_date + dateutil.relativedelta.relativedelta(months=1)

        reading_list = Reading.objects.filter(series__site__exact=current_site.id).filter(start_time__gte=start_date).filter(start_time__lte=end_date)

        if series_id:
            # we are in detail_series mode so filter the reading_list down to just the ones for this series_id
            reading_list = reading_list.filter(series__id=series_id)
            sr = Series.objects.get(pk=series_id)
        else:
            sr = None

    else:
        # not GET method
        raise Http404

    if series_id:
        # we are in detail-series mode  
        pretty = sr.rrule.text()
        return render_to_response('series_detail.html', {
                                                            'series': sr, 
                                                            'pretty_rrule': pretty,
                                                            'reading_list': reading_list,
                                                            'start_date': start_date.strftime("%m/%d/%Y"), 
                                                            'end_date': end_date.strftime("%m/%d/%Y"),
                                                            'cal_name': start_date.strftime("%B %Y"),
                                                            'list_view': list_view,
                                                            'year': start_date.year,
                                                            'month': start_date.month,
                                                            'js_available': js_available,
                                                        }, context_instance=RequestContext(request))
    else:                       
        # we are in index mode
        return render_to_response('index.html', {
                                                    'reading_list': reading_list, 
                                                    'index': True, 
                                                    'start_date': start_date.strftime("%m/%d/%Y"), 
                                                    'end_date': end_date.strftime("%m/%d/%Y"),
                                                    'cal_name': start_date.strftime("%B %Y"),                                                   
                                                    'list_view': list_view,
                                                    'year': start_date.year,
                                                    'month': start_date.month,
                                                    'js_available': js_available,                                                   
                                                }, context_instance=RequestContext(request))

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

def edit_user_series(request, contact_id=None):
    """
    Allows a user to edit all his/her own series via a formset.
    """
    
    if contact_id is None:
        raise Http404
        
    SeriesFormSet = modelformset_factory(Series, form=SeriesForm)
    
    if request.method == "POST":
        formset = SeriesFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Updated")

    formset = SeriesFormSet(queryset=Series.objects.filter(contact__exact=contact_id))
    
    return render_to_response("edit_all_series.html", { 'formset': formset }, context_instance=RequestContext(request))
    