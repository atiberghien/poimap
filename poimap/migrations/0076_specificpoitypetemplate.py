# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-08 15:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('poimap', '0075_poi_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecificPOITypeTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poimap.POIType')),
            ],
        ),
    ]