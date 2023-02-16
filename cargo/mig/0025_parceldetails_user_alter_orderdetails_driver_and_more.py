# Generated by Django 4.0.2 on 2022-12-03 07:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0024_alter_orderdetails_picked'),
    ]

    operations = [
        migrations.AddField(
            model_name='parceldetails',
            name='user',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='driver',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='service.drivers'),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='picked',
            field=models.BooleanField(),
        ),
    ]
