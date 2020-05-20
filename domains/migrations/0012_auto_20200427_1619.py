# Generated by Django 3.0.5 on 2020-04-27 16:19

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0011_auto_20200427_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(default='', max_length=128, region=None),
            preserve_default=False,
        ),
    ]
