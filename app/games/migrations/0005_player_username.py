# Generated by Django 4.1.1 on 2022-09-29 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_alter_player_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='username',
            field=models.CharField(default='miska', max_length=25),
            preserve_default=False,
        ),
    ]
