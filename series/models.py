from django.db import models
from django.db.models import permalink
from django.contrib.localflavor.us.models import PhoneNumberField, USStateField
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, time, timedelta
#from django.contrib.sites.models import Site

from city_site.models import CitySite


class Contact(models.Model):
	"""
	Represents a person who can be contacted about a particular reading series. Currently 
	associated one-to-one with a user in the system.
	"""
	# If we wanted to disassociate a contact from a particular user--for example, to let
	# someone be a user in the system but create a new reading series and designate someone
	# else as the contact, we could uncomment these fields and comment out the 
	# OneToOneField to a user object. That way, a contact would exist separately, outside
	# the users system.
	#first_name = models.CharField("First Name", max_length=50)
	#last_name = models.CharField("Last Name", max_length=50)
	#email = models.CharField(max_length=70)
	# By associating a contact with a user in the system, we assure that people can't create
	# a new series and designate some arbitrary person as the contact, which would mean they
	# would get emails from the system when somesone requested the series be deleted, etc.
	# This way, a user can only create a series with themself as the contact.
	user = models.OneToOneField(User)
	
	def _get_first_name(self):
		return self.user.first_name
		
	first_name = property(_get_first_name)
		
	def _get_last_name(self):
		return self.user.last_name
		
	last_name = property(_get_last_name)
		
	def _get_email(self):
		return self.user.email
		
	email = property(_get_email)
		
	def _get_full_name(self):
		# Returns the contact's full name.
		return u'%s %s' % (self.first_name, self.last_name)

	full_name = property(_get_full_name)
		
	def __unicode__(self):
		return self.full_name
		
	
class Genre(models.Model):
	"""
	Represents the genre of writing available at a given reading.
	The built-in choices are fiction, poetry, and non-fiction. They are loaded into the 
	database by fixtures at installation.
	"""
	GENRE_CHOICES = (
	('F', 'Fiction'),
	('P', 'Poetry'),
	('N', 'Non-fiction')
	)
	
	genre = models.CharField(max_length=1, choices=GENRE_CHOICES)
	def __unicode__(self):
		for genrepair in self.GENRE_CHOICES:
			if self.genre in genrepair:
				return genrepair[1];
				
		# this should only happen if all the genres were not added to the db
		print "Self.genre = %s, was not in self.GENRE_CHOICES. Did you add all the genres to the database?" % self.genre
		return self.genre

class Address(models.Model):
	"""
	Represents a street address in the United States. Used by Venue.
	"""
	street_address = models.CharField(max_length=100)
	city_name = models.CharField(max_length=100)
	state = USStateField()
	zip_code = models.CharField(max_length=5)
	def __unicode__(self):
		return self.street_number + " " + self.street_name + " " + self.zip_code
		
		
	def _get_city_address(self):
		return self.city_name + ", " + self.state
		
	city_address = property(_get_city_address)
	
	class Meta(object):
		verbose_name_plural = 'Addresses'
	
class Venue(models.Model):
	"""
	Represents the location of a reading series. Associated with an Address.
	"""
	name = models.CharField(max_length=100)
	secondary_name = models.CharField(max_length=100, blank=True, null=True)
	#address = models.CharField(max_length=200)
	address = models.OneToOneField(Address)
	phone = PhoneNumberField(blank=True, null=True)
	notes = models.CharField(max_length=200, blank=True, null=True)
	website = models.URLField(blank = True, null = True)
	in_dc = models.BooleanField("In DC?")
	def __unicode__(self):
		return self.name
		
class Affiliate(models.Model):
	"""
	Represents an organization with which a reading series can optionally be affiliated.
	"""
	name = models.CharField(max_length=100)
	website = models.URLField(blank = True, null = True)
	def __unicode__(self):
		return self.name
				
class DayOfWeek(models.Model):
	"""
	Represents a day of the week (on which a reading series can take place). 
	Because the dates of reading series are often designated by terms like 'first Monday'
	or 'third Friday', this field is useful in determining on which dates individual
	readings take place.
	"""
	days =[ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
	       'Sunday' ]
	
	DAYS_OF_WEEK_CHOICES = (
	('MO', days[0]),
	('TU', days[1]),
	('WE', days[2]),
	('TH', days[3]),
	('FR', days[4]),
	('SA', days[5]),
	('SU', days[6]),
	)
	
	day = models.CharField(max_length=2, choices=DAYS_OF_WEEK_CHOICES)
	def __unicode__(self):
		for daypair in self.DAYS_OF_WEEK_CHOICES:
			if self.day in daypair:
				return daypair[1]

		# this shouldn't happen
		print "self.day = %s, was not in DAY_OF_WEEK_CHOICES. Did you add all the days of the week to the database?" % self.day
		return self.day
		
	# my_next_day_of_the_week returns a datetime equal to the start (midnight+min) of the next day that is this instance's day of the week.
	# it doesn't know what time the reading is, so if today is the day of the week the reading falls on,
	# it simply returns today rather than checking whether the reading time has passed already.
	# so we need to check for that outside of this method. 
	def my_next_day_of_the_week(self):
		""" Returns a datetime equal to the start of the next day that is this instance's day of the week. """
		# need to find the number of the current day of the week
		today_day = datetime.today().weekday()
		reading_day = self.days.index(self.__unicode__())
		next_day = datetime.today().date()
		
		if today_day < reading_day:
			next_day = next_day + timedelta(reading_day-today_day)
		elif today_day > reading_day:
			next_day = next_day + timedelta(7-today_day)
		
		return next_day
	
	class Meta(object):
		verbose_name_plural = 'DaysOfWeek'

