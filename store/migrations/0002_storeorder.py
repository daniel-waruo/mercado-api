# Generated by Django 3.2.6 on 2021-09-08 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210816_1703'),
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='store_orders', to='orders.order')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='store.store')),
            ],
        ),
    ]
