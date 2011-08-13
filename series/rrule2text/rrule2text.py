#!/usr/bin/env python
# encoding: utf-8
"""
rrule2text.py

Created by William Bert on 2011-08-12.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import unittest
from datetime import datetime

from django.utils.translation import ugettext_lazy as _ # TODO change this to Python

from dateutil.rrule import *
from dateutil.parser import *
from dateutil.relativedelta import *

from readsr.series.rrule2text.int2word import int2word

class Rrule2textError(ValueError):
    pass

class rrule2text(rrule):

    ORDINAL = (
        (1,  _(u'first')),
        (2,  _(u'second')),
        (3,  _(u'third')),
        (4,  _(u'fourth')),
        (-1, _(u'last'))
    ) 
    
    WEEKDAY_LONG = (
        (7, _(u'Sunday')),
        (1, _(u'Monday')),
        (2, _(u'Tuesday')),
        (3, _(u'Wednesday')),
        (4, _(u'Thursday')),
        (5, _(u'Friday')),
        (6, _(u'Saturday'))
    )
    
    INTERVAL = (
        (1, _(u'each')),
        (2, _(u'every other')),
        (3, _(u'every third')),
        (4, _(u'every fourth')),
        (5, _(u'every fifth')),
        (6, _(u'every sixth')),
        (7, _(u'every seventh')),
        (8, _(u'every eighth')),
        (9, _(u'every ninth')),
        (10, _(u'every tenth')),
        (11, _(u'every eleventh')),
        (12, _(u'every twelfth')),
    )

    def rrule2text(self):

        freq = self._freq
        interval = self._interval
        wkst = self._wkst
        until = self._until
        count = self._count
        bymonth = self._bymonth
        byweekno = self._byweekno
        byyearday = self._byyearday
        byweekday = self._byweekday
        bynweekday = self._bynweekday
        byeaster = self._byeaster
        bymonthday = self._bymonthday
        bynmonthday = self._bynmonthday
        bysetpos = self._bysetpos
        byhour = self._byhour
        byminute = self._byminute
        bysecond = self._bysecond
        
        text_description = []
        if freq != MONTHLY:
            raise Rrule2textError, "rrule2text only works with monthly frequencies right now."        
            
        # Get the interval. "Each", "Every other", "Every third", etc.
        p_interval = rrule2text.INTERVAL[interval][1]
        text_description.append(p_interval)

        # bynweekday is a tuple of (weekday, week_in_month) tuples
        print "bynweekday is %s" % (bynweekday,)
        for rule_pair in bynweekday:
            print "rule_pair is %s" % (rule_pair,)

            # Get the ordinal.
            p_ordinal = rrule2text.ORDINAL[rule_pair[1]]
            text_description.append(p_ordinal)

            #  Get the weekday name
            p_weekday = rrule2text.WEEKDAY_LONG[rule_pair[0] % 7][1]
            text_description.append(p_weekday)
            
            # tack on "and interval" for the next item in the list
            text_description.append(["and", p_interval])

        # remove the last "and interval" because it's hanging off the end
        # TODO improve this
        
        if count != 0:
            text_description.extend([int2word(count), "times"])
        elif until:
            text_description.extend(["until", until])
            
        text_description = text_description[:-2]
        return text_description


class rrule2textTests(unittest.TestCase):
	def setUp(self):
		pass
		
	def test_monthly(self):
	    rr = rrule2text(MONTHLY, byweekday=FR(3), dtstart=datetime(2011, 8, 15), count=10)
	    print "text is %s" % rr.rrule2text()
	    self.assertEqual(rr.rrule2text(), ["each", "third", "Friday", "ten", "times"])


if __name__ == '__main__':
	unittest.main()