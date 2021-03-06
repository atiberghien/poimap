# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-18 09:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('poimap', '0068_auto_20180701_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poilisting',
            name='area_display',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='poimap.Area', verbose_name=b'Zone \xc3\xa0 afficher'),
        ),
        migrations.AlterField(
            model_name='poilisting',
            name='path_display',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='poimap.Path', verbose_name=b'Chemin \xc3\xa0 afficher'),
        ),
        migrations.AlterField(
            model_name='poilisting',
            name='type_display',
            field=models.ManyToManyField(to='poimap.POIType', verbose_name=b'Type de POI \xc3\xa0 afficher'),
        ),
    ]
