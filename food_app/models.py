import uuid

from pathlib import Path

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail

from django_resized import ResizedImageField

# Create your models here.


def image_upload_handler(instance, filename):
    
    model_name = instance.__class__.__name__
    new_filename = uuid.uuid4().hex
    file_suffix = Path(filename).suffix
    
    return f'food_app/{model_name}/{new_filename}{file_suffix}'


class User(AbstractUser):

    class Meta:
            verbose_name = 'Użytkownik'
            verbose_name_plural = 'Użytkownicy'

    first_name = models.CharField(verbose_name='Imię', max_length=64)
    last_name = models.CharField(verbose_name='Nazwisko', max_length=64)
    password = models.CharField(verbose_name='Hasło', max_length=128)
    is_active = models.BooleanField(verbose_name='Aktywny', default=False)
    username = models.CharField(
        verbose_name='Nazwa użytkownika',
        max_length=64,
        unique=True,
        error_messages={'unique': 'Nazwa użytkownika już zarejestrowana w serwisie'},
        )
    email = models.EmailField(
        verbose_name='Email',
        max_length=128,
        unique=True,
        error_messages={'unique': 'Email już zarejestrowany w serwisie'},
        )
    avatar = ResizedImageField(
        size=[192, 256],
        crop=['middle', 'center'],
        force_format='PNG',
        upload_to=image_upload_handler,
        default='food_app/default_person.png',
        verbose_name='Awatar'
        )
    
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):

        return self.username
    
    def get_full_name(self):
        
        return f'{self.first_name} {self.last_name}'

    def email_user(self, subject, message, from_email='webmaster@localhost', *args, **kwargs):
        
        send_mail(subject, message, from_email, [self.email,], *args, **kwargs)


class UserUniqueToken(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Ingredient(models.Model):

    class Meta:
        verbose_name = 'Składnik'
        verbose_name_plural = 'Składniki'
        ordering = ['name']

    name = models.CharField(
        verbose_name='Nazwa składnika',
        max_length=128,
        unique=True,
        error_messages={'unique': 'Składnik już zapisany w bazie'},
        )
    create_by = models.ForeignKey(
        'User',
        related_name='ingredients',
        verbose_name='Stworzył',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )

    def __str__(self):
        return self.name
