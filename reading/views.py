from datetime import date, datetime, timedelta
from calendar import monthrange

import dateutil

from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.http import HttpResponse, HttpResponseRedirect, Http404

from reading.models import Reading
from reading.forms import ReadingForm

def named_month(month_number):
    """
    Return the name of the month, given the number.
    """
    return date(1900, month_number, 1).strftime("%B")
    
def this_month(request):
    """
    Show calendar of readings this month.
    """
    today = datetime.now()
    return calendar(request, today.year, today.month)
    
    
def calendar(request, year, month, series_id=None):
    """
    Show calendar of readings for a given month.
    """
    
    my_year = int(year)
    my_month = int(month)
    my_calendar_from_month = datetime(my_year, my_month, 1)
    my_calendar_to_month = datetime(my_year, my_month, monthrange(my_year, my_month)[1])

    if series_id:
        my_reading_events = Reading.objects.filter(series=series_id).filter(start_time__gte=my_calendar_from_month).filter(start_time__lte=my_calendar_to_month)
    else:
        my_reading_events = Reading.objects.filter(start_time__gte=my_calendar_from_month).filter(start_time__lte=my_calendar_to_month)

    my_previous_year = my_year
    my_previous_month = my_month - 1
    if my_previous_month == 0:
        my_previous_year = my_year - 1
        my_previous_month = 12
    my_next_year = my_year
    my_next_month = my_month + 1
    if my_next_month == 13:
        my_next_year = my_year + 1
        my_next_month = 1
    my_year_after_this = my_year + 1
    my_year_before_this = my_year - 1
    print "readings_list count is %d" % my_reading_events.count()
    return render_to_response("cal_template.html", { 'readings_list': my_reading_events,
                                                        'month': my_month,
                                                        'month_name': named_month(my_month),
                                                        'year': my_year,
                                                        'previous_month': my_previous_month,
                                                        'previous_month_name': named_month(my_previous_month),
                                                        'previous_year': my_previous_year,
                                                        'next_month': my_next_month,
                                                        'next_month_name': named_month(my_next_month),
                                                        'next_year': my_next_year,
                                                        'year_before_this': my_year_before_this,
                                                        'year_after_this': my_year_after_this,
    }, context_instance=RequestContext(request))
        
    


def list_readings(request, series_id=None, start_date=datetime.today(), end_date=datetime.today()+dateutil.relativedelta.relativedelta(months=1)):
    """
    Displays a list of all the readings in series series_id between start_date and end_date.
    If series_id is None, list all readings.
    """
    
    try: 
        if series_id:
            reading_list = Reading.objects.filter(series=series_id).filter(start_time__gte=start_date).filter(start_time__lte=end_date).order_by("date_and_time")
        else:
            reading_list = Reading.objects.filter(start_time__gte=start_date).filter(start_time__lte=end_date).order_by("date_and_time")
            
        return render_to_response('readings_index.html', {'reading_list': reading_list }, context_instance=RequestContext(request))
    except ValueError:
        raise Http404
        
def list_readings_month(request, series_id=None, num_months=1, ajax="0", index="0"):
    """
    Displays a list of all the readings for num_months months from today.
    """
    
    try: 
        reading_list = Reading.objects.filter(start_time__gte=datetime.today()).filter(start_time__lte=datetime.today()+timedelta(31*int(num_months.rstrip('/')))).order_by("date_and_time")
        if index=="0":
            whether_index = False
        else:
            whether_index = True
    
        if ajax=="1": # list_readings has not styles by itself
            return render_to_response('list_readings.html', {'reading_list': reading_list, 'index': whether_index }, context_instance=RequestContext(request))
        else: # readings_index is a wrapper so the page can stand on its own
            return render_to_response('readings_index.html', {'reading_list': reading_list, 'index': whether_index }, context_instance=RequestContext(request))
    except ValueError:
        raise Http404
    
def list_readings_date(request, year, month, date, series_id=None):
    """
    Displays a list of readings for a given date, for a calendar-style lookup.
    """
    try: 
        start_date = datetime(int(year), int(month), int(date), 0, 0, 0)
        end_date = datetime(int(year), int(month), int(date), 23, 59, 59)
        reading_list = Reading.objects.filter(start_time__gte=start_date).filter(start_time__lte=end_date).order_by("date_and_time")
        # .filter(series.site_id__eq=request.city_site.site_ptr_id)
        return render_to_response('readings_index.html', {'reading_list': reading_list }, context_instance=RequestContext(request))
    except ValueError:
        raise Http404
    
def detail_reading(request, series_id=None, reading_id=None):
    reading = get_object_or_404(Reading, pk=reading_id)
    return render_to_response("reading_detail.html", { 'reading': reading, }, context_instance=RequestContext(request))
    
@login_required
def edit_reading(request, reading_id=None):
    if request.is_ajax():
        if not request.method == "POST":
            raise Http404
            
        reading_id = request.POST["reading_id"]
        r = get_object_or_404(Reading, pk=reading_id)
        # import pdb; pdb.set_trace()
        if r.series.wiki_mode and r.series.contact != request.user:
            messages.add_message(request, messages.ERROR, "This series is not in wiki mode. Only the owner can edit readings.")
        else:
            try:
                r.description = request.POST["description"]
                r.full_clean()
                r.save()
            except ValidationError, e:
                for error in e.message_dict:
                    print "error=%s" % error
                messages.error(request, "There was an error validating your update.")

        return render_to_response('index.html', {}, context_instance=RequestContext(request))
            
    else: # not AJAX
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
                    messages.add_message(request, message.ERROR, 'Error %s reading.' % (created_new and "creating" or "updating", r.title))
                    return HttpResponseRedirect(reverse('edit-reading', args=(sr.id,)))
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = ReadingForm(instance=r)
    return render_to_response('edit_reading.html', {'form': form, 'reading': r}, context_instance=RequestContext(request))
        
    
def index(request, series_id=None):
    return HttpResponse("index")