# Generated by Django 5.0.3 on 2024-04-23 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("domains", "0056_domainautomaticreneworder_resource_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="domainregistration",
            name="cf_zone_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]