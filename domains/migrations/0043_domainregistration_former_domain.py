# Generated by Django 2.2.17 on 2021-02-18 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0042_contact_privacy_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='domainregistration',
            name='former_domain',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]