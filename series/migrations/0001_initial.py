# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Contact'
        db.create_table('series_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('series', ['Contact'])

        # Adding model 'Genre'
        db.create_table('series_genre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('genre', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('series', ['Genre'])

        # Adding model 'Address'
        db.create_table('series_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street_address', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('series', ['Address'])

        # Adding model 'Venue'
        db.create_table('series_venue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('secondary_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['series.Address'], unique=True)),
            ('phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('in_dc', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('series', ['Venue'])

        # Adding model 'Affiliate'
        db.create_table('series_affiliate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('series', ['Affiliate'])

        # Adding model 'DayOfWeek'
        db.create_table('series_dayofweek', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('series', ['DayOfWeek'])

        # Adding model 'WeekWithinMonth'
        db.create_table('series_weekwithinmonth', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('week_within_month', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('series', ['WeekWithinMonth'])

        # Adding model 'Series'
        db.create_table('series_series', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('primary_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('secondary_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['series.Venue'])),
            ('regular', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('irregular_date_description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('day_of_week', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['series.DayOfWeek'], null=True, blank=True)),
            ('week_within_month', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['series.WeekWithinMonth'], null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')(default=datetime.time(18, 0))),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('admission', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('admission_description', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('wiki_mode', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['city_site.CitySite'])),
        ))
        db.send_create_signal('series', ['Series'])

        # Adding M2M table for field genre on 'Series'
        db.create_table('series_series_genre', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('series', models.ForeignKey(orm['series.series'], null=False)),
            ('genre', models.ForeignKey(orm['series.genre'], null=False))
        ))
        db.create_unique('series_series_genre', ['series_id', 'genre_id'])

        # Adding M2M table for field affiliations on 'Series'
        db.create_table('series_series_affiliations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('series', models.ForeignKey(orm['series.series'], null=False)),
            ('affiliate', models.ForeignKey(orm['series.affiliate'], null=False))
        ))
        db.create_unique('series_series_affiliations', ['series_id', 'affiliate_id'])

        # Adding model 'SeriesTweet'
        db.create_table('series_seriestweet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['series.Series'], null=True)),
            ('tweet', self.gf('django.db.models.fields.CharField')(max_length=140)),
            ('bitly_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('twitter_status_id', self.gf('django.db.models.fields.CharField')(max_length=17)),
        ))
        db.send_create_signal('series', ['SeriesTweet'])


    def backwards(self, orm):
        
        # Deleting model 'Contact'
        db.delete_table('series_contact')

        # Deleting model 'Genre'
        db.delete_table('series_genre')

        # Deleting model 'Address'
        db.delete_table('series_address')

        # Deleting model 'Venue'
        db.delete_table('series_venue')

        # Deleting model 'Affiliate'
        db.delete_table('series_affiliate')

        # Deleting model 'DayOfWeek'
        db.delete_table('series_dayofweek')

        # Deleting model 'WeekWithinMonth'
        db.delete_table('series_weekwithinmonth')

        # Deleting model 'Series'
        db.delete_table('series_series')

        # Removing M2M table for field genre on 'Series'
        db.delete_table('series_series_genre')

        # Removing M2M table for field affiliations on 'Series'
        db.delete_table('series_series_affiliations')

        # Deleting model 'SeriesTweet'
        db.delete_table('series_seriestweet')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'city_site.citysite': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'CitySite', '_ormbases': ['sites.Site']},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'series.address': {
            'Meta': {'object_name': 'Address'},
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'series.affiliate': {
            'Meta': {'object_name': 'Affiliate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'series.contact': {
            'Meta': {'object_name': 'Contact'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'series.dayofweek': {
            'Meta': {'object_name': 'DayOfWeek'},
            'day': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'series.genre': {
            'Meta': {'object_name': 'Genre'},
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'series.series': {
            'Meta': {'ordering': "('primary_name',)", 'object_name': 'Series'},
            'admission': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'admission_description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'affiliations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['series.Affiliate']", 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'day_of_week': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['series.DayOfWeek']", 'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['series.Genre']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irregular_date_description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'primary_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'regular': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'secondary_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['city_site.CitySite']"}),
            'time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(18, 0)'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['series.Venue']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'week_within_month': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['series.WeekWithinMonth']", 'null': 'True', 'blank': 'True'}),
            'wiki_mode': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'series.seriestweet': {
            'Meta': {'object_name': 'SeriesTweet'},
            'bitly_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['series.Series']", 'null': 'True'}),
            'tweet': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'twitter_status_id': ('django.db.models.fields.CharField', [], {'max_length': '17'})
        },
        'series.venue': {
            'Meta': {'object_name': 'Venue'},
            'address': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['series.Address']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_dc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'secondary_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'series.weekwithinmonth': {
            'Meta': {'object_name': 'WeekWithinMonth'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'week_within_month': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['series']
