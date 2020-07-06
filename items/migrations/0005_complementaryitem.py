# Generated by Django 3.0.7 on 2020-06-29 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0004_item_brand'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComplementaryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complementary_items', to='items.Item')),
            ],
        ),
    ]