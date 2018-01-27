# Generated by Django 2.0.1 on 2018-01-23 15:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmsinno', '0029_auto_20180123_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='year',
            field=models.PositiveIntegerField(default=None, validators=[django.core.validators.MinLengthValidator(4), django.core.validators.MaxLengthValidator(4)]),
        ),
    ]
