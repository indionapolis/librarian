# Generated by Django 2.0.1 on 2018-01-23 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmsinno', '0032_auto_20180123_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='copy',
            name='status',
            field=models.IntegerField(choices=[(0, 0), (1, 1)], default=0),
        ),
    ]
