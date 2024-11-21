# Generated by Django 4.0 on 2024-11-21 02:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Kitty', '0005_alter_adoption_kitty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adoption',
            name='kitty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='adoptions', to='Kitty.kitty'),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]
