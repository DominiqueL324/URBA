# Generated by Django 3.1.5 on 2021-02-03 13:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200, verbose_name='Nom')),
                ('prenom', models.CharField(max_length=200, verbose_name='Prenom')),
                ('email', models.EmailField(max_length=300, verbose_name='Email')),
                ('adresse', models.CharField(max_length=300, verbose_name='Adresse')),
                ('telephone', models.IntegerField(verbose_name='Téléphone')),
            ],
            options={
                'verbose_name': 'client',
            },
        ),
        migrations.CreateModel(
            name='Fichier',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fichier', models.FileField(max_length=500, upload_to='fichier/')),
            ],
        ),
        migrations.CreateModel(
            name='Responsable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adresse', models.CharField(max_length=300, verbose_name='Adresse')),
                ('telephone', models.IntegerField(verbose_name='Téléphone')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'responsable',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'service',
            },
        ),
        migrations.CreateModel(
            name='ResponsableService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('responsable', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rdv.responsable')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rdv.service')),
            ],
            options={
                'verbose_name': 'Responsable de service',
            },
        ),
        migrations.CreateModel(
            name='RendezVous',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('by_phone', models.BooleanField(default=False, verbose_name='Rendez-vous Téléphonique')),
                ('urbanisme', models.BooleanField(default=False, verbose_name="Avez vous déjà pris contact avec le service d'urbanisme")),
                ('date_r', models.DateField(verbose_name='Date Rdv')),
                ('heure_r', models.TimeField(verbose_name='Heure Rdv')),
                ('nombre_personne', models.IntegerField(verbose_name='Nombre de Personne')),
                ('en_attente', models.BooleanField(default=False, verbose_name='Mettre en attente')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rdv.client')),
                ('fichiers', models.ManyToManyField(related_name='rdv_fichier', to='rdv.Fichier')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rdv.service')),
            ],
            options={
                'verbose_name': 'rendez-vous',
                'verbose_name_plural': 'rendez-vous',
            },
        ),
    ]
