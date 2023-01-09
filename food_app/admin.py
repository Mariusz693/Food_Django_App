from django.contrib import admin

from .models import User, Ingredient, UserUniqueToken, Recipe, IngredientRecipe, CommentRecipe, Schedule, RecipeSchedule

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    
    list_display = ('username', 'email', 'first_name', 'last_name')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    
    list_display = ('name', 'create_date', 'create_by')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    
    list_display = ('name', 'create_date', 'create_by')


admin.site.register(Ingredient)

admin.site.register(UserUniqueToken)

admin.site.register(IngredientRecipe)

admin.site.register(CommentRecipe)

admin.site.register(RecipeSchedule)