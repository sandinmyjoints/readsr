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

from django.utils.translation import ugettext_lazy as _ # TODO change this to Python

from dateutil import rrule, parser, relativedelta

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
    		
	def rrule2text(self):
        # first verify that this is a valid monthly recurring date
        rule_pair = self._bynweekday[0]
        # The first item of rule_pair is the weekday
        weekday = WEEKDAY_LONG[rule_pair[0] % 7][1]
        print "weekday is %s" % weekday
        
        # The second item is the ordinal.
        ordinal = ORDINAL[rule_pair[1]]
        text = _("%s %s" % (rule_pair[1], rrule.weekdays[rule_pair[0]])
        return text


class rrule2textTests(unittest.TestCase):
	def setUp(self):
		pass
		
	def test_monthly(self):
	    rr = rrule(dr.MONTHLY, byweekday=relativedelta.FR(3), dtstart=datetime(2011, 8, 15), count=10)
	    self.assertEqual(rr.printrule(), "third Friday")


if __name__ == '__main__':
	unittest.main()