# Generated by Django 4.0.3 on 2022-07-24 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryinvitation',
            name='is_accepted',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
