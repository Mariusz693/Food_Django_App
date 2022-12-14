import os
from copy import deepcopy

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, FormView, DetailView, UpdateView, DeleteView, CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from formtools.wizard.views import SessionWizardView
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Count

from .models import User, UserUniqueToken, Ingredient, Recipe, CommentRecipe
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, UserPasswordUpdateForm, \
    UserPasswordResetForm, UserPasswordSetForm, SearchForm, IngredientForm, RecipeFormStep1, \
        RecipeFormStep2, RecipeFormStep3, IngredientRecipeFormset, CommentRecipeForm
from .validators import validate_token

# Create your views here.


FORMS_RECIPE = [
    ('step1', RecipeFormStep1),
    ('step2', RecipeFormStep2),
    ('step3', RecipeFormStep3),
    ('step4', IngredientRecipeFormset)
]

TEMPLATES_RECIPE = {
    'step1': 'food_app/recipe_form_step1.html',
    'step2': 'food_app/recipe_form_step2.html',
    'step3': 'food_app/recipe_form_step3.html',
    'step4': 'food_app/recipe_formset.html',
}


class TestMixin(UserPassesTestMixin):
    
    def handle_no_permission(self):

        if self.request.user.is_authenticated:
            
            return redirect(reverse_lazy('user-panel'))
        
        return redirect(reverse_lazy('user-login')+f'?next={self.request.get_full_path()}')


class IndexView(View):

    """
    Return base view
    """
    def get(self, request, *args, **kwargs):

        recipe_list = Recipe.objects.annotate(num_likes=Count('likes')).order_by('-num_likes')[:3]
        context = {}
        if recipe_list.count() == 3:
            context['recipe_list'] = recipe_list
        
        return render (
            request=request,
            template_name='food_app/index.html',
            context=context
        )


class UserRegisterView(FormView):

    """
    Return user register form
    """
    form_class = UserRegisterForm
    template_name = 'food_app/user_register.html'
    success_url = reverse_lazy('user-login')
   
    def form_valid(self, form, *args, **kwargs):

        user = form.save()
        new_token = UserUniqueToken.objects.create(user=user)
        user.email_user(
            subject='Rejestracja konta',
            message=f'''Witaj {user}, twój link do aktywacji konta:
                {self.request.get_host()}{reverse_lazy('user-active')}?token={new_token.token}'''
        )
        messages.success(self.request, message='Dziękujemy za rejestrację w serwisie. Sprawdź pocztę i kliknij w link aktywacyjny aby się zalogować')
        
        return super().form_valid(form, *args, **kwargs)


class UserActiveView(View):

    """
    Check user token and activ account
    """
    def get(self, request, *args, **kwargs):

        token = request.GET.get('token')

        if token and validate_token(token) and UserUniqueToken.objects.filter(token=token).first():    
            user_token = UserUniqueToken.objects.get(token=token)
            user = user_token.user
            user.is_active = True
            user.save()
            user_token.delete()
        
        else:
            messages.error(self.request, message='Twój link jest błędny lub źle podany !!!')

        return redirect(reverse_lazy('user-login'))


class UserLoginView(FormView):

    """
    Return user login view
    """
    form_class = UserLoginForm
    template_name = 'food_app/user_login.html'

    def get_success_url(self, *args, **kwargs):

        return self.request.GET.get('next') or reverse_lazy('user-panel')

    def form_valid(self, form, *args, **kwargs):

        user = form.authenticate_user()

        if user:
            login(self.request, user=user)

        return super().form_valid(form, *args, **kwargs)


