# Generated by Django 3.2.6 on 2022-08-20 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('orders', '0005_alter_orderitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='organizations.organization'),
        ),
    ]
