# Generated by Django 3.1.5 on 2021-05-13 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rdv', '0013_auto_20210317_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendezvous',
            name='heure_f',
            field=models.TimeField(null=True, verbose_name='Heure de fin Rdv'),
        ),
    ]
