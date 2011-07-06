"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from series.models import Series, WeekWithinMonth, DayOfWeek, InvalidDayOfWeekError, InvalidWeekWithinMonthError
from datetime import date
import mock

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

class FakeDate(date):
	"A fake replacement for date that can be mocked for testing."
	def __new__(cls, *args, **kwargs):
		return date.__new__(date, *args, **kwargs)

class TestDayOfWeek(TestCase):
	"""Test the day of the week functions."""

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
	def test_valid_week_within_month(self):
		w = WeekWithinMonth.objects.create()
		w.week_within_month = "1"
		self.assertEquals(w.__unicode__(), "The First")
		
	def test_invalid_week_within_month(self):
		w = WeekWithinMonth.objects.create()
		w.week_within_month = "9"
		self.assertRaises(InvalidWeekWithinMonthError, w.__unicode__)
		
class SeriesTestCase(TestCase):
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
