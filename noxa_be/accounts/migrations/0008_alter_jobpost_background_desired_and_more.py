# Generated by Django 5.1.1 on 2024-10-13 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_classtime_post_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobpost',
            name='background_desired',
            field=models.CharField(blank=True, choices=[('high_school_diploma', 'Có bằng tốt nghiệp trung học phổ thông'), ('university_student', 'Sinh viên'), ('university_graduate', 'Tốt nghiệp đại học'), ('university_graduate_education', 'Tốt nghiệp đại học sư phạm'), ('other', 'Khác')], max_length=255),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='educational_background',
            field=models.CharField(blank=True, choices=[('high_school_diploma', 'Có bằng tốt nghiệp trung học phổ thông'), ('university_student', 'Sinh viên'), ('university_graduate', 'Tốt nghiệp đại học'), ('university_graduate_education', 'Tốt nghiệp đại học sư phạm'), ('other', 'Khác')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('tutor', 'Gia sư'), ('parent', 'Phụ huynh'), ('admin', 'Quản trị viên')], max_length=50),
        ),
    ]
