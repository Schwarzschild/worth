# Generated by Django 3.2.8 on 2022-02-25 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ppmresult',
            old_name='total',
            new_name='value',
        ),
    ]