class UserLogoutView(View):

    """
    Return user logout view
    """
    def get(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:

            logout(request)
        
        return redirect(reverse_lazy('index'))


class UserUpdateView(LoginRequiredMixin, UpdateView):
    
    """
    Return user update view
    """
    model = User
    form_class = UserUpdateForm
    template_name = 'food_app/user_update.html'
    success_url = reverse_lazy('user-panel')
    
    def get_object(self, *args, **kwargs):
       
        return self.request.user


class UserPanelView(LoginRequiredMixin, DetailView):

    """
    Return user panel view
    """
    model = User
    template_name = 'food_app/user_panel.html'
    context_object_name = 'user'
    
    def get_object(self, *args, **kwargs):
       
        return self.request.user


class UserPasswordUpdateView(LoginRequiredMixin, UpdateView):
    
    """
    Return user password update view
    """
    model = User
    form_class = UserPasswordUpdateForm
    template_name = 'food_app/user_password_update.html'
    success_url = reverse_lazy('user-panel')
    
    def get_object(self, *args, **kwargs):
       
        return self.request.user

    def form_valid(self, form, *args, **kwargs):
        
        self.object.set_password(form.cleaned_data['password_new'])
        logout(self.request)
        
        return super().form_valid(form, *args, **kwargs)


class UserPasswordResetView(FormView):

    """
    Return user password reset view
    """
    form_class = UserPasswordResetForm
    template_name = 'food_app/user_password_reset.html'
    success_url = reverse_lazy('user-login')
    
    def form_valid(self, form, *args, **kwargs):

        user = User.objects.get(email=form.cleaned_data['email'])
        new_token, created = UserUniqueToken.objects.get_or_create(user=user)
        
        if user.is_active:
            user.email_user(
                subject='Resetowanie hasła',
                message=f'''Witaj {user}, twój link do ustawienia nowego hasła:
                    {self.request.get_host()}{reverse_lazy('user-password-set')}?token={new_token.token}'''
                )
            messages.success(self.request, message='Dziękujemy, sprawdź pocztę i kliknij w link resetujący hasło')
        
        else:
            user.email_user(
                subject='Aktywacja konta',
                message=f'''Witaj {user}, twój link do aktywacji konta:
                    {self.request.get_host()}{reverse_lazy('user-active')}?token={new_token.token}'''
                )
            messages.success(self.request, message='Konto nie zostało jeszcze aktywowany, sprawdź pocztę i kliknij w link aktywacyjny')
        
        return super().form_valid(form, *args, **kwargs)


class UserPasswordSetView(View):
    
    """
    Return user password set view
    """    
    def get(self, request, *args, **kwargs):
       
        token = request.GET.get('token')
        form = None

        if token and validate_token(token) and UserUniqueToken.objects.filter(token=token).first():
            form = UserPasswordSetForm
            messages.success(self.request, message='Ustaw nowe hasło')
        
        else:
            messages.error(self.request, message='Twój link jest błędny lub źle podany !!!')

        return render(
            request=request,
            template_name='food_app/user_password_set.html',
            context={
                'form': form,
            }
        )            
     
    def post(self, request, *args, **kwargs):
        
        form = UserPasswordSetForm(request.POST)

        if form.is_valid():
            token = request.GET.get('token')
            user_unique_token = UserUniqueToken.objects.filter(token=token).first()
            password_new = form.cleaned_data['password_new']
            user = user_unique_token.user
            user.set_password(password_new)
            user.save()
            user_unique_token.delete()

            return redirect('user-login')


class UserDeleteView(LoginRequiredMixin, DeleteView):

    """
    Return the delete user view
    """
    model = User
    template_name = 'food_app/user_delete.html'
    success_url = reverse_lazy('index')

    def get_object(self, *args, **kwargs):
       
        return self.request.user


class UserIngredientView(LoginRequiredMixin, ListView):

    """
    Return the list all ingredients create by user
    """
    model = Ingredient
    template_name = 'food_app/user_ingredient.html'
    context_object_name = 'ingredient_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):

        ingredient_list = self.request.user.ingredients.all()
        self.form = SearchForm(self.request.GET)
        self.search_count = ''

        if self.form.is_valid():

            if self.form.changed_data:
                ingredient_list = ingredient_list.filter(name__icontains=self.form.cleaned_data['name'])
                self.search_count = ingredient_list.count()
             
        return ingredient_list
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['form'] = self.form
        context['search_count'] = self.search_count
        
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context


class UserRecipeView(LoginRequiredMixin, ListView):

    """
    Return the list all recipes create by user
    """
    model = Recipe
    template_name = 'food_app/user_recipe.html'
    context_object_name = 'recipe_list'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):

        recipe_list = self.request.user.recipes.all()
        self.form = SearchForm(self.request.GET)
        self.search_count = ''

        if self.form.is_valid():

            if self.form.changed_data:
                recipe_list = recipe_list.filter(name__icontains=self.form.cleaned_data['name'])
                self.search_count = recipe_list.count()
             
        return recipe_list
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['form'] = self.form
        context['search_count'] = self.search_count
        
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context


