# Generated by Django 4.0.3 on 2023-03-15 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_client_api', '0002_rename_ign_player_discord_rename_username_player_lol'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='mmr',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
    ]
