# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Deployment'
        db.create_table('stacktach_deployment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('stacktach', ['Deployment'])

        # Adding model 'RawData'
        db.create_table('stacktach_rawdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deployment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stacktach.Deployment'])),
            ('tenant', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('routing_key', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('old_state', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=20, null=True, blank=True)),
            ('old_task', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=30, null=True, blank=True)),
            ('when', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=6, db_index=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('event', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('service', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('host', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('instance', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('request_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('stacktach', ['RawData'])

        # Adding model 'Lifecycle'
        db.create_table('stacktach_lifecycle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('instance', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('last_state', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('last_task_state', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('last_raw', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stacktach.RawData'], null=True)),
        ))
        db.send_create_signal('stacktach', ['Lifecycle'])

        # Adding model 'Timing'
        db.create_table('stacktach_timing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('lifecycle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stacktach.Lifecycle'])),
            ('start_raw', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['stacktach.RawData'])),
            ('end_raw', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['stacktach.RawData'])),
            ('start_when', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=6)),
            ('end_when', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=6)),
            ('diff', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=6, db_index=True)),
        ))
        db.send_create_signal('stacktach', ['Timing'])

        # Adding model 'RequestTracker'
        db.create_table('stacktach_requesttracker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('request_id', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('lifecycle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stacktach.Lifecycle'])),
            ('last_timing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stacktach.Timing'], null=True)),
            ('start', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=6, db_index=True)),
            ('duration', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=6, db_index=True)),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('stacktach', ['RequestTracker'])


    def backwards(self, orm):
        # Deleting model 'Deployment'
        db.delete_table('stacktach_deployment')

        # Deleting model 'RawData'
        db.delete_table('stacktach_rawdata')

        # Deleting model 'Lifecycle'
        db.delete_table('stacktach_lifecycle')

        # Deleting model 'Timing'
        db.delete_table('stacktach_timing')

        # Deleting model 'RequestTracker'
        db.delete_table('stacktach_requesttracker')


    models = {
        'stacktach.deployment': {
            'Meta': {'object_name': 'Deployment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'stacktach.lifecycle': {
            'Meta': {'object_name': 'Lifecycle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'last_raw': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stacktach.RawData']", 'null': 'True'}),
            'last_state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'last_task_state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'stacktach.rawdata': {
            'Meta': {'object_name': 'RawData'},
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stacktach.Deployment']"}),
            'event': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'old_state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'old_task': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'request_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'routing_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'tenant': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'when': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '6', 'db_index': 'True'})
        },
        'stacktach.requesttracker': {
            'Meta': {'object_name': 'RequestTracker'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'duration': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '6', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_timing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stacktach.Timing']", 'null': 'True'}),
            'lifecycle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stacktach.Lifecycle']"}),
            'request_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '6', 'db_index': 'True'})
        },
        'stacktach.timing': {
            'Meta': {'object_name': 'Timing'},
            'diff': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '6', 'db_index': 'True'}),
            'end_raw': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['stacktach.RawData']"}),
            'end_when': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lifecycle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stacktach.Lifecycle']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'start_raw': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['stacktach.RawData']"}),
            'start_when': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '6'})
        }
    }

    complete_apps = ['stacktach']