# Generated by Django 3.2.6 on 2022-08-20 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('products', '0007_product_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='brands', to='organizations.organization'),
        ),
        migrations.AddField(
            model_name='category',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='organizations.organization'),
        ),
        migrations.AddField(
            model_name='product',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='organizations.organization'),
        ),
    ]
