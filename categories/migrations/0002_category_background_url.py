# Generated by Django 4.0.2 on 2022-02-11 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='background_url',
            field=models.URLField(blank=True),
        ),
    ]
