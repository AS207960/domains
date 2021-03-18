# Generated by Django 2.2.17 on 2021-03-17 13:55

import as207960_utils.models
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0045_domainautomaticreneworder'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainPendingChangeKeyData',
            fields=[
                ('id', as207960_utils.models.TypedUUIDField(data_type='domains_domainpendingchangedsdata', primary_key=True, serialize=False)),
                ('operation', models.CharField(choices=[('A', 'Add'), ('R', 'Remove')], max_length=1)),
                ('flags', models.PositiveIntegerField()),
                ('protocol', models.PositiveIntegerField()),
                ('algorithm', models.PositiveIntegerField()),
                ('public_key', models.TextField()),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='key_data', to='domains.DomainRegistration')),
            ],
        ),
        migrations.CreateModel(
            name='DomainPendingChangeHostName',
            fields=[
                ('id', as207960_utils.models.TypedUUIDField(data_type='domains_domainpendingchangehostname', primary_key=True, serialize=False)),
                ('host_name', models.CharField(max_length=255)),
                ('addresses', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), size=None)),
                ('operation', models.CharField(choices=[('A', 'Add'), ('R', 'Remove')], max_length=1)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='host_names', to='domains.DomainRegistration')),
            ],
        ),
        migrations.CreateModel(
            name='DomainPendingChangeDSData',
            fields=[
                ('id', as207960_utils.models.TypedUUIDField(data_type='domains_domainpendingchangedsdata', primary_key=True, serialize=False)),
                ('operation', models.CharField(choices=[('A', 'Add'), ('R', 'Remove')], max_length=1)),
                ('key_tag', models.PositiveIntegerField()),
                ('algorithm', models.PositiveIntegerField()),
                ('digest_type', models.PositiveIntegerField()),
                ('digest', models.TextField()),
                ('flags', models.PositiveIntegerField(blank=True, null=True)),
                ('protocol', models.PositiveIntegerField(blank=True, null=True)),
                ('public_key', models.TextField(blank=True, null=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ds_data', to='domains.DomainRegistration')),
            ],
        ),
        migrations.CreateModel(
            name='DomainPendingChange',
            fields=[
                ('id', as207960_utils.models.TypedUUIDField(data_type='domains_domainpendingchange', primary_key=True, serialize=False)),
                ('registry_id', models.CharField(blank=True, max_length=255, null=True)),
                ('new_auth_info', models.CharField(blank=True, max_length=255, null=True)),
                ('add_host_objects', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), size=None)),
                ('rem_host_objects', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), size=None)),
                ('remove_dnssec', models.BooleanField(blank=True)),
                ('new_max_sig_life', models.DurationField(blank=True, null=True)),
                ('add_status', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None)),
                ('rem_status', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pending_changes', to='domains.DomainRegistration')),
                ('new_admin_contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='domains_pending_admin', to='domains.Contact')),
                ('new_billing_contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='domains_pending_billing', to='domains.Contact')),
                ('new_registrant_contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='domains_pending_registrant', to='domains.Contact')),
                ('new_tech_contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='domains_pending_tech', to='domains.Contact')),
            ],
        ),
    ]
