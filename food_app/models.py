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


class Recipe(models.Model):
    
    class Meta:
        verbose_name = 'Przepis'
        verbose_name_plural = 'Przepisy'
        ordering = ['name']
    
    name = models.CharField(verbose_name='Nazwa przepisu', max_length=128)
    description = models.TextField(verbose_name='Opis przepisu', null=True, blank=True)
    preparing = models.TextField(verbose_name='Sposób przygotowania')
    create_date = models.DateTimeField(verbose_name='Data dodania', auto_now_add=True)
    preparation_time = models.DurationField(verbose_name='Czas przygotowania')
    calories = models.PositiveSmallIntegerField(verbose_name='Ilość kalorii / 100 gram', null=True, blank=True)
    create_by = models.ForeignKey(
        'User',
        related_name='recipes',
        verbose_name='Stworzył',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='recipes',
        verbose_name='Składniki',
        through='IngredientRecipe',
        )
    comments = models.ManyToManyField(
        'User',
        related_name='comments',
        verbose_name='Komentarze',
        through='CommentRecipe',
        )
    likes = models.ManyToManyField(
        'User',
        related_name='likes',
        verbose_name='Polubienia',
        )
    image = ResizedImageField(
        size=[342, 256],
        crop=['middle', 'center'],
        force_format='PNG',
        upload_to=image_upload_handler,
        default='food_app/default_recipe.png',
        verbose_name='Zdjęcie'
        )
    
    def __str__(self):
        return self.name
    

class IngredientRecipe(models.Model):

    class Meta:
        verbose_name = 'Składnik przepisu'
        verbose_name_plural = 'Składnik przepisu'
        unique_together = ['ingredient', 'recipe']
        ordering = ['ingredient', 'recipe']

    quantity = models.CharField(verbose_name='Ilość', max_length=64)
    ingredient = models.ForeignKey(
        'Ingredient',
        related_name='ingredient_recipes',
        verbose_name='Składnik',
        on_delete=models.RESTRICT
        )
    recipe = models.ForeignKey(
        'Recipe',
        related_name='recipe_ingredients',
        verbose_name='Przepis',
        on_delete=models.CASCADE
        )
    
    def unique_error_message(self, model_class, unique_check):

        if unique_check == ('ingredient', 'recipe'):
            return 'Składnik już dodany do przepisu'

        return super().unique_error_message(model_class, unique_check)


class CommentRecipe(models.Model):

    class Meta:
        verbose_name = 'Komentarz przepisu'
        verbose_name_plural = 'Komentarz przepisu'
        ordering = ['-date_added']

    comment = models.TextField(verbose_name='Komentarz')
    date_added = models.DateTimeField(verbose_name='Data wpisu', auto_now_add=True)
    recipe = models.ForeignKey(
        'Recipe',
        related_name='recipe_comments',
        verbose_name='Przepis',
        on_delete=models.CASCADE
        )
    user = models.ForeignKey(
        'User',
        related_name='user_comments',
        verbose_name='Użytkownik',
        on_delete=models.CASCADE
        )


class Schedule(models.Model):
    
    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plany'
        ordering = ['name']
    
    name = models.CharField(verbose_name='Nazwa planu', max_length=128)
    description = models.TextField(verbose_name='Opis planu', null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='Data dodania', auto_now_add=True)
    create_by = models.ForeignKey(
        'User',
        related_name='schedules',
        verbose_name='Stworzył',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )
    recipes = models.ManyToManyField(
        'Recipe',
        related_name='schedules',
        verbose_name='Przepisy',
        through='RecipeSchedule',
        )
    likes = models.ManyToManyField(
        'User',
        related_name='likes_schedule',
        verbose_name='Polubienia',
        )
    
    def __str__(self):
        return self.name
 

class RecipeSchedule(models.Model):
    
    class Meta:
        verbose_name = 'Przepis w planie'
        verbose_name_plural = 'Przepisy w planie'
        unique_together = ['schedule', 'day_number', 'meal_number']
        ordering = ['schedule', 'day_number', 'meal_number']

    DAY_CHOICES = (
        (1, 'Poniedziałek'),
        (2, 'Wtorek'),
        (3, 'Środa'),
        (4, 'Czwartek'),
        (5, 'Piątek'),
        (6, 'Sobota'),
        (7, 'Niedziela')
    )
    MEAL_CHOICES = (
        (1, 'Śniadanie'),
        (2, 'Drugie śniadanie'),
        (3, 'Obiad'),
        (4, 'Podwieczorek'),
        (5, 'Kolacja')
    )
    
    day_number = models.PositiveSmallIntegerField(verbose_name='Dzień tygodnia', choices=DAY_CHOICES)
    meal_number = models.PositiveSmallIntegerField(verbose_name='Posiłek', choices=MEAL_CHOICES)
    schedule = models.ForeignKey(
        'Schedule',
        related_name='schedule_recipes',
        verbose_name='Plan',
        on_delete=models.CASCADE
        )
    recipe = models.ForeignKey(
        'Recipe',
        related_name='recipe_schedules',
        verbose_name='Przepis',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )

    def unique_error_message(self, model_class, unique_check):

        if unique_check == ('schedule', 'day_number', 'meal_number'):
            return 'Posiłek już ujęty w tym dniu w planie'

        return super().unique_error_message(model_class, unique_check)
