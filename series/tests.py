"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from series.models import DayOfWeek, InvalidDayOfWeekError
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


class SeriesTestCase(TestCase):
	pass
