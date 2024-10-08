# Generated by Django 5.0.3 on 2024-10-04 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_parentprofile_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobpost',
            old_name='wage_per_hour',
            new_name='wage_per_session',
        ),
        migrations.AddField(
            model_name='classtime',
            name='weekday',
            field=models.CharField(choices=[('monday', 'Thứ hai'), ('tuesday', 'Thứ ba'), ('wednesday', 'Thứ tư'), ('thursday', 'Thứ năm'), ('friday', 'Thứ sáu'), ('saturday', 'Thứ bảy'), ('sunday', 'Chủ nhật')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='classtime',
            name='time_end',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='classtime',
            name='time_start',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='jobpost',
            name='background_desired',
            field=models.CharField(choices=[('high_school_diploma', 'Có bằng tốt nghiệp trung học phổ thông'), ('bachelor_degree', 'Có bằng cử nhân'), ('bachelor_degree_engineering', 'Có bằng kĩ sư'), ('master_degree', 'Có bằng thạc sĩ'), ('doctorate_degree', 'Có bằng tiến sĩ')], max_length=255),
        ),
        migrations.AlterField(
            model_name='jobpost',
            name='status',
            field=models.CharField(choices=[('pending_approval', 'Đang chờ phê duyệt'), ('approved', 'Đã phê duyệt'), ('rejected', 'Bị từ chối'), ('closed', 'Đã đóng')], default='pending_approval', max_length=50),
        ),
        migrations.AlterField(
            model_name='jobpost',
            name='subject',
            field=models.CharField(choices=[('math', 'Toán'), ('literature', 'Văn học'), ('physics', 'Vật lý'), ('chemistry', 'Hóa học'), ('biology', 'Sinh học'), ('english', 'Tiếng Anh'), ('history', 'Lịch sử'), ('geography', 'Địa lý'), ('economy', 'Kinh tế'), ('computer_science', 'Khoa học máy tính'), ('other', 'Khác')], max_length=50),
        ),
        migrations.AlterField(
            model_name='parentprofile',
            name='gender',
            field=models.CharField(choices=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác')], max_length=50),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='educational_background',
            field=models.CharField(blank=True, choices=[('high_school_diploma', 'Có bằng tốt nghiệp trung học phổ thông'), ('bachelor_degree', 'Có bằng cử nhân'), ('bachelor_degree_engineering', 'Có bằng kĩ sư'), ('master_degree', 'Có bằng thạc sĩ'), ('doctorate_degree', 'Có bằng tiến sĩ')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='gender',
            field=models.CharField(choices=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác')], max_length=50),
        ),
        migrations.AlterField(
            model_name='tutorsubject',
            name='subject',
            field=models.CharField(choices=[('math', 'Toán'), ('literature', 'Văn học'), ('physics', 'Vật lý'), ('chemistry', 'Hóa học'), ('biology', 'Sinh học'), ('english', 'Tiếng Anh'), ('history', 'Lịch sử'), ('geography', 'Địa lý'), ('economy', 'Kinh tế'), ('computer_science', 'Khoa học máy tính'), ('other', 'Khác')], max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('tutor', 'Gia sư'), ('parent', 'Phụ huynh')], max_length=50),
        ),
    ]
