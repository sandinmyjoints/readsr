from datetime import time

from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField, USStateSelect, USZipCodeField
from django.contrib.auth.models import User
from django.conf import settings

from swingtime.models import EventType

from series.models import Series, Venue, Affiliate, Address, Contact
from contact_form.forms import ContactForm
from registration.forms import RegistrationFormUniqueEmail
from city_site.models import CitySite


class SeriesForm(forms.ModelForm):
    regular = forms.BooleanField(required=False);
    irregular_date_description = forms.CharField(required=False, widget=forms.Textarea);
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
    
    # Hidden fields
    contact = forms.ModelChoiceField(queryset=Contact.objects.all(),
                widget=forms.HiddenInput)
    event_type = forms.IntegerField(widget=forms.HiddenInput, initial=EventType.objects.get(pk=1).id) # TODO make this nicer. right it just supplies 1 for the default event_type, Reading Series
    city_site = forms.IntegerField(widget=forms.HiddenInput, initial=CitySite.objects.get(pk=settings.SITE_ID).id)
    
    class Meta:
        model = Series
        #exclude = ('site', 'contact')
        
    class Media:
        css = {
            'screen': ('js/timePicker/timePicker.css',)
        }
        js = ('js/timePicker/jquery.timePicker.min.js',)

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