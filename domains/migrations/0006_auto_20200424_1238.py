# Generated by Django 3.0.5 on 2020-04-24 12:38

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0005_auto_20200424_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactaddress',
            name='country_code',
            field=django_countries.fields.CountryField(max_length=2, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='contactaddress',
            name='street_1',
            field=models.CharField(max_length=255, verbose_name='Address line 1'),
        ),
        migrations.AlterField(
            model_name='contactaddress',
            name='street_2',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Address line 2'),
        ),
        migrations.AlterField(
            model_name='contactaddress',
            name='street_3',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Address line 3'),
        ),
    ]
