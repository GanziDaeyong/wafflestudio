# Generated by Django 3.1 on 2021-01-06 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('card', '0030_auto_20210106_0857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='created_at',
            field=models.DateTimeField(blank=True, default='2021-01-06 09:00:09'),
        ),
    ]
