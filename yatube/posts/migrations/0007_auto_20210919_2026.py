# Generated by Django 2.2.6 on 2021-09-19 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created', '-pk')},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date', '-pk')},
        ),
    ]
