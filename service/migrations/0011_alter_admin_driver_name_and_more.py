# Generated by Django 4.0.6 on 2022-12-13 10:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0010_delete_driver_details_update_admin_driver_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin_driver',
            name='name',
            field=models.CharField(max_length=12, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='admin_driver',
            name='new_password',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='admin_driver',
            name='temp_password',
            field=models.CharField(max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='driver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='service.admin_driver'),
        ),
        migrations.DeleteModel(
            name='Drivers',
        ),
    ]
