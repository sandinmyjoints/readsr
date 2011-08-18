from datetime import datetime, date, time, timedelta

from django.db import models
from django.db.models import permalink
from django.contrib.localflavor.us.models import PhoneNumberField, USStateField
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from dateutil import rrule

from picklefield.fields import PickledObjectField

from swingtime.models import Event

from city_site.models import CitySite
import reading

class ModelBase(models.Model):
    """ Abstract base model that provides some timestamps. """
    
    created_on = models.DateTimeField(auto_now_add=True, default=datetime.now)
    updated_on = models.DateTimeField(auto_now=True, default=datetime.now)
    
    class Meta:
        abstract = True
        
class InvalidGenreError(Exception):
    pass    
    
class Genre(ModelBase):
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
                
        # This should only happen if all the genres were not added to the db from the fixture.
        raise InvalidGenreError, "Self.genre = %s, was not in self.GENRE_CHOICES. Did you add all the genres to the database?" % self.genre
        

class Address(ModelBase):
    """
    Represents a street address in the United States. Used by Venue.
    """
    street_address = models.CharField(max_length=100)
    city_name = models.CharField(max_length=100)
    state = USStateField()
    zip_code = models.CharField(max_length=5)
    def __unicode__(self):
        return " ".join([self.street_address, self.city_name, self.state, self.zip_code])
                
    def _get_city_address(self):
        return self.city_name + ", " + self.state
        
    city_address = property(_get_city_address)
    
    class Meta(object):
        verbose_name_plural = 'Addresses'
    
class Venue(ModelBase):
    """
    Represents the location of a reading series. Associated with an Address.
    """
    name = models.CharField(max_length=100)
    secondary_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.OneToOneField(Address)
    phone = PhoneNumberField(blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(blank = True, null = True)
    in_dc = models.BooleanField("In DC?")
    def __unicode__(self):
        return self.name
        
class Affiliate(ModelBase):
    """
    Represents an organization with which a reading series can optionally be affiliated.
    """
    name = models.CharField(max_length=100)
    website = models.URLField(blank = True, null = True)
    def __unicode__(self):
        return self.name
        
class InvalidDayOfWeekError(Exception):
    pass
        
class DayOfWeek(ModelBase):
    """
    Represents a day of the week (on which a reading series can take place). 
    Because the dates of reading series are often designated by terms like 'first Monday'
    or 'third Friday', this field is useful in determining on which dates individual
    readings take place.
    """

    # The pk in the db is 1-indexed (Monday=1, Tuesday=2, etc), but python's days 
    # of the week are 0-indexed if you use .weekday(), so we are using .isoweekday()
    # instead. 
    days =[ '', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
           'Sunday' ]

    DAYS_OF_WEEK_CHOICES = (
    ('MO', days[1]),
    ('TU', days[2]),
    ('WE', days[3]),
    ('TH', days[4]),
    ('FR', days[5]),
    ('SA', days[6]),
    ('SU', days[7]),
    )
    
    day = models.CharField(max_length=2, choices=DAYS_OF_WEEK_CHOICES)
    
    def __unicode__(self):
        for daypair in self.DAYS_OF_WEEK_CHOICES:
            if self.day in daypair:
                return daypair[1]

        # This shouldn't happen unless the days of the week were not loaded from the fixture.
        raise InvalidDayOfWeekError, "self.day = %s, was not in DAY_OF_WEEK_CHOICES. Did you add all the days of the week to the database?" % self.day
        
    # next_my_day_of_week returns a datetime equal to the start (midnight+min) of the next day that is this instance's day of the week.
    # It doesn't know what time the reading is, so if today is the day of the week the reading falls on,
    # it simply returns today rather than checking whether the reading time has passed already.
    # So we need to check for that outside of this method. 
    def next_my_day_of_week(self):
        """ 
        Returns a date equal to the start of the next day that is this instance's day of the week. 
        """
        
        # Find the number of the current day of the week
        today_day = date.today().isoweekday() 
        reading_day = self.days.index(self.__unicode__()) 
        next_day = date.today() 
        while next_day.isoweekday() != reading_day:
            next_day = next_day + timedelta(1)
                
        return next_day
    
    class Meta(object):
        verbose_name_plural = 'DaysOfWeek'

class InvalidWeekWithinMonthError(Exception):
    pass
    
class WeekWithinMonth(ModelBase):
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

        # This will only happen if all the choices haven't been added from the fixture.
        raise InvalidWeekWithinMonthError, "self.week_within_month = %s, was not in WEEK_WITHIN_MONTH_CHOICES. Did you add all the weeks of the month to the database?" % self.week_within_month
                
    class Meta(object):
        verbose_name_plural = 'WeeksWithinMonth'

class UnknownNextReadingDayException(Exception):
    pass

class Contact(ModelBase):
    """
    Represents a person who can be contacted about a particular reading series. Currently 
    associated one-to-one with a django User object (a user of the system).

    By associating a contact with a user in the system, we assure that people can't create
    a new series and designate some arbitrary person as the contact, which would mean they
    would get emails from the system when someone requested the series be deleted, etc.
    This way, a user can only create a series with themself as the contact.
    """

    user = models.OneToOneField(User)

    @permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })

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
        return u'%d' % self.id

    def create_contact(sender, instance, created, **kwargs):  
        if created:  
           profile, created = Contact.objects.get_or_create(user=instance)  

    post_save.connect(create_contact, sender=User)
        
