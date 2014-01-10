# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Movie'
        db.create_table(u'base_movie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('imdb_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('year', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('starRating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rawTrueSkillMu', self.gf('django.db.models.fields.FloatField')(default=3.0)),
            ('rawTrueSkillSigma', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('starSeededTrueSkillMu', self.gf('django.db.models.fields.FloatField')(default=3.0)),
            ('starSeededTrueSkillSigma', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('poster_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'base', ['Movie'])

        # Adding model 'VersusMatch'
        db.create_table(u'base_versusmatch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('movie1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='movie_1', to=orm['base.Movie'])),
            ('movie2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='movie_2', to=orm['base.Movie'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 1, 9, 0, 0))),
            ('result', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal(u'base', ['VersusMatch'])

        # Adding M2M table for field contestants on 'VersusMatch'
        m2m_table_name = db.shorten_name(u'base_versusmatch_contestants')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('versusmatch', models.ForeignKey(orm[u'base.versusmatch'], null=False)),
            ('movie', models.ForeignKey(orm[u'base.movie'], null=False))
        ))
        db.create_unique(m2m_table_name, ['versusmatch_id', 'movie_id'])


    def backwards(self, orm):
        # Deleting model 'Movie'
        db.delete_table(u'base_movie')

        # Deleting model 'VersusMatch'
        db.delete_table(u'base_versusmatch')

        # Removing M2M table for field contestants on 'VersusMatch'
        db.delete_table(db.shorten_name(u'base_versusmatch_contestants'))


    models = {
        u'base.movie': {
            'Meta': {'ordering': "['name', '-starRating']", 'object_name': 'Movie'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'poster_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 9, 0, 0)'})
        }
    }

    complete_apps = ['base']