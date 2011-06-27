# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CitySite'
        db.create_table('city_site_citysite', (
            ('site_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sites.Site'], unique=True, primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2)),
        ))
        db.send_create_signal('city_site', ['CitySite'])


    def backwards(self, orm):
        
        # Deleting model 'CitySite'
        db.delete_table('city_site_citysite')


    models = {
        'city_site.citysite': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'CitySite', '_ormbases': ['sites.Site']},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['city_site']
