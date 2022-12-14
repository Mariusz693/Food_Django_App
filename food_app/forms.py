from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import User, Ingredient, Recipe, IngredientRecipe, CommentRecipe
from .validators import validate_password


class DurationInput(forms.TimeInput):

    input_type = 'time'


class UserRegisterForm(forms.ModelForm):

    password_repeat = forms.CharField(label='Powtórz hasło', max_length=128, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar', 'password', 'password_repeat']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False
        
    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)
        
        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']

        if password != password_repeat:
            self.add_error('password_repeat', 'Hasła róźnią się od siebie')

        try:
            validate_password(password=password)
        except ValidationError as e:
            self.add_error('password', e)
        
    def save(self, commit=True, *args, **kwargs):

        return User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            avatar=self.cleaned_data['avatar'],
            password=self.cleaned_data['password'],
        )


class UserLoginForm(forms.Form):

    username = forms.CharField(label='Nazwa użytkownika', max_length=64)
    password = forms.CharField(label='Hasło', max_length=128, widget=forms.PasswordInput())

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.filter(username=username).first()
        
        if not user:
            self.add_error('username', 'Brak użytkownika o takiej nazwie')
        
        elif not authenticate(username=username, password=password):
            self.add_error('password', 'Błędne hasło')
    
    def authenticate_user(self, *args, **kwargs):

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        
        user = authenticate(username=username, password=password)

        return user


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False


class UserPasswordUpdateForm(forms.ModelForm):

    password = forms.CharField(label='Hasło', max_length=128, widget=forms.PasswordInput())
    password_new = forms.CharField(label='Nowe hasło', max_length=128, widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='Powtórz hasło', max_length=128, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['password', 'password_new', 'password_repeat']

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)
        
        password = self.cleaned_data['password']
        password_new = self.cleaned_data['password_new']
        password_repeat = self.cleaned_data['password_repeat']
        
        if not authenticate(username=self.instance.username, password=password):
            self.add_error('password_old', 'Błędne hasło')
    
        if password_new != password_repeat:
            self.add_error('password_repeat', 'Hasła róźnią się od siebie')

        try:
            validate_password(password=password_new)
        except ValidationError as e:
            self.add_error('password_new', e)


class UserPasswordResetForm(forms.Form):

    email = forms.CharField(label='Email', widget=forms.EmailInput())

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)

        email = self.cleaned_data['email']

        if not User.objects.filter(email=email).first():
            self.add_error('email', 'Brak użytkownika o podanym adresie email')


class UserPasswordSetForm(forms.Form):

    password_new = forms.CharField(label='Nowe hasło', widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput())

    def clean(self, *args, **kwargs):

        super().clean(*args, **kwargs)
        
        password_new = self.cleaned_data['password_new']
        password_repeat = self.cleaned_data['password_repeat']
        
        if password_new != password_repeat:
            self.add_error('password_repeat', 'Hasła róźnią się od siebie')

        try:
            validate_password(password=password_new)
        except ValidationError as e:
            self.add_error('password_new', e)


class SearchForm(forms.Form):

    name = forms.CharField(max_length=64, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Nazwa'


class IngredientForm(forms.ModelForm):

    class Meta:
        model = Ingredient
        fields = ['name', 'create_by']
        widgets = {
            'create_by': forms.HiddenInput(),
        }


class RecipeFormStep1(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ['ingredients',]
        widgets = {
            'ingredients': forms.CheckboxSelectMultiple(attrs={'class': "checkbox-style"}),
        }


class RecipeFormStep2(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ['name', 'description', 'preparation_time', 'calories', 'image', 'create_by']
        widgets = {
            'description': forms.Textarea(attrs={'rows':'5', 'maxlength': '512',}),
            'preparation_time': DurationInput(attrs={'step': '1'}),
            'create_by': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
    

class RecipeFormStep3(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ['preparing']
        widgets = {
            'preparing': forms.Textarea(attrs={'rows':'15',}),
        }


class IngredientRecipeForm(forms.ModelForm):

    class Meta:
        model = IngredientRecipe
        fields = ['ingredient', 'quantity']


IngredientRecipeFormset = forms.inlineformset_factory(
    parent_model=Recipe,
    model=IngredientRecipe,
    form=IngredientRecipeForm,
    extra=0,
    can_delete=True
)


class CommentRecipeForm(forms.ModelForm):

    class Meta:
        model = CommentRecipe
        fields = ['user', 'recipe', 'comment']
        labels = {
            'comment': 'Dodaj komentarz:',
        }
        widgets = {
            'user': forms.HiddenInput(),
            'recipe': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows':'4', 'maxlength': '512'}),
        }