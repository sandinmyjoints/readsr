from series.models import *
from django.contrib import admin

	
class SeriesAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['primary_name', 'secondary_name', 'genre', 'notes', 'affiliations', 'admission', 'admission_description']}),
		('Contact', {'fields': ['contact']}), 
		('Venue', {'fields': ['venue']}),
		('When', {'fields': ['regular', 'day_of_week', 'week_within_month', 'time', 'irregular_date_description']})
		]
	#filter_horizontal = ['contact', 'genre', 'affiliation', 'websites']
	search_fields = ['primary_name']


admin.site.register(Series, SeriesAdmin)
admin.site.register(Venue)
admin.site.register(Address)
admin.site.register(Affiliate)
admin.site.register(Genre)
#admin.site.register(DayOfWeek)
#admin.site.register(WeekWithinMonth)
