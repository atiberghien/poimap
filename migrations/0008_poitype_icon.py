# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-02 09:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itinerary', '0007_poiaddress_poi'),
    ]

    operations = [
        migrations.AddField(
            model_name='poitype',
            name='icon',
            field=models.CharField(choices=[(b'flag', b'Drapeau'), (b'cutlery', b'Restaurant'), (b'bed', b'Hotel'), (b'shopping-basket', b'Magasin')], default=b'flag', max_length=30),
        ),
    ]
