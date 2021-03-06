# Generated by Django 3.2.3 on 2021-06-09 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0004_auto_20210607_0726'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapersettings',
            name='vectorworks_hostname',
            field=models.CharField(default='change', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uptimetest',
            name='name',
            field=models.CharField(default='change', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uptimetest',
            name='test_type',
            field=models.IntegerField(choices=[(0, 'Internal'), (1, 'External')], default=0),
            preserve_default=False,
        ),
    ]
