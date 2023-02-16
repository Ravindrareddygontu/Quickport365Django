# Generated by Django 4.0.6 on 2022-11-25 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0011_alter_orderdetails_destination_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='Destination_country',
            field=models.CharField(editable=False, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='image',
            field=models.ImageField(editable=False, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='status',
            field=models.CharField(choices=[('started', 'started'), ('in process', 'in process'), ('completed', 'completed')], max_length=20, null=True),
        ),
    ]
