from django.contrib import admin

from .models import User, Ingredient, UserUniqueToken

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    
    list_display = ('username', 'email', 'first_name', 'last_name')


admin.site.register(Ingredient)

admin.site.register(UserUniqueToken)