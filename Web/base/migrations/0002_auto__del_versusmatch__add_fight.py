# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'VersusMatch'
        db.delete_table(u'base_versusmatch')

        # Removing M2M table for field contestants on 'VersusMatch'
        db.delete_table(db.shorten_name(u'base_versusmatch_contestants'))

        # Adding model 'Fight'
        db.create_table(u'base_fight', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('movie1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='movie_1', to=orm['base.Movie'])),
            ('movie2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='movie_2', to=orm['base.Movie'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 1, 11, 0, 0))),
            ('result', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal(u'base', ['Fight'])

        # Adding M2M table for field contestants on 'Fight'
        m2m_table_name = db.shorten_name(u'base_fight_contestants')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('fight', models.ForeignKey(orm[u'base.fight'], null=False)),
            ('movie', models.ForeignKey(orm[u'base.movie'], null=False))
        ))
        db.create_unique(m2m_table_name, ['fight_id', 'movie_id'])


    def backwards(self, orm):
        # Adding model 'VersusMatch'
        db.create_table(u'base_versusmatch', (
            ('movie1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='movie_1', to=orm['base.Movie'])),
            ('movie2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='movie_2', to=orm['base.Movie'])),
            ('result', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 1, 11, 0, 0))),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
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

        # Deleting model 'Fight'
        db.delete_table(u'base_fight')

        # Removing M2M table for field contestants on 'Fight'
        db.delete_table(db.shorten_name(u'base_fight_contestants'))


    models = {
        u'base.fight': {
            'Meta': {'object_name': 'Fight'},
            'contestants': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['base.Movie']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'movie1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'movie_1'", 'to': u"orm['base.Movie']"}),
            'movie2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'movie_2'", 'to': u"orm['base.Movie']"}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 11, 0, 0)'})
        },
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
        }
    }

    complete_apps = ['base']