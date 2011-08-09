from series.models import *
from django.contrib import admin

	
class SeriesAdmin(admin.ModelAdmin):
    
    # TODO: Restore notes to the fieldset. Notes is a generic relation on 
    # swingtime.models.Event so I don't know why django complains when I add it here, 
    # because Series is descended from Event.
	fieldsets = [
		(None, {'fields': ['title', 'genre', 'affiliations', 'admission', 'admission_description']}),
		('Contact', {'fields': ['contact']}), 
		('Venue', {'fields': ['venue']}),
		('When', {'fields': ['regular', 'irregular_date_description']})
		]
	#filter_horizontal = ['contact', 'genre', 'affiliation', 'websites']
	search_fields = ['primary_name']


admin.site.register(Series, SeriesAdmin)
admin.site.register(Venue)
admin.site.register(Address)
admin.site.register(Affiliate)
admin.site.register(Genre)
admin.site.register(Contact)
#admin.site.register(DayOfWeek)
#admin.site.register(WeekWithinMonth)
