import copy
import string
from datetime import datetime, timedelta
import calendar
from urlparse import urlparse

from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import logout
from django.views.generic import list_detail
from django.contrib.sites.models import Site
from django.conf import settings

#import tweepy # for tweeting about updated series
import bitlyapi # for shortening urls for tweets

from series.util import get_tweepy_api
from series.models import Series, Affiliate, Venue, Address, SeriesTweet
from series.forms import SeriesForm, ReadsrContactForm, RemoveSeriesContactForm, VenueForm, AffiliateForm, AddressForm, ProfileForm
from reading.models import Reading
from city_site.models import CitySite
from contact_form.forms import ContactForm

from profiles.views import profile_detail as profile_profile_detail
from profiles.views import create_profile as profile_create_profile
from profiles.views import edit_profile as profile_edit_profile


# profiles ######################
@login_required
def profile_detail(request, username):
    """
    Renders the user's profile page, which contains links to update email and change password.
    Requires the user to be logged in.
    """

    user_owned_series = Series.objects.filter(contact__exact=request.user)
    
#   return render_to_response("registration/profile.html", { "user": request.user, "user_series": user_series }, context_instance=RequestContext(request))
    return profile_profile_detail(request, username, extra_context={ 'user_series': user_owned_series })

#   if request.user.is_authenticated():
#       return render_to_response("registration/profile.html", { "user": request.user }, context_instance=RequestContext(request))
#   else:
#       messages.info(request, "You aren't logged in. Please log in or create an account.")
#   return render_to_response("registration/login.html", {}, context_instance=RequestContext(request))

@login_required
def create_profile(request):
    return profile_create_profile(request)
    
@login_required 
def edit_profile(request):
    user_owned_series = Series.objects.filter(contact__exact=request.user)
    return profile_edit_profile(request, form_class=ProfileForm, extra_context={ 'user_series': user_owned_series })

