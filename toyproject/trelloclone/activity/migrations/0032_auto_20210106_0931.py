# Generated by Django 3.1 on 2021-01-06 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0031_auto_20210106_0910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='created_at',
            field=models.DateTimeField(blank=True, default='2021-01-06 09:31:10'),
        ),
    ]
