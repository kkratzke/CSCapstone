# Generated by Django 3.1.7 on 2022-09-29 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_auto_20220921_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaignName', models.CharField(max_length=150)),
                ('type', models.CharField(choices=[('Medical', 'Medical'), ('Memorial', 'Memorial'), ('Emergency', 'Emergency'), ('Education', 'Education'), ('Other', 'Other')], default='Other', max_length=15)),
                ('campaignCode', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('On going', 'On going'), ('Suspended', 'Suspended'), ('Canceled', 'Canceled'), ('End', 'End')], default='On going', max_length=15)),
                ('owner', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='myuser',
            name='role',
            field=models.CharField(choices=[('Admin', 'Admin'), ('User', 'User')], default='User', max_length=10),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
