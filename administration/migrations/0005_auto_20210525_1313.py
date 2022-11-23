# Generated by Django 3.1.5 on 2021-05-25 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0004_auto_20210521_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='jourspecifique',
            name='date_debut',
            field=models.DateField(null=True, verbose_name='Date de debut'),
        ),
        migrations.AddField(
            model_name='jourspecifique',
            name='date_fin',
            field=models.DateField(null=True, verbose_name='Date de fin'),
        ),
        migrations.AddField(
            model_name='jourspecifique',
            name='jour_semaine',
            field=models.CharField(max_length=20, null=True, verbose_name='jour de la semaine'),
        ),
        migrations.AlterField(
            model_name='jourspecifique',
            name='date',
            field=models.DateField(null=True, verbose_name='Jour'),
        ),
    ]