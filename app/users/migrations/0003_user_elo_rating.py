# Generated by Django 4.1.1 on 2022-10-14 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_first_name_remove_user_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='elo_rating',
            field=models.FloatField(default=400),
        ),
    ]
