# Generated by Django 4.0.1 on 2022-02-10 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashrecord',
            name='cleared_f',
            field=models.BooleanField(default=False),
        ),
    ]
