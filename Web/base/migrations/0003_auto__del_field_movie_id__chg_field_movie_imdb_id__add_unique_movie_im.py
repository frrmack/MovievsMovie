# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Movie.id'
        db.delete_column(u'base_movie', u'id')


        # Changing field 'Movie.imdb_id'
        db.alter_column(u'base_movie', 'imdb_id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True))
        # Adding unique constraint on 'Movie', fields ['imdb_id']
        db.create_unique(u'base_movie', ['imdb_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Movie', fields ['imdb_id']
        db.delete_unique(u'base_movie', ['imdb_id'])

        # Adding field 'Movie.id'
        db.add_column(u'base_movie', u'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)


        # Changing field 'Movie.imdb_id'
        db.alter_column(u'base_movie', 'imdb_id', self.gf('django.db.models.fields.CharField')(max_length=255))

    models = {
        u'base.movie': {
            'Meta': {'ordering': "['name', '-starRating']", 'object_name': 'Movie'},
            'description': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '1000'}),
            'director': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '500'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'poster_name': ('django.db.models.fields.CharField', [], {'default': "'_empty_poster.jpg'", 'max_length': '255'}),
            'rawTrueSkillMu': ('django.db.models.fields.FloatField', [], {'default': '3.0'}),
            'rawTrueSkillSigma': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'starRating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'starSeededTrueSkillMu': ('django.db.models.fields.FloatField', [], {'default': '3.0'}),
            'starSeededTrueSkillSigma': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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