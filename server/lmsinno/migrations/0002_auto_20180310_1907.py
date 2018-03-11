# Generated by Django 2.0.1 on 2018-03-10 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lmsinno', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='document',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='lmsinno.Document'),
        ),
        migrations.AlterField(
            model_name='order',
            name='copy',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='lmsinno.Copy'),
        ),
    ]
