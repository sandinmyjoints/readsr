from django.contrib.auth.models import User

from tastypie.resources import ModelResource
from tastypie import fields

from series.models import Series, Contact


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        
class ContactResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = Contact.objects.all()
        resource_name = 'contact'

class SeriesResource(ModelResource):
    contact = fields.ForeignKey(ContactResource, 'contact')
    
    class Meta:
        queryset = Series.objects.all()
        resource_name = 'series'
