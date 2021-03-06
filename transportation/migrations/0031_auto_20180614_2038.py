# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-14 20:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0030_remove_ticket_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat', models.IntegerField(blank=True, null=True)),
                ('from_stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='transportation.Stop')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transportation.Service')),
            ],
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='connections',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='seat_number',
        ),
        migrations.AddField(
            model_name='connection',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transportation.Ticket'),
        ),
        migrations.AddField(
            model_name='connection',
            name='to_stop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='transportation.Stop'),
        ),
    ]
