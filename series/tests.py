from datetime import date
import mock

from django.test import TestCase, Client
from django.contrib.auth.models import User

from series.models import Series, WeekWithinMonth, DayOfWeek, InvalidDayOfWeekError, InvalidWeekWithinMonthError
from series.views import about

class Authenticator():
    def __init__(self):
        self.user = None
        self.client = None

    def create_user(self):
        u = User()
        u.username = "test_user"
        u.set_password("test1")
        u.email = "test@test.com"
        u.save()
        
    def login_valid_user(self):
        self.client = Client()

        self.client.login(username="test_user", password="test1")

        
class TestAbout(TestCase):
    """
    Test the about page.
    """

    # Load test data that creates a user
    fixtures = ['test-readsr'] 
    
    def setup(self):
        self.auth = Authenticator()
        auth.create_user()
        
    def test_createuser(self):
        # self.auth.create_user()        
        setup()
        self.assertEquals(auth.user.username, "test_user")
        self.assertEquals(auth.user.email, "test@test.com")        
        
    def test_login_valid_user(self):
        # self.auth.login_valid_user()
        auth = Authenticator()
        auth.login_valid_user()
        
    def test_login_invalid_user(self):
        auth = Authenticator()
        response = auth.client.login(username="Noname", password="Nopassword")
        self.assertEquals(response, False)
        
    # def test_unauthenticated_edit(self):
    #     pass
        
    def test_about_page(self):
        # response = self.auth.client.get("/about/")
        auth = Authenticator()
        auth.client.get("/about/")
        self.assertEquals(response.status_code, 200)
    

class FakeDate(date):
	"""A fake replacement for date that can be mocked for testing."""
	def __new__(cls, *args, **kwargs):
		return date.__new__(date, *args, **kwargs)

class TestDayOfWeek(TestCase):
	"""Test the day of the week functions from series.models DayOfWeek."""

	@mock.patch('series.models.date', FakeDate)
	def test_valid_my_next_day_of_week_sameday(self):
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 3)) # July 3, 2011 is a Sunday
		new_day_of_week = DayOfWeek.objects.create()
		new_day_of_week.day = "SU"
		self.assertEquals(new_day_of_week.my_next_day_of_week(), date(2011, 7, 3))
				
	@mock.patch('series.models.date', FakeDate)
	def test_valid_my_next_day_of_week_nextday(self):
		pass
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 4)) # July 4, 2011 is a Monday
		new_day_of_week = DayOfWeek.objects.create()
		new_day_of_week.day = "SU"
		self.assertEquals(new_day_of_week.my_next_day_of_week(), date(2011, 7, 10))
		
	@mock.patch('series.models.date', FakeDate)
	def test_valid_my_next_day_of_week_previousday(self):
		pass
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 2)) # July 2, 2011 is a Saturday
		new_day_of_week = DayOfWeek.objects.create()
		new_day_of_week.day = "SU"
		self.assertEquals(new_day_of_week.my_next_day_of_week(), date(2011, 7, 3))

	def test_invalid_my_next_day_of_week(self):
		new_day_of_week = DayOfWeek.objects.create()
		new_day_of_week.day = "MT"
		self.assertRaises(InvalidDayOfWeekError, new_day_of_week.my_next_day_of_week)

	def test_invalid_my_next_day_of_week_blank(self):
		new_day_of_week = DayOfWeek.objects.create()
		new_day_of_week.day = ""
		self.assertRaises(InvalidDayOfWeekError, new_day_of_week.my_next_day_of_week)

class WeekWithinMonthTestCase(TestCase):
	"""
	Test the WeekWithinMonth model from series.models.
	"""
	def test_valid_week_within_month(self):
		w = WeekWithinMonth.objects.create()
		w.week_within_month = "1"
		self.assertEquals(w.__unicode__(), "The First")
		
	def test_invalid_week_within_month(self):
		w = WeekWithinMonth.objects.create()
		w.week_within_month = "9"
		self.assertRaises(InvalidWeekWithinMonthError, w.__unicode__)
		
class SeriesTestCase(TestCase):
	"""
	Test the functions that series.models.series uses to report its next event
	occurrence date.
	"""
	
	@mock.patch('series.models.date', FakeDate)
	def test_next_reading_day_nextmonth(self):
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 4))
		s = Series()
		s.day_of_week = DayOfWeek()
		s.day_of_week.day = "SU"
		s.week_within_month = WeekWithinMonth()
		s.week_within_month.week_within_month = "1" # Test first Sunday after Monday July 4, 2011
		self.assertEquals(s.next_reading_day(), date(2011, 8, 7))
		
	@mock.patch('series.models.date', FakeDate)
	def test_next_reading_day_thismonth(self):
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 4))
		s = Series()
		s.day_of_week = DayOfWeek()
		s.day_of_week.day = "MO"
		s.week_within_month = WeekWithinMonth()
		s.week_within_month.week_within_month = "1" # Test first Sunday after Monday July 4, 2011
		self.assertEquals(s.next_reading_day(), date(2011, 7, 4))
		
	@mock.patch('series.models.date', FakeDate)
	def test_reading_days_ahead_by_month_lessthanzero(self):
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 4))
		s = Series()
		s.day_of_week = DayOfWeek()
		s.day_of_week.day = "SU"
		s.week_within_month = WeekWithinMonth()
		s.week_within_month.week_within_month = "1" # Test first Sunday
		self.assertEquals(s.reading_days_ahead_by_month(-1), [date(2011, 8, 7)])
		
	def test_reading_days_ahead_by_month_zero(self):
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 4))
		s = Series()
		s.day_of_week = DayOfWeek()
		s.day_of_week.day = "SU"
		s.week_within_month = WeekWithinMonth()
		s.week_within_month.week_within_month = "1" # Test first Sunday
		self.assertEquals(s.reading_days_ahead_by_month(0), [date(2011, 8, 7)])

	def test_reading_days_ahead_by_month_one(self):
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 4))
		s = Series()
		s.day_of_week = DayOfWeek()
		s.day_of_week.day = "SU"
		s.week_within_month = WeekWithinMonth()
		s.week_within_month.week_within_month = "1" # Test first Sunday
		self.assertEquals(s.reading_days_ahead_by_month(1), [date(2011, 8, 7)])

	def test_reading_days_ahead_by_month_twelve(self):
		from datetime import date
		FakeDate.today = classmethod(lambda cls: date(2011, 7, 4))
		s = Series()
		s.day_of_week = DayOfWeek()
		s.day_of_week.day = "SU"
		s.week_within_month = WeekWithinMonth()
		s.week_within_month.week_within_month = "1" # Test first Sunday
		self.assertEquals(s.reading_days_ahead_by_month(12), [ 
																date(2011, 8, 7),
																date(2011, 9, 4),
																date(2011, 10, 2),
																date(2011, 11, 6),
																date(2011, 12, 4),
																date(2012, 1, 1),
																date(2012, 2, 5),
																date(2012, 3, 4),
																date(2012, 4, 1),
																date(2012, 5, 6),
																date(2012, 6, 3),
																date(2012, 7, 1),
																date(2012, 8, 5),
															])
