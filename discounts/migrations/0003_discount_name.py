# Generated by Django 5.1.2 on 2024-11-17 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discounts', '0002_remove_discount_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
