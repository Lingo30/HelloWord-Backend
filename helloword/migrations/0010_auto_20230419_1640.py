# Generated by Django 3.2.9 on 2023-04-19 16:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('helloword', '0009_auto_20230419_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstudylist',
            name='list_author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='create', to='helloword.userinfo'),
        ),
        migrations.AddField(
            model_name='wordlist',
            name='list_author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='helloword.userinfo'),
        ),
        migrations.AlterField(
            model_name='userstudylist',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study', to='helloword.userinfo'),
        ),
    ]
