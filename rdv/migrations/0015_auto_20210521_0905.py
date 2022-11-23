# Generated by Django 3.1.5 on 2021-05-21 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rdv', '0014_rendezvous_heure_f'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneauhoraire',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rdv.service'),
        ),
        migrations.AlterField(
            model_name='rendezvous',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rdv.client'),
        ),
        migrations.AlterField(
            model_name='rendezvous',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rdv.service'),
        ),
        migrations.AlterField(
            model_name='responsableservice',
            name='responsable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rdv.responsable'),
        ),
        migrations.AlterField(
            model_name='responsableservice',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rdv.service'),
        ),
    ]