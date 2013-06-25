# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Movie'
        db.create_table('uuid__movie', (
            ('id', self.gf('django_pg.models.fields.uuid.UUIDField')(auto_add=True, primary_key=True, unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('uuid_', ['Movie'])

        # Adding model 'Game'
        db.create_table('uuid__game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('uuid', self.gf('django_pg.models.fields.uuid.UUIDField')(unique=True)),
        ))
        db.send_create_signal('uuid_', ['Game'])

        # Adding model 'Book'
        db.create_table('uuid__book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('uuid', self.gf('django_pg.models.fields.uuid.UUIDField')(null=True, unique=True)),
        ))
        db.send_create_signal('uuid_', ['Book'])


    def backwards(self, orm):
        # Deleting model 'Movie'
        db.delete_table('uuid__movie')

        # Deleting model 'Game'
        db.delete_table('uuid__game')

        # Deleting model 'Book'
        db.delete_table('uuid__book')


    models = {
        'uuid_.book': {
            'Meta': {'object_name': 'Book'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'uuid': ('django_pg.models.fields.uuid.UUIDField', [], {'null': 'True', 'unique': 'True'})
        },
        'uuid_.game': {
            'Meta': {'object_name': 'Game'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'uuid': ('django_pg.models.fields.uuid.UUIDField', [], {'unique': 'True'})
        },
        'uuid_.movie': {
            'Meta': {'object_name': 'Movie'},
            'id': ('django_pg.models.fields.uuid.UUIDField', [], {'auto_add': 'True', 'primary_key': 'True', 'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['uuid_']
