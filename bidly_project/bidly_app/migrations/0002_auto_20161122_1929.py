# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-23 01:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bidly_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bidly_User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=11)),
            ],
        ),
        migrations.AlterField(
            model_name='bid',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bidly_app.Bidly_User'),
        ),
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='role',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bidly_app.Bidly_User'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='bidly_user',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]