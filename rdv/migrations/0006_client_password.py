# Generated by Django 3.1.5 on 2021-02-24 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rdv', '0005_auto_20210219_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='password',
            field=models.CharField(default='password', max_length=300, verbose_name='Mot de passe'),
            preserve_default=False,
        ),
    ]
