from django.shortcuts import render, redirect
from django.views.generic import View, FormView, DetailView, UpdateView, DeleteView, CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import User, UserUniqueToken, Ingredient
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, UserPasswordUpdateForm, \
    UserPasswordResetForm, UserPasswordSetForm, SearchForm, IngredientForm
from .validators import validate_token

# Create your views here.


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

        return render (
            request=request,
            template_name='food_app/index.html',
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


class IngredientCreateView(LoginRequiredMixin, CreateView):

    """
    Return the create ingredient view
    """
    model = Ingredient
    form_class = IngredientForm
    template_name = 'food_app/ingredient_form.html'
    
    def get_success_url(self, *args, **kwargs):

        return reverse_lazy('user-panel')

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
