# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# -- Note to the reader:                                            --
# -- This migration is intentionally incomplete; it doesn't match   --
# --   models.py. That is because the purpose of this test suite is --
# --   to test the creation of the migration itself, and so it only --
# --   makes sense if there is, in fact, something to migrate.      --
# --------------------------------------------------------------------

from __future__ import absolute_import, unicode_literals
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Author'
        db.create_table('south_migrations_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True)),
        ))
        db.send_create_signal('south_migrations', ['Author'])


    def backwards(self, orm):
        # Deleting model 'Author'
        db.delete_table('south_migrations_author')


    models = {
        'south_migrations.author': {
            'Meta': {'object_name': 'Author'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        }
    }

    complete_apps = ['south_migrations']
