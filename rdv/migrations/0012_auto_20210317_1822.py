# Generated by Django 3.1.5 on 2021-03-17 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rdv', '0011_auto_20210312_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rendezvous',
            name='en_attente',
            field=models.CharField(default='En attente', max_length=30, null=True, verbose_name='Etat du Rdv'),
        ),
    ]