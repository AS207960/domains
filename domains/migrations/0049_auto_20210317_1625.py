# Generated by Django 3.1.7 on 2021-03-17 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0048_auto_20210317_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='domainpendingchangedsdata',
            name='domain',
        ),
        migrations.RemoveField(
            model_name='domainpendingchangehostname',
            name='domain',
        ),
        migrations.AddField(
            model_name='domainpendingchangedsdata',
            name='domain_change',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='ds_data', to='domains.domainpendingchange'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='domainpendingchangehostname',
            name='domain_change',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='host_names', to='domains.domainpendingchange'),
            preserve_default=False,
        ),
    ]
