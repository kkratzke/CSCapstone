# Generated by Django 4.1.1 on 2022-10-04 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaignName', models.CharField(max_length=150)),
                ('type', models.CharField(choices=[('Medical', 'Medical'), ('Memorial', 'Memorial'), ('Emergency', 'Emergency'), ('Education', 'Education'), ('Other', 'Other')], default='Other', max_length=15)),
                ('campaignCode', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('On going', 'On going'), ('Suspended', 'Suspended'), ('Canceled', 'Canceled'), ('End', 'End')], default='On going', max_length=15)),
                ('owner', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default=None, max_length=20)),
                ('last_name', models.CharField(default=None, max_length=20)),
                ('first_name', models.CharField(default=None, max_length=20)),
                ('email', models.CharField(default=None, max_length=30)),
                ('role', models.CharField(choices=[('Admin', 'Admin'), ('User', 'User')], default='User', max_length=10)),
                ('password', models.CharField(default=None, max_length=64)),
            ],
        ),
    ]