class Series(Event):
    """
    Represents one reading series, defined as a recurring event at a particular
    location on a particular day of a particular week within a month.
    """
    
    created_on = models.DateTimeField(auto_now_add=True, default=datetime.now)
    updated_on = models.DateTimeField(auto_now=True, default=datetime.now)
    #primary_name = models.CharField("Reading Name", max_length=200, unique=True) # replaced by Event.title
    #secondary_name = models.CharField("Reading Secondary Name", max_length=200, blank=True, null=True) # deprecated
    contact = models.ForeignKey(User)
    genre = models.ManyToManyField(Genre)
    venue = models.ForeignKey(Venue)
    regular = models.BooleanField("Regular", default=True)
    irregular_date_description = models.CharField("Date and Time", max_length=200, blank=True, null=True)
    #day_of_week = models.ForeignKey(DayOfWeek, blank=True, null=True)
    #week_within_month = models.ForeignKey(WeekWithinMonth, blank=True, null=True)
    #time = models.TimeField(default=time(18))
    affiliations = models.ManyToManyField(Affiliate, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    admission = models.BooleanField("Admission", default=False)
    admission_description = models.CharField("Admission", max_length=300, blank=True, null=True)
    #notes = models.CharField("Notes", max_length=300, blank=True, null=True)
    wiki_mode = models.BooleanField("Wiki Mode", default=True)
    site = models.ForeignKey(CitySite)
    rrule = PickledObjectField("Recurrence Rule", blank=True, null=True) # Save the recurrence rule for this Series as a pickled object in the db

    def __unicode__(self):
        return self.title
        
    @models.permalink
    def get_absolute_url(self):
        return ('detail-series', (), { 'series_id': self.id } )
     
    def recurrence_rule(self):
        """
        Returns a nice description of the recurrence rule for this Series.
        """
        
        # drop the last two elements which are "until end_date"
        return ' '.join(self.rrule.text()[:-2])
        
    def add_occurrences(self, start_time, end_time, **rrule_params):
        '''
        Override the Event add_occurrences method to create Reading objects instead
        of Occurrence objects.
        
        Add one or more occurences to the event using a comparable API to 
        ``dateutil.rrule``. 
        
        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.
        
        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.
        
        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        '''
        rrule_params.setdefault('freq', rrule.MONTHLY)
        
        if 'count' not in rrule_params and 'until' not in rrule_params:
            # This shouldn't happened. TODO change to an assertion
            self.reading_set.create(start_time=start_time, end_time=end_time)
        else:
            delta = end_time - start_time
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                self.reading_set.create(start_time=ev, end_time=ev + delta, event_id=self.id)
        
    # def next_reading_day(self):
    #     """ 
    #     Return the date of the next instance of this reading.
    #     Series can only know this if it is a regular event that occurs on the same
    #     day of each month.
    #     """
    # 
    #     if not self.regular:
    #         raise UnknownNextReadingDayException, "Series %s is irregular. Cannot determine next reading date."
    # 
    #     one_week = timedelta(7)
    #     today = date.today()
    # 
    #     # To find the next day that this series has a reading event, first we get 
    #     # the date of the next occurence of the day of the week that this series
    #     # happens on (e.g., the date of the next Monday if this series happens on 
    #     # Mondays).
    #     next_reading_day = self.day_of_week.next_my_day_of_week()
    #     
    #     # Next we need to find the right day of the right month--either this month 
    #     # if the next reading day hasn't happened yet this month, or next month if it has.
    # 
    #     # First, subtract until we get to the last reading day of the previous month as
    #     # a starting point.
    #     while next_reading_day.month == today.month:
    #         next_reading_day = next_reading_day - one_week
    # 
    #     # Next get the week within the month the reading day occurs 
    #     # (e.g., the first week within the month).
    #     which_week = int(self.week_within_month.week_within_month)
    # 
    #     # Now add which_week weeks to get the day of the reading this month.
    #     this_month_reading_day = next_reading_day = next_reading_day + timedelta(7*(which_week))
    # 
    #     # If this month's reading day has passed, add time until we get to next month's reading day.
    #     if this_month_reading_day < today:
    #         # This loop gives us the first reading_day of the next month.
    #         while next_reading_day.month == today.month:
    #             next_reading_day = next_reading_day + one_week
    #         # This addition us the which_weekth reading_day of the next month, which is what we want.
    #         next_reading_day = next_reading_day + timedelta(7*(which_week-1))
    #     
    #     return next_reading_day
    #     
    # def reading_days_ahead_by_month(self, months_ahead=0):
    #     """ Returns a list of reading days up to months_ahead months ahead. If month_ahead is 0, returns the next reading day. """
    # 
    #     my_next_reading_day = self.next_reading_day()
    #     my_ahead_readings = [my_next_reading_day]
    #     if months_ahead <= 0:
    #         return my_ahead_readings 
    #         
    #     which_week = int(self.week_within_month.week_within_month)      
    #     limit_date = datetime.today().date() + timedelta(months_ahead * 31)
    # 
    #     while my_next_reading_day <= limit_date:
    #         # Advance by week to get to the first occurence of the next month
    #         cur_month = my_next_reading_day.month
    #         while my_next_reading_day.month == cur_month: 
    #             my_next_reading_day = my_next_reading_day + timedelta(7)
    # 
    #         # Once we are at the first week of the right month, advance to the right week of this month
    #         my_ahead_readings.append(my_next_reading_day + timedelta(7*(which_week-1)))
    # 
    #     return my_ahead_readings
    # 
    # def get_future_readings(self, years=1):
    #     """
    #     Returns a list of Reading objects for a given Series for a number of years ahead.
    # 
    #     ** Arguments **
    # 
    #     ``years``
    #         The number of years ahead to create Reading objects for for this series.
    #     """
    # 
    #     new_reading_list = []
    # 
    #     for reading_day in self.reading_days_ahead_by_month(12*years):
    #         r = reading.models.Reading()
    #         r.start_time = datetime.combine(reading_day, self.time)
    #         r.series = self
    #         new_reading_list.append(r)
    # 
    #     return new_reading_list
    #             
    # class Meta:
    #     ordering = ('title',)
    #     verbose_name_plural = 'Series'
    
class SeriesTweet(ModelBase):
    """
    Represents a tweet about a reading series.
    """
    
    series = models.ForeignKey(Series, null=True)
    tweet = models.CharField(max_length=140)
    bitly_url = models.URLField()
    twitter_status_id = models.CharField(max_length=20)

    def __unicode__(self):
        return self.tweet
