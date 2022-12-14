# Generated by Django 3.1.5 on 2021-02-03 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rdv', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evenement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=400, verbose_name="Nom de l'évènemnt")),
                ('date_d', models.DateField(verbose_name='Date de debut')),
                ('date_f', models.DateField(verbose_name='Date de fin')),
                ('type_e', models.CharField(default='holiday', max_length=100, verbose_name="Type d'evènement")),
                ('descriptions', models.CharField(default=' ', max_length=1000, verbose_name="Description de l'évènement")),
                ('color', models.CharField(default='#1ce', max_length=100, verbose_name="Couleur de l'évènement")),
                ('everyYear', models.BooleanField(default=False, verbose_name='Chaque année')),
                ('responsable', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rdv.responsable')),
            ],
            options={
                'verbose_name': 'Evènement',
            },
        ),
    ]
