# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Movie.starSeededTrueSkillSigma'
        db.delete_column(u'base_movie', 'starSeededTrueSkillSigma')

        # Deleting field 'Movie.rawTrueSkillSigma'
        db.delete_column(u'base_movie', 'rawTrueSkillSigma')

        # Deleting field 'Movie.rawTrueSkillMu'
        db.delete_column(u'base_movie', 'rawTrueSkillMu')

        # Deleting field 'Movie.starSeededTrueSkillMu'
        db.delete_column(u'base_movie', 'starSeededTrueSkillMu')

        # Adding field 'Movie.scoreMu'
        db.add_column(u'base_movie', 'scoreMu',
                      self.gf('django.db.models.fields.FloatField')(default=3.0),
                      keep_default=False)

        # Adding field 'Movie.scoreSigma'
        db.add_column(u'base_movie', 'scoreSigma',
                      self.gf('django.db.models.fields.FloatField')(default=1.0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Movie.starSeededTrueSkillSigma'
        db.add_column(u'base_movie', 'starSeededTrueSkillSigma',
                      self.gf('django.db.models.fields.FloatField')(default=1.0),
                      keep_default=False)

        # Adding field 'Movie.rawTrueSkillSigma'
        db.add_column(u'base_movie', 'rawTrueSkillSigma',
                      self.gf('django.db.models.fields.FloatField')(default=1.0),
                      keep_default=False)

        # Adding field 'Movie.rawTrueSkillMu'
        db.add_column(u'base_movie', 'rawTrueSkillMu',
                      self.gf('django.db.models.fields.FloatField')(default=3.0),
                      keep_default=False)

        # Adding field 'Movie.starSeededTrueSkillMu'
        db.add_column(u'base_movie', 'starSeededTrueSkillMu',
                      self.gf('django.db.models.fields.FloatField')(default=3.0),
                      keep_default=False)

        # Deleting field 'Movie.scoreMu'
        db.delete_column(u'base_movie', 'scoreMu')

        # Deleting field 'Movie.scoreSigma'
        db.delete_column(u'base_movie', 'scoreSigma')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'base.fight': {
            'Meta': {'object_name': 'Fight'},
            'contestants': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['base.Movie']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'movie1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'movie_1'", 'to': u"orm['base.Movie']"}),
            'movie2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'movie_2'", 'to': u"orm['base.Movie']"}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 4, 0, 0)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': "'NULL'", 'related_name': "'user'", 'to': u"orm['auth.User']"})
        },
        u'base.movie': {
            'Meta': {'ordering': "['name', '-starRating']", 'object_name': 'Movie'},
            'description': ('django.db.models.fields.TextField', [], {'default': "'N/A'"}),
            'director': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '500'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'poster_name': ('django.db.models.fields.CharField', [], {'default': "'_empty_poster.jpg'", 'max_length': '255'}),
            'scoreMu': ('django.db.models.fields.FloatField', [], {'default': '3.0'}),
            'scoreSigma': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'starRating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'year': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['base']