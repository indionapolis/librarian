# Generated by Django 2.0.1 on 2018-01-23 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lmsinno', '0009_auto_20180123_0918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lmsinno.User'),
        ),
    ]
