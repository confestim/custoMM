# Generated by Django 4.0.3 on 2023-03-15 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server_client_api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='ign',
            new_name='discord',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='username',
            new_name='lol',
        ),
    ]