# Generated by Django 2.0.1 on 2018-01-23 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lmsinno', '0020_auto_20180123_1446'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='data_created',
            new_name='date_created',
        ),
    ]
