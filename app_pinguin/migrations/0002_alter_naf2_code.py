# Generated by Django 4.2.21 on 2025-05-15 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pinguin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='naf2',
            name='CODE',
            field=models.CharField(max_length=4, unique=True),
        ),
    ]
