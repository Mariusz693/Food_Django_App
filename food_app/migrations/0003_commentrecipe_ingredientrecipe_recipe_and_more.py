# Generated by Django 4.0.3 on 2022-12-11 20:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms
import food_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('food_app', '0002_ingredient'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='Komentarz')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='Data wpisu')),
            ],
            options={
                'verbose_name': 'Komentarz przepisu',
                'verbose_name_plural': 'Komentarz przepisu',
                'ordering': ['-date_added'],
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.CharField(max_length=64, verbose_name='Ilość')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='ingredient_recipes', to='food_app.ingredient', verbose_name='Składnik')),
            ],
            options={
                'verbose_name': 'Składnik przepisu',
                'verbose_name_plural': 'Składnik przepisu',
                'ordering': ['ingredient', 'recipe'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Nazwa przepisu')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Opis przepisu')),
                ('preparing', models.TextField(verbose_name='Sposób przygotowania')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Data dodania')),
                ('preparation_time', models.DurationField(verbose_name='Czas przygotowania')),
                ('calories', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Ilość kalorii')),
                ('image', django_resized.forms.ResizedImageField(crop=['middle', 'center'], default='food_app/default_recipe.png', force_format='PNG', keep_meta=True, quality=-1, scale=None, size=[342, 256], upload_to=food_app.models.image_upload_handler, verbose_name='Zdjęcie')),
                ('comments', models.ManyToManyField(related_name='comments', through='food_app.CommentRecipe', to=settings.AUTH_USER_MODEL, verbose_name='Komentarze')),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Stworzył')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='food_app.IngredientRecipe', to='food_app.ingredient', verbose_name='Składniki')),
                ('likes', models.ManyToManyField(related_name='likes', to=settings.AUTH_USER_MODEL, verbose_name='Głosy')),
            ],
            options={
                'verbose_name': 'Przepis',
                'verbose_name_plural': 'Przepisy',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='food_app.recipe', verbose_name='Przepis'),
        ),
        migrations.AddField(
            model_name='commentrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_comments', to='food_app.recipe', verbose_name='Przepis'),
        ),
        migrations.AddField(
            model_name='commentrecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to=settings.AUTH_USER_MODEL, verbose_name='Użytkownik'),
        ),
        migrations.AlterUniqueTogether(
            name='ingredientrecipe',
            unique_together={('ingredient', 'recipe')},
        ),
    ]
