# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-01 02:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0017_auto_20161026_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='servergroup',
            name='apps',
            field=models.ManyToManyField(to='cmdb.App'),
        ),
    ]