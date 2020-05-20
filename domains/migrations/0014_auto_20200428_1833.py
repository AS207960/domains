# Generated by Django 3.0.5 on 2020-04-28 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0013_auto_20200428_1819'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='birthday',
        ),
        migrations.AddField(
            model_name='contactaddress',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contactaddress',
            name='identity_number',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='National identity number'),
        ),
    ]