class UserLikeView(LoginRequiredMixin, ListView):

    """
    Return the list all recipes like by user
    """
    model = Recipe
    template_name = 'food_app/user_like.html'
    context_object_name = 'recipe_list'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):

        recipe_list = self.request.user.likes.all()
        self.form = SearchForm(self.request.GET)
        self.search_count = ''

        if self.form.is_valid():

            if self.form.changed_data:
                recipe_list = recipe_list.filter(name__icontains=self.form.cleaned_data['name'])
                self.search_count = recipe_list.count()
             
        return recipe_list

    def post(self, *args, **kwargs):
        
        if self.request.POST.get('like'):
            recipe = Recipe.objects.get(pk=self.request.POST.get('like'))
            recipe.likes.remove(self.request.user)

        return redirect(reverse_lazy('user-like') + '#user-like')

    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['form'] = self.form
        context['search_count'] = self.search_count
        
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context


class UserCommentView(LoginRequiredMixin, ListView):

    """
    Return the list all recipes comment by user
    """
    model = CommentRecipe
    template_name = 'food_app/user_comment.html'
    context_object_name = 'comment_list'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):

        comment_list = self.request.user.user_comments.all()
        self.form = SearchForm(self.request.GET)
        self.search_count = ''

        if self.form.is_valid():

            if self.form.changed_data:
                comment_list = comment_list.filter(recipe__in=Recipe.objects.filter(name__icontains=self.form.cleaned_data['name']))
                self.search_count = comment_list.count()
             
        return comment_list

    def post(self, *args, **kwargs):
        
        if self.request.POST.get('comment'):
            comment_recipe = CommentRecipe.objects.get(pk=self.request.POST.get('comment'))
            comment_recipe.delete()

        return redirect(reverse_lazy('user-comment') + '#user-comment')

    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['form'] = self.form
        context['search_count'] = self.search_count
        
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context


class UserRecipesView(ListView):

    """
    Return the list all recipes create by user for non register user
    """
    model = Recipe
    template_name = 'food_app/user_recipes.html'
    context_object_name = 'recipe_list'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):

        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        recipe_list = self.user.recipes.all()
        self.form = SearchForm(self.request.GET)
        self.search_count = ''

        if self.form.is_valid():

            if self.form.changed_data:
                recipe_list = recipe_list.filter(name__icontains=self.form.cleaned_data['name'])
                self.search_count = recipe_list.count()
             
        return recipe_list
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['user'] = self.user
        context['form'] = self.form
        context['search_count'] = self.search_count
        
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context


class UserCommentsView(ListView):

    """
    Return the list all comments create by user for non register user
    """
    model = Recipe
    template_name = 'food_app/user_comments.html'
    context_object_name = 'comment_list'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):

        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        comment_list = self.user.user_comments.all()
        self.form = SearchForm(self.request.GET)
        self.search_count = ''

        if self.form.is_valid():

            if self.form.changed_data:
                comment_list = comment_list.filter(recipe__in=Recipe.objects.filter(name__icontains=self.form.cleaned_data['name']))
                self.search_count = comment_list.count()
             
        return comment_list
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['user'] = self.user
        context['form'] = self.form
        context['search_count'] = self.search_count
        
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context