# index and upcoming #################### 
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
        Can be passed as a GET parameter.
        
    ``genre_id``
        Default is none, which returns readings of all any and all genres. 
        
    ``list_view``
        Whether to show in list view or in calendar view.
        
    """
    current_site = Site.objects.get_current()
    
    # assume client's js is enabled until we get a value that indicates otherwise.
    # the template will use this value to decide whether to show some extra information
    # that would otherwise be shown using js (start date and end date)
    js_available = True
    
    # If we're on the generic www.readsrs.com site, show a list of available cities
    if current_site.id == settings.WWW_SITE:
        return splash(request)
            
    if request.method == "GET":
        # If request is get, then we can get start and end dates from that
        start = request.GET.get('start', "")
        end = request.GET.get('end', "")
        series_id = request.GET.get('series_id', series_id)
        list_view = request.GET.get('list_view', "True")
        if settings.DEBUG:
            print "method is get, list_view is %s, start out of GET is %s, end is %s" % (list_view, start, end)

        # If list_view is Calendar or List, then the client is not using js. We know
        # this because they submitted a form, rather than the js capturing the event
        # and preventing it from submitting.
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
                # first try with dashes
                if string.find(start, "-") > -1:
                    start_date = datetime.strptime(start, "%m-%d-%Y")
                    end_date = datetime.strptime(end, "%m-%d-%Y")
                else:
                    # then try with slashes
                    start_date = datetime.strptime(start, "%m/%d/%Y")
                    end_date = datetime.strptime(end, "%m/%d/%Y")
                
            except ValueError:
                # raise an error if neither of those formats works
                raise Http404
                
            if not list_view and not js_available:
                # this means we are using calendar but without the input
                # validation occuring in js, so set the start date to
                # the first of the month and the end date to
                # one month after the start date.
                start_date = start_date.replace(day=1)
                end_date = end_date.replace(month=start_date.month, day=calendar.monthrange(start_date.year, start_date.month)[1], year=start_date.year)
                
                
        else:
            # if both dates are not supplied, default to a range of today + one month
            start_date = datetime.today()
            td = timedelta(31)
            end_date = start_date + td
        
        reading_list = Reading.objects.filter(series__site__exact=current_site.id).filter(date_and_time__gte=start_date).filter(date_and_time__lte=end_date)
        
        if series_id:
            # we are in detail_series mode so filter the reading_list down to just the ones for this series_id
            reading_list = reading_list.filter(series__id__exact=series_id)
            sr = Series.objects.get(pk=series_id)
        else:
            sr = None
            
    else:
        # not GET method
        raise Http404
    
    if series_id:
        # we are in detail-series mode  
        return render_to_response('series_detail.html', {
                                                            'series': sr, 
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

def splash(request):
    current_site = Site.objects.get_current()
    return render_to_response('splash.html', { 'sites_list': Site.objects.exclude(id__exact=current_site.id) }, context_instance=RequestContext(request))


# THIS VIEW IS DEPRECATED, REPLACED BY INDEX
def series_detail(request, series_id, list_view=True):
    """
    Displays a page about one particular series object, and a list of all its readings 
    that happen today or in the future.

    ``series_id``
        Series id must be supplied or else we get a 404 error.

    ``list_view``
        Whether to display in list view or calendar view. Default is list.
    """
    sr = get_object_or_404(Series, pk=series_id)
    reading_list=Reading.objects.filter(date_and_time__gte=datetime.today()).filter(series=series_id)
    if settings.DEBUG:
        print "series is %s, series contact_id is %s, series contact is X, series contact user is X" % (sr, sr.contact_id, )
    return render_to_response('series_detail.html', {
                                                        'series': sr, 
                                                        'reading_list': reading_list,
                                                        'list_view': list_view,
                                                    }, context_instance=RequestContext(request))



# about ##############################
def about(request, form_class=ContactForm, success_url=None, extra_context=None, fail_silently=False, message_success=False):
    """
    Displays some information about the website.
    Also displays a contact form which can be used to send an email to site managers.
    """
    return contact_form_view(request, form_class, template_name="about.html")
    
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
        tweet_or_not = False
        tweet_message = []
        
        # We are creating a new reading series, so give it the current user as the contact, and
        if not sr.id:
            sr.contact = request.user
            tweet_message.append("New series: %s!" % sr.primary_name)
            tweet_or_not = True

        old_sr = copy.deepcopy(sr) # need to create a copy because is_valid() will trigger model validation, which will update the model object with the new time values
        if form.is_valid():
            new_reading_list = []
            created_new = create_new_readings_list = False
            if not sr.id:
                # We are creating a new reading series, so 
                # create all its reading events for a year.
                created_new = True
                if sr.regular:
                    create_new_readings_list = True

            # If so, we will need to update its reading events.
            else:
                # We are updating an existing series. 
                
                # Depending on what changed, we may want to tweet about it, so start constructing
                # a tweet message.
                tweet_message.append("%s has been updated!" % old_sr.primary_name)
                tweet_or_not = False
                
                # If the name has changed, tweet about it:
                if form.cleaned_data["primary_name"] != old_sr.primary_name:
                    tweet_or_not = True
                    tweet_message.append("New name: %s" % sr.primary_name)
                
                # We are updating an existing reading series, so need to check if its time or regularity changed.               
                # Loop through items in sr and compare them to items in form.cleaned_data
                # to see if any of the date/times have changed.                 
                if old_sr.regular != form.cleaned_data["regular"] or old_sr.day_of_week != form.cleaned_data["day_of_week"] or old_sr.week_within_month != form.cleaned_data["week_within_month"] or old_sr.irregular_date_description != form.cleaned_data["irregular_date_description"] or old_sr.time != form.cleaned_data["time"] or old_sr.regular != form.cleaned_data["regular"] :
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
                    
                    tweet_or_not = True
                    tweet_message.append("New time.")

                if old_sr.venue.id != form.cleaned_data["venue"].id:
                    tweet_or_not = True
                    tweet_message.append("New venue: %s" % form.cleaned_data["venue"])
                    # The location has changed, so add that to the tweet.
                                    
            # If the series has a regular time, day of the week, and week of the month, and
            # it is new or its time has changed, then create new reading objects for the new year
            if create_new_readings_list: 
                new_reading_list = new_series_readings(sr)
                
            try:
                # First, save the new series.
                form.save()
                
                # Now if that was successful, tweet and save the tweet.
                if tweet_or_not:
                    # append shortened URL
                    api = bitlyapi.BitLy(settings.BITLY_USER, settings.BITLY_KEY) 
                    url = request.build_absolute_uri().replace("/edit", "")
                    res = api.shorten(longUrl=url)
                    tweet_message.append("%s" % res['url'])
                    send_msg = ' '.join(tweet_message)

                    try:
                        api = get_tweepy_api()
                        if settings.DEBUG:
                            print "tweeting %s" % send_msg
                        api.update_status(send_msg)
                        last_msg = api.user_timeline(count=1)[0]
                        if settings.DEBUG:
                            print "saving new tweet sr=%s, tweet=%s, url=%s, id=%s" % (sr, send_msg, res['url'], last_msg.id)
                        SeriesTweet.objects.create(
                            series = sr,
                            tweet = send_msg,
                            bitly_url = res['url'],
                            twitter_status_id = last_msg.id
                        )


                    except tweepy.TweepError as terror:
                        tweet_or_not = False # so we won't be able to save it to the DB
                        if settings.DEBUG:
                            print "tweep error: %s" % terror
                            
                    
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

            return HttpResponseRedirect(sr.get_absolute_url())
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
    """
    Uses a generic view to return a list of all the contacts on the site.
    This is deprecated, because in practice, this probably will not be used often or at 
    all. Any listing of contacts would be done by an admin from the admin site.
    Consider removing entirely.
    """
    return list_detail.object_list(request, queryset=User.objects.all(), template_name="generic_list.html")
    
def contact_detail(request, contact_id):
    """
    Presents the details of a particular contact.
    """
    c = get_object_or_404(User, pk=contact_id)
    return render_to_response('contact_detail.html', {'contact': c}, context_instance=RequestContext(request))
    
@login_required
def edit_contact(request, contact_id=None):
    """
    This is deprecated now that Contacts are Users. A user can only edit his/her own
    information, and they can do that through the account profile page.
    """
    if contact_id:
        c = get_object_or_404(User, pk=contact_id)
    else:
        c = User()
    if request.method == 'POST':
        form = ReadsrContactForm(request.POST, instance=c)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Updated %' % c)
            except ValueError:
                # need to figure out how to display more about this error
                messages.error(request, 'ValueError')
                return HttpResponseRedirect(reverse('series.views.contact_detail', args=(c.id,)))
    else:
        form = ReadsrContactForm(instance=c)    
    return render_to_response('edit_contact.html', {'form': form, 'contact': c}, context_instance=RequestContext(request))

# venue ########################
def venue_list(request):
    """
    Lists all the venues on the site. A better way to use this would be as a snipper
    that presents a list of series by venue.
    """
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
    
def venue_detail(request, venue_id):
    """
    Show the details of a venue, including a list of all the series happening there.
    """
    series_list = Series.objects.all()
    venue_series_list = series_list.filter(venue=venue_id)
    return render_to_response("venue_detail.html", { 'venue': Venue.objects.get(pk=venue_id), 'series_list': series_list, 'venue_series_list': venue_series_list}, context_instance=RequestContext(request))
    
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


# site_redirect ##############
def site_redirect(request):
    """
    Site_redirect is used for switching between different city_sites when javascript is disabled.
    """
    if request.method == "GET":
        new_site = request.GET.get('new_site', None)
        if not new_site.startswith("http://"):
            new_site = "".join(["http://", new_site])
        return redirect(urlparse(new_site).geturl())
 