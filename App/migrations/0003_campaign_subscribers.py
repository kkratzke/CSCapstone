# Generated by Django 4.1.1 on 2022-11-17 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_alter_userpictures_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='subscribers',
            field=models.ManyToManyField(related_name='subscribers', to='App.myuser'),
        ),
    ]
