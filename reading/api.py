from django.contrib.auth.models import User

from tastypie.resources import ModelResource
from tastypie import fields

from reading.models import Reading
from series.api import SeriesResource


class ReadingResource(ModelResource):
    series = fields.ForeignKey(SeriesResource, 'series')
    class Meta:
        queryset = Reading.objects.all()
        resource_name = 'reading'
