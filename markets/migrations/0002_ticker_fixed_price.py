# Generated by Django 3.2.8 on 2022-02-17 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticker',
            name='fixed_price',
            field=models.FloatField(blank=True, help_text='If set then this is the price that will always be used.', null=True),
        ),
    ]