class IngredientCreateView(LoginRequiredMixin, CreateView):

    """
    Return the create ingredient view
    """
    model = Ingredient
    form_class = IngredientForm
    template_name = 'food_app/ingredient_form.html'
    
    def get_success_url(self, *args, **kwargs):

        return self.request.GET.get('next') or reverse_lazy('user-ingredient') + '#user-ingredient'

    def get_initial(self, *args, **kwargs):

        initial = super().get_initial(*args, **kwargs)
        initial['create_by'] = self.request.user 
        
        return initial


class IngredientUpdateView(TestMixin, UpdateView):

    """
    Return the update ingredient view
    """
    def test_func(self):

        return self.get_object().create_by == self.request.user

    model = Ingredient
    form_class = IngredientForm
    template_name = 'food_app/ingredient_form.html'
    context_object_name = 'ingredient'
    
    def get_success_url(self, *args, **kwargs):

        return self.request.GET.get('next') + '#user-ingredient'


class IngredientDeleteView(TestMixin, DeleteView):

    """
    Return the delete ingredient view
    """
    def test_func(self):

        return self.get_object().create_by == self.request.user

    model = Ingredient
    template_name = 'food_app/ingredient_delete.html'
    context_object_name = 'ingredient'

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('user-ingredient') + '#user-ingredient'

    def form_valid(self, form, *args, **kwargs):
        
        if self.get_object().recipes.all():
            messages.error(self.request, message='Twój składnik jest zawarty w pzepisie, nie można usunąć !!!')

            return super().form_invalid(form, *args, **kwargs)
        
        return super().form_valid(form, *args, **kwargs)


class RecipeCreateView(LoginRequiredMixin, SessionWizardView):

    """
    Return the create recipe in four step view
    """
    instance = None
    form_list = FORMS_RECIPE
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, ''))

    def get_form_instance(self, step, *args, **kwargs):
        
        if self.instance is None:
            self.instance = Recipe()
        
        return self.instance

    def get_template_names(self, *args, **kwargs):
        
        return [TEMPLATES_RECIPE[self.steps.current]]
 
    def get_form(self, step=None, data=None, files=None):
        
        form = super().get_form(step, data, files)

        if step is None:
            step = self.steps.current
        
        if step == 'step2':
            form.initial = {'create_by': self.request.user}

        if step == 'step4':
            ingredient_checked = self.get_cleaned_data_for_step('step1')['ingredients']
            form.min_num = ingredient_checked.count()
            form.initial = [{'ingredient': ingredient.pk} for ingredient in ingredient_checked]
        
        return form
  
    def done(self, form_list, *args, **kwargs):
        
        self.instance.save()
        formset = form_list[3]
        formset.instance = self.instance
        formset.save()
        
        return redirect(reverse_lazy('user-panel') + '#user-recipe')


