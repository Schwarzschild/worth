# Generated by Django 3.2.8 on 2022-02-15 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('ib_exchange', models.CharField(choices=[('CASH', 'CASH'), ('STOCK', 'STOCK'), ('ARCA', 'ARCA'), ('SMART', 'SMART'), ('CME', 'CME'), ('NYM', 'NYM'), ('NYBOT', 'NYBOT'), ('NYB', 'NYB')], default='STOCK', max_length=6)),
                ('yahoo_exchange', models.CharField(choices=[('CASH', 'CASH'), ('STOCK', 'STOCK'), ('ARCA', 'ARCA'), ('SMART', 'SMART'), ('CME', 'CME'), ('NYM', 'NYM'), ('NYBOT', 'NYBOT'), ('NYB', 'NYB')], default='STOCK', max_length=6)),
                ('cs', models.FloatField(default=1.0)),
                ('commission', models.FloatField(default=0.0)),
                ('ib_price_factor', models.FloatField(default=1.0)),
                ('yahoo_price_factor', models.FloatField(default=1.0)),
                ('pprec', models.IntegerField(default=4)),
            ],
        ),
        migrations.CreateModel(
            name='Ticker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=20, unique=True)),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='markets.market')),
            ],
        ),
        migrations.CreateModel(
            name='DailyBar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('d', models.DateField()),
                ('o', models.FloatField()),
                ('h', models.FloatField()),
                ('l', models.FloatField()),
                ('c', models.FloatField()),
                ('v', models.FloatField()),
                ('oi', models.FloatField()),
                ('ticker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='markets.ticker')),
            ],
        ),
    ]
