# Generated by Django 5.2.3 on 2025-07-16 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0024_alter_invoice_account_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='type',
            field=models.CharField(choices=[('class', 'Class'), ('event', 'Event'), ('workshop', 'Workshop')], default='class', max_length=20),
        ),
    ]