class RecipeUpdateView(TestMixin, SessionWizardView):

    """
    Return the update recipe in four step view
    """
    instance = None
    form_list = FORMS_RECIPE
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, ''))

    def test_func(self):

        self.recipe = Recipe.objects.get(pk=self.kwargs['pk'])

        return self.recipe.create_by == self.request.user

    def get_form_instance(self, step, *args, **kwargs):

        self.recipe = Recipe.objects.get(pk=self.kwargs['pk'])

        if self.instance is None:
            self.instance = self.recipe
        
        return self.instance

    def get_template_names(self, *args, **kwargs):
        
        return [TEMPLATES_RECIPE[self.steps.current]]

    def get_context_data(self, form, *args, **kwargs):
        
        context = super().get_context_data(form, *args, **kwargs)
        context['recipe'] = self.recipe
        context['next'] = self.request.GET.get('next') + '#user-recipe'
    
        return context

    def get_form(self, step=None, data=None, files=None):
        
        form = super().get_form(step, data, files)

        if step is None:
            step = self.steps.current
        
        if step == 'step4':
            
            if data == None:
                ingredient_checked = self.get_cleaned_data_for_step('step1')['ingredients']
                ingredient_id = [ingredient.id for ingredient in ingredient_checked]
                ingredient_initial = self.recipe.ingredients.all()
                
                if len(form.forms) > ingredient_initial.count():
                    form.forms = form.forms[:ingredient_initial.count()]
                
                for ingredient_recipe_form in form.forms:
                    if not ingredient_recipe_form.initial['ingredient'] in ingredient_id:
                        ingredient_recipe_form.initial['DELETE'] = True
            
                for ingredient in ingredient_checked:
                    
                    if not ingredient in ingredient_initial:
                        new_form = deepcopy(form.forms[0])
                        new_form.initial = {
                            'quantity': '',
                            'ingredient': ingredient.pk,
                            'recipe': self.recipe.pk,
                            'id': ''
                        }
                        new_form.prefix = f'step4-{len(form.forms)}'
                        form.forms.append(new_form)
                
                form.min_num = len(form.forms)
                
        return form
  
    def done(self, form_list, *args, **kwargs):
        
        self.instance.save()
        formset = form_list[3]
        formset.save()
        
        return redirect(self.request.GET.get('next') + '#user-recipe')


class RecipeDeleteView(TestMixin, DeleteView):

    """
    Return the delete recipe view
    """
    def test_func(self):

        return self.get_object().create_by == self.request.user

    model = Recipe
    template_name = 'food_app/recipe_delete.html'
    context_object_name = 'recipe'

    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('user-recipe') + '#user-recipe'


class RecipeDetailView(DetailView):

    """
    Return the detail recipe view
    """
    model = Recipe
    template_name = 'food_app/recipe_detail.html'
    context_object_name = 'recipe'

    def post(self, *args, **kwargs):
        
        if self.request.POST.get('button_recipe'):
            button_recipe = self.request.POST.get('button_recipe')
            
            if button_recipe == 'like_up':
                self.get_object().likes.add(self.request.user)

            elif button_recipe == 'like_down':
                self.get_object().likes.remove(self.request.user)

            elif button_recipe == 'comment':
                form = CommentRecipeForm(self.request.POST)
                
                if form.is_valid():
                    form.save()

        return redirect(reverse_lazy('recipe-detail', args=[self.get_object().pk,]))
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        comments = self.get_object().recipe_comments.all()
        paginator = Paginator(comments, 5)
        page = self.request.GET.get('page')
        comment_list = paginator.get_page(page)
        
        context['comment_list'] = comment_list
        context['likes_count'] = self.get_object().likes.count()
        
        if self.request.user.is_authenticated:
            form = CommentRecipeForm()
            form.initial['user'] = self.request.user
            form.initial['recipe'] = self.get_object()
            context['form'] = form
            context['user_like'] = self.get_object().likes.filter(pk=self.request.user.pk).exists()
        
        return context


class RecipeListView(ListView):

    """
    Return the list all recipe view
    """
    model = Recipe
    template_name = 'food_app/recipe_list.html'
    context_object_name = 'recipe_list'
    paginate_by = 15

    def get_queryset(self, *args, **kwargs):

        recipe_list = Recipe.objects.all()
        self.form = SearchForm(self.request.GET)
        self.search_count = ''

        if self.form.is_valid():

            if self.form.changed_data:
                recipe_list = recipe_list.filter(name__icontains=self.form.cleaned_data['name'])
                self.search_count = recipe_list.count()
             
        return recipe_list
        
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['form'] = self.form
        context['search_count'] = self.search_count
        
        if self.search_count:
            context['path_pagination'] = self.request.get_full_path().split('&page=')[0] + '&page='
        
        else:
            context['path_pagination'] = self.request.get_full_path().split('?')[0] + '?page='
        
        return context