class WeekWithinMonth(models.Model):
	"""
	Represents a week within the month. See note under DayOfTheWeek for why this is 
	useful for tracking when individual readings take place.
	Fifth is exceedingly unlikely to be used by
	any real reading series.
	"""
	WEEK_WITHIN_MONTH_CHOICES = (
	('1', 'First'),
	('2', 'Second'),
	('3', 'Third'),
	('4', 'Fourth'),
	('5', 'Fifth'),
	)
	
	week_within_month = models.CharField(max_length=1, choices=WEEK_WITHIN_MONTH_CHOICES)
	def __unicode__(self):
		for weekpair in self.WEEK_WITHIN_MONTH_CHOICES:
			if self.week_within_month in weekpair:
				return "The %s" % weekpair[1];

		# this will happen if all the choices haven't been added but should not happen otherwise
		print "self.week_within_month = %s, was not in WEEK_WITHIN_MONTH_CHOICES. Did you add all the weeks of the month to the database?" % self.week_within_month
		return self.week_within_month
				
	class Meta(object):
		verbose_name_plural = 'WeeksWithinMonth'
		
class Series(models.Model):
	"""
	Represents one reading series, defined as a recurring event at a particular
	location on a particular day of a particular week within a month at which
	people read out loud from literary works of certain genres.
	"""
	primary_name = models.CharField("Reading Name", max_length=200, unique=True)
	secondary_name = models.CharField("Reading Secondary Name", max_length=200, blank=True, null=True)
	contact = models.ForeignKey(Contact)
	genre = models.ManyToManyField(Genre)
	venue = models.ForeignKey(Venue)
	regular = models.BooleanField("Regular", default=True)
	irregular_date_description = models.CharField("Date and Time", max_length=200, blank=True, null=True)
	day_of_week = models.ForeignKey(DayOfWeek, blank=True, null=True)
	week_within_month = models.ForeignKey(WeekWithinMonth, blank=True, null=True)
	time = models.TimeField(default=time(18))
	affiliations = models.ManyToManyField(Affiliate, blank=True, null=True)
	website = models.URLField(blank=True, null=True)
	admission = models.BooleanField("Admission", default=False)
	admission_description = models.CharField("Admission", max_length=300, blank=True, null=True)
	notes = models.CharField("Notes", max_length=300, blank=True, null=True)
	wiki_mode = models.BooleanField("Wiki Mode", default=True)
	created = models.DateTimeField(default=datetime.now)
	last_update = models.DateTimeField("Last Updated", default=datetime.now)
	site = models.ForeignKey(CitySite, default=CitySite.objects.get(pk=settings.SITE_ID))
 
	def __unicode__(self):
		return self.primary_name
		
	@models.permalink
	def get_absolute_url(self):
		return ('detail-series', (), { 
			'series_id': self.id })
		
	def next_reading_day(self):
		""" Return the date of the next instance of this reading (assumes reading is monthly) """

		today = datetime.today().date()
		next_reading_day = self.day_of_week.my_next_day_of_the_week()

		# need to find the right day of the right month
		# take a day of the week, and a week of the month. figure out if that
		# day/week has already happened this month. if not, that's it. if yes,
		# then add weeks until we get that day/week next month.
		which_week = int(self.week_within_month.week_within_month)

		# count backwards to get the reading day in the last week of the previous month
		while next_reading_day.month == today.month:
			next_reading_day = next_reading_day - timedelta(7)

		# now add which_week weeks to it to get the day of the reading this month
		this_month_reading_day = next_reading_day = next_reading_day + timedelta(7*(which_week))

		# if this month's reading day has passed, add time to get to the next month
		if this_month_reading_day < today:
			# this while loop gives us the first reading_day of the next month
			while next_reading_day.month == today.month:
				next_reading_day = next_reading_day + timedelta(7)
			# this gives us the which_weekth reading_day of the next month, which is what we want
			next_reading_day = next_reading_day + timedelta(7*(which_week-1))
		
		return next_reading_day
		
	def reading_days_ahead_by_month(self, months_ahead=0):
		""" Returns a list of reading days up to months_ahead months ahead. If month_ahead is 0, returns this month's reading day. """

		my_next_reading_day = self.next_reading_day()
		my_ahead_readings = [my_next_reading_day]
		if months_ahead <= 0:
			return my_ahead_readings 
			
		which_week = int(self.week_within_month.week_within_month)		
		limit_date = datetime.today().date() + timedelta(months_ahead * 31)

		while my_next_reading_day <= limit_date:
		#for counter in range(months_ahead):
			# advance by week to get to the first occurence of the next month
			cur_month = my_next_reading_day.month
			while my_next_reading_day.month == cur_month: 
				my_next_reading_day = my_next_reading_day + timedelta(7)

			# once we are at the first week of the right month, advance to the right week of this month
			my_ahead_readings.append(my_next_reading_day + timedelta(7*(which_week-1)))

		return my_ahead_readings
				
	class Meta:
		ordering = ('primary_name',)
		verbose_name_plural = 'Series'
