# Generated by Django 3.0.7 on 2020-06-06 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0018_auto_20200526_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactaddress',
            name='resource_id',
            field=models.UUIDField(null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='int_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='int_contacts', to='domains.ContactAddress', verbose_name='Internationalised address'),
        ),
        migrations.AlterField(
            model_name='contactaddress',
            name='postal_code',
            field=models.CharField(max_length=255, null=True),
        ),
    ]