# Generated by Django 3.1.5 on 2021-03-17 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rdv', '0012_auto_20210317_1822'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rendezvous',
            old_name='en_attente',
            new_name='etat',
        ),
    ]