# Generated by Django 5.0.3 on 2024-10-17 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_parentprofile_avatar_tutorprofile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác')], max_length=50, null=True),
        ),
    ]
