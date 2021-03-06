from datetime import datetime, time, timedelta
from dateutil import rrule

from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField, USStateSelect, USZipCodeField
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import swingtime
from swingtime.models import EventType
from swingtime.forms import MultipleOccurrenceForm, SECONDS_INTERVAL

from rrule2text import rrule2text as rr2t

from series.models import Series, Venue, Affiliate, Address, Contact
from contact_form.forms import ContactForm
from registration.forms import RegistrationFormUniqueEmail
from city_site.models import CitySite

class DifferentlySizedTextarea(forms.Textarea):
  def __init__(self, *args, **kwargs):
    attrs = kwargs.setdefault('attrs', {})
    attrs.setdefault('cols', 40)
    attrs.setdefault('rows', 3)
    super(DifferentlySizedTextarea, self).__init__(*args, **kwargs)
    
class SeriesForm(forms.ModelForm):
    regular = forms.BooleanField(required=False)
    irregular_date_description = forms.CharField(required=False, widget=DifferentlySizedTextarea)
    # time = forms.TimeField(
    #     input_formats=('%H:%M', '%I:%M %p', '%I %p', '%H.%M', '%I.%M %p'), 
    #     widget=forms.TimeInput(format=r"%I:%M %p",), 
    #     help_text="HH:MM AM/PM",
    #     initial=time(18))
    affiliations = forms.ModelMultipleChoiceField(
                            queryset=Affiliate.objects.all(),
                            widget=forms.CheckboxSelectMultiple(),
                            required=False)
    
    admission = forms.BooleanField(required=False)
    admission_description = forms.CharField(required=False)
    notes = forms.CharField(required=False)
    wiki_mode = forms.BooleanField(required=False)
    description = forms.CharField(required=True, widget=DifferentlySizedTextarea)

    class Meta:
        model = Series
        exclude = ('site', 'contact', 'event_type') # These will be saved when the new instance is saved in the view
        
    class Media:
        css = {
            'screen': ('js/timePicker/timePicker.css',)
        }
        js = ('js/timePicker/jquery.timePicker.min.js',)

class MonthlyReadingMultipleOccurrenceForm(MultipleOccurrenceForm):
    """
    Defaults to monthly occurrences.
    """
    
    def __init__(self, *args, **kws):
        # TODO write a version of init that takes a Series and sets the form to the rrule values of that Series.
        
        super(MonthlyReadingMultipleOccurrenceForm, self).__init__(*args, **kws)

        today = datetime.today().date()
        self.fields["until"].initial = datetime(today.year+2, today.month, today.day)
        self.fields["repeats"].initial = "until"
        self.fields["freq"].initial = rrule.MONTHLY
        self.fields["freq"].label = "What day?"
        self.fields["start_time_delta"].label = "What time?"
        self.fields["repeats"].label = "End date in mind?"
        self.fields["month_option"].initial = "on"
        self.fields["day"].label = _(u"Date of next reading")
        self.fields["day"].required = False
        self.fields["freq"].required = False
        self.fields["month_option"].required = False
        self.fields["year_month_ordinal"].required = False
        self.fields["year_month_ordinal_day"].required = False
        self.fields["end_time_delta"].required = False
        
    def clean(self):
        self.cleaned_data["day"] = datetime.today().date()
        offset = self.cleaned_data["start_time_delta"]
        self.cleaned_data["end_time_delta"] = offset + SECONDS_INTERVAL
        self.cleaned_data["freq"] = rrule.MONTHLY
        self.cleaned_data["month_option"] = "on"
        
        return super(MonthlyReadingMultipleOccurrenceForm, self).clean()

    def save(self, series):        
        """
        returns the Event these readings are associated with
        """
        
        # This creates the occurences by calling Event.add_occurrences and gives them the series as a foreign key. It does not
        # save the series.
        super(MonthlyReadingMultipleOccurrenceForm, self).save(series)
        
        # this code also appears in the super save method, but params is local so 
        # we don't have access to it here. but we need params to save as part of the
        # series.
        if self.cleaned_data['repeats'] == 'no':
             params = {}
        else:
             params = self._build_rrule_params()        
             
        # We need to use params to generate the rrule which we will save to the db
        # as part of the series. We need it to use when describing this series.
        series.rrule = rr2t(dtstart=self.cleaned_data['start_time'], **params)
        series.save()
        
        return series
        
    def get_rrule(self):
        if not self.cleaned_data:
            return None
            
        if self.cleaned_data.has_key("repeats") and self.cleaned_data["repeats"] == "no":
            params = {}
        else: 
            params = self._build_rrule_params() 
            
        return rr2t(dtstart=self.cleaned_data['start_time'], **params)

class ReadsrContactForm(forms.ModelForm):
    """
    A form for changing a contact (person), named so as not to conflict with the library class for sending messages via a ContactForm
    """
    
    class Meta:
        model = User    

class VenueForm(forms.Form):
    name = forms.CharField()
    phone = USPhoneNumberField(required=False)
    website = forms.URLField(required=False)
    in_dc = forms.BooleanField(required=False)


class AddressForm(forms.Form):
    street_address = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    zipcode = USZipCodeField()
    
    class Meta:
        model = Address
        
class AffiliateForm(forms.ModelForm):
    my_type = "Afilliate"
    class Meta:
        model = Affiliate
        
class RemoveSeriesContactForm(ContactForm):
    """
    Custom contact form for a user to send a message about removing a particular series.
    """
    
    def __init__(self, data=None, files=None, request=None, username=None, name=None, email=None, *args, **kwargs):
        super(RemoveSeriesContactForm, self).__init__(data=data, files=files, request=request, *args, **kwargs)

    name = forms.CharField(widget=forms.HiddenInput(), required=False)
    username = forms.CharField(widget=forms.HiddenInput(), required=False)
    email = forms.EmailField(widget=forms.HiddenInput(), required=False)
    series_id = forms.IntegerField(widget=forms.HiddenInput())
    series_primary_name = forms.CharField(widget=forms.HiddenInput())

class FullNameRegistrationForm(RegistrationFormUniqueEmail):
    """
    Custom class for registering a user with first names and last names.
    Inherits from the RegistrationFormUniqueEmail form from django-registration.
    """
    first_name = forms.CharField(widget=forms.TextInput(), required=False)
    last_name = forms.CharField(widget=forms.TextInput(), required=False)

class ProfileForm(forms.ModelForm):
    """
    Custom form class to allow users to edit their email address and name through 
    django-profiles.
    """

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        try:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        except User.DoesNotExist as ex:
            if settings.DEBUG:
                print "In ProfileForm constructor: %s" % ex
            pass


    email = forms.EmailField(label="Primary email", help_text='Your primary email address')
    first_name = forms.CharField(widget=forms.TextInput(), required=False)
    last_name = forms.CharField(widget=forms.TextInput(), required=False)

    class Meta:
        model = Contact 
        exclude = ('user',)        

    def save(self, *args, **kwargs):
        """
        Update the primary email address and names on the related User object as well.
        """
        u = self.instance.user
        u.email = self.cleaned_data['email']
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        u.save()
        profile = super(ProfileForm, self).save(*args,**kwargs)
        return profile