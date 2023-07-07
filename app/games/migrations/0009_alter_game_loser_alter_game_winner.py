# Generated by Django 4.1.1 on 2022-10-13 19:02

from django.db import migrations, models
import games.models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0008_alter_challange_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='loser',
            field=models.ForeignKey(null=True, on_delete=models.SET(games.models.get_sentinel_user), related_name='loser', to='games.player'),
        ),
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.ForeignKey(null=True, on_delete=models.SET(games.models.get_sentinel_user), related_name='winner', to='games.player'),
        ),
    ]