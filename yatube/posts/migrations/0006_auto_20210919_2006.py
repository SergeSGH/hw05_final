# Generated by Django 2.2.9 on 2021-09-19 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20210919_2002'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты пользователей'},
        ),
    ]
