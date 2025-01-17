# Generated by Django 4.2.13 on 2024-08-31 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="customuser", name="oauth_kakao_access_token", field=models.CharField(blank=True, max_length=512, null=True)
        ),
        migrations.AlterField(model_name="customuser", name="oauth_kakao_id_token", field=models.CharField(blank=True, max_length=1024, null=True)),
        migrations.AlterField(
            model_name="customuser", name="oauth_kakao_refresh_token", field=models.CharField(blank=True, max_length=512, null=True)
        ),
    ]
