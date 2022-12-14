# Generated by Django 4.0.3 on 2022-11-21 19:13

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_resized.forms
import food_app.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=64, verbose_name='Imię')),
                ('last_name', models.CharField(max_length=64, verbose_name='Nazwisko')),
                ('password', models.CharField(max_length=128, verbose_name='Hasło')),
                ('is_active', models.BooleanField(default=False, verbose_name='Aktywny')),
                ('username', models.CharField(error_messages={'unique': 'Nazwa użytkownika już zarejestrowana w serwisie'}, max_length=64, unique=True, verbose_name='Nazwa użytkownika')),
                ('email', models.EmailField(error_messages={'unique': 'Email już zarejestrowany w serwisie'}, max_length=128, unique=True, verbose_name='Email')),
                ('avatar', django_resized.forms.ResizedImageField(crop=['middle', 'center'], default='food_app/default_person.png', force_format='PNG', keep_meta=True, quality=-1, scale=None, size=[192, 256], upload_to=food_app.models.image_upload_handler, verbose_name='Awatar')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Użytkownik',
                'verbose_name_plural': 'Użytkownicy',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserUniqueToken',
            fields=[
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
