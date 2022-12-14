# Generated by Django 3.2.6 on 2021-11-14 18:40

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SessionState',
            fields=[
                ('session_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('state', models.CharField(max_length=200, null=True)),
                ('data', jsonfield.fields.JSONField(null=True)),
                ('context', models.CharField(max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
    ]
