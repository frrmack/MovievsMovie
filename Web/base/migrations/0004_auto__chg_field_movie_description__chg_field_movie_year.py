# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Movie.description'
        db.alter_column(u'base_movie', 'description', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Movie.year'
        db.alter_column(u'base_movie', 'year', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):

        # Changing field 'Movie.description'
        db.alter_column(u'base_movie', 'description', self.gf('django.db.models.fields.CharField')(max_length=1000))

        # Changing field 'Movie.year'
        db.alter_column(u'base_movie', 'year', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'base.movie': {
            'Meta': {'ordering': "['name', '-starRating']", 'object_name': 'Movie'},
            'description': ('django.db.models.fields.TextField', [], {'default': "'N/A'"}),
            'director': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '500'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'poster_name': ('django.db.models.fields.CharField', [], {'default': "'_empty_poster.jpg'", 'max_length': '255'}),
            'rawTrueSkillMu': ('django.db.models.fields.FloatField', [], {'default': '3.0'}),
            'rawTrueSkillSigma': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'starRating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'starSeededTrueSkillMu': ('django.db.models.fields.FloatField', [], {'default': '3.0'}),
            'starSeededTrueSkillSigma': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'year': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '100'})
        },
        u'base.versusmatch': {
            'Meta': {'object_name': 'VersusMatch'},
            'contestants': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['base.Movie']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'movie1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'movie_1'", 'to': u"orm['base.Movie']"}),
            'movie2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'movie_2'", 'to': u"orm['base.Movie']"}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 11, 0, 0)'})
        }
    }

    complete_apps = ['base']