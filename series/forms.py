from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField, USStateSelect, USZipCodeField
from datetime import time
from series.models import Series, Contact, Venue, Affiliate, Address
from contact_form.forms import ContactForm
from registration.forms import RegistrationFormUniqueEmail
from django.conf import settings
from city_site.models import CitySite

class SeriesForm(forms.ModelForm):
	primary_name = forms.CharField();
	secondary_name = forms.CharField(required=False);
	#contact = forms.
	#genre = 
	#venue
	regular = forms.BooleanField(required=False);
	irregular_date_description = forms.CharField(required=False, widget=forms.Textarea);
	#day_of_week
	#week_within_month
	time = forms.TimeField(
		input_formats=('%H:%M', '%I:%M %p', '%I %p', '%H.%M', '%I.%M %p'), 
		widget=forms.TimeInput(format=r"%I:%M %p",), 
		help_text="HH:MM AM/PM",
		initial=time(18))
	#affiliation
	affiliations = forms.ModelMultipleChoiceField(
	                        queryset=Affiliate.objects.all(),
	                        widget=forms.CheckboxSelectMultiple(),
							required=False)
	
	admission = forms.BooleanField(required=False)
	admission_description = forms.CharField(required=False)
	notes = forms.CharField(required=False)
	wiki_mode = forms.BooleanField(required=False)
	#site = forms.ModelChoiceField(required=True, queryset=CitySite.objects.all(), initial=settings.SITE_ID, widget=forms.HiddenInput())
	
	class Meta:
		model = Series
		exclude = ('last_update', 'created', 'site', 'contact')
		
	class Media:
		css = {
			'screen': ('js/timePicker/timePicker.css',)
		}
		js = ('js/timePicker/jquery.timePicker.min.js',)

# a form for changing a Contact (person), named so as not to conflict with the library class for sending messages via a ContactForm
class ReadsrContactForm(forms.ModelForm):
	first_name = forms.CharField()
	last_name = forms.CharField()
	email = forms.CharField()

	class Meta:
		model = Contact	

# need to figure out how to get this to display the associated address as well
class VenueForm(forms.Form):
	name = forms.CharField()
	phone = USPhoneNumberField(required=False)
	#notes = forms.CharField()
	website = forms.URLField(required=False)
	in_dc = forms.BooleanField(required=False)

#	class Meta:
#		model = Venue
#		exclude = ('secondary_name', 'notes')

class AddressForm(forms.Form):
	street_address = forms.CharField()
	city = forms.CharField()
	#state = USStateSelect()
	state = forms.CharField()
	zipcode = USZipCodeField()
	
	class Meta:
		model = Address
		
class AffiliateForm(forms.ModelForm):
	class Meta:
		model = Affiliate
		
# custom class for sending a message about removing a particular series
class RemoveSeriesContactForm(ContactForm):
	
	def __init__(self, data=None, files=None, request=None, username=None, name=None, email=None, *args, **kwargs):
		super(RemoveSeriesContactForm, self).__init__(data=data, files=files, request=request, *args, **kwargs)
		#self.username.intial = username
		#self.email.initial = email
		#self.name = name

	name = forms.CharField(widget=forms.HiddenInput(), required=False)
	username = forms.CharField(widget=forms.HiddenInput(), required=False)
	email = forms.EmailField(widget=forms.HiddenInput(), required=False)
	series_id = forms.IntegerField(widget=forms.HiddenInput())
	series_primary_name = forms.CharField(widget=forms.HiddenInput())

# custom class for registering with first names and last names
class FullNameRegistrationForm(RegistrationFormUniqueEmail):
	first_name = forms.CharField(widget=forms.TextInput(), required=False)
	last_name = forms.CharField(widget=forms.TextInput(), required=False)
