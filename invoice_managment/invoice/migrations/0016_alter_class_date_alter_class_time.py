# Generated by Django 5.2.3 on 2025-07-13 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0015_class_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='class',
            name='time',
            field=models.TimeField(),
        ),
    ]
