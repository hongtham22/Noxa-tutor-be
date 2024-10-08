# Generated by Django 5.0.3 on 2024-09-30 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentprofile',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='parentprofile',
            name='birthdate',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='parentprofile',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='bio_link',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='birthdate',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='educational_background',
            field=models.CharField(blank=True, choices=[('high_school_diploma', 'High School Diploma'), ('bachelor_degree', 'Bachelor Degree'), ('bachelor_degree_engineering', 'Bachelor Degree in Engineering'), ('master_degree', 'Master Degree'), ('doctorate_degree', 'Doctorate Degree')], max_length=255),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
