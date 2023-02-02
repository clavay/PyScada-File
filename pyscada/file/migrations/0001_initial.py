# Generated by Django 3.2 on 2023-02-01 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pyscada', '0099_alter_dictionaryitem_label'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtendedFileDevice',
            fields=[
            ],
            options={
                'verbose_name': 'File Device',
                'verbose_name_plural': 'File Devices',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('pyscada.device',),
        ),
        migrations.CreateModel(
            name='ExtendedFileVariable',
            fields=[
            ],
            options={
                'verbose_name': 'File Variable',
                'verbose_name_plural': 'File Variables',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('pyscada.variable',),
        ),
        migrations.CreateModel(
            name='FileVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program', models.CharField(choices=[('awk', 'awk'), ('sed', 'sed')], default='awk', max_length=25)),
                ('command', models.CharField(blank=True, default='NR==1{ print; exit }', help_text='Look at https://www.gnu.org/software/gawk/manual/gawk.html<br> To write, use $value$ where the variable value should be placed.', max_length=500)),
                ('file_variable', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pyscada.variable')),
            ],
        ),
        migrations.CreateModel(
            name='FileDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.URLField(default='test.com')),
                ('port', models.PositiveSmallIntegerField(default=21)),
                ('protocol', models.PositiveSmallIntegerField(choices=[(0, 'local'), (1, 'ssh'), (2, 'ftp')])),
                ('username', models.CharField(blank=True, default='', max_length=50)),
                ('password', models.CharField(blank=True, default='', max_length=50)),
                ('ftp_passive_mode', models.BooleanField(default=True)),
                ('remote_file_path', models.CharField(blank=True, default='', help_text='For example : /dir/file.txt', max_length=100)),
                ('local_temporary_file_copy_path', models.CharField(blank=True, default='', help_text='For example : /tmp/file.txt', max_length=100)),
                ('timeout', models.PositiveSmallIntegerField(default=5, help_text='in seconds')),
                ('file_device', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pyscada.device')),
            ],
        ),
    ]
