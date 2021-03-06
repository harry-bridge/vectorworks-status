# Generated by Django 3.2.3 on 2021-06-11 10:45

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0007_alter_uptimehistory_test_ran_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='RlmInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=100)),
                ('count', models.IntegerField()),
                ('in_use', models.IntegerField()),
                ('last_updated', models.DateTimeField(default=datetime.datetime(2021, 6, 11, 10, 45, 14, 559543, tzinfo=utc))),
            ],
        ),
    ]
