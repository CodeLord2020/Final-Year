# Generated by Django 4.2.3 on 2023-09-27 23:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ML', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentimentmodel',
            name='query_start_date',
            field=models.DateField(default=datetime.date(2022, 9, 27)),
        ),
    ]
