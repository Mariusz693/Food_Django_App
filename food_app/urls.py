from django.urls import path

from .views import IndexView, UserRegisterView, UserActiveView, UserLoginView, UserLogoutView, UserPanelView, \
    UserUpdateView, UserPasswordUpdateView, UserPasswordResetView, UserPasswordSetView, UserDeleteView, \
        UserRecipeView, UserScheduleView, UserIngredientView, UserCommentView, UserLikeView, UserLikeScheduleView, \
            UserRecipesView, UserSchedulesView, UserCommentsView, IngredientCreateView, IngredientUpdateView, \
                IngredientDeleteView, RecipeCreateView, RecipeUpdateView, RecipeDeleteView, RecipeDetailView, \
                    RecipeListView, ScheduleCreateView, ScheduleUpdateView, ScheduleDeleteView, ScheduleDetailView, \
                        ScheduleListView

urlpatterns = [
    path('', view=IndexView.as_view(), name='index'),
    path('user/register/', view=UserRegisterView.as_view(), name='user-register'),
    path('user/active/', view=UserActiveView.as_view(), name='user-active'),
    path('user/login/', view=UserLoginView.as_view(), name='user-login'),
    path('user/logout/', view=UserLogoutView.as_view(), name='user-logout'),
    path('user/panel/', view=UserPanelView.as_view(), name='user-panel'),
    path('user/update/', view=UserUpdateView.as_view(), name='user-update'),
    path('user/password/update/', view=UserPasswordUpdateView.as_view(), name='user-password-update'),
    path('user/password/reset/', view=UserPasswordResetView.as_view(), name='user-password-reset'),
    path('user/password/set/', view=UserPasswordSetView.as_view(), name='user-password-set'),
    path('user/delete/', view=UserDeleteView.as_view(), name='user-delete'),
    path('user/recipe/', view=UserRecipeView.as_view(), name='user-recipe'),
    path('user/schedule/', view=UserScheduleView.as_view(), name='user-schedule'),
    path('user/ingredient/', view=UserIngredientView.as_view(), name='user-ingredient'),
    path('user/comment/', view=UserCommentView.as_view(), name='user-comment'),
    path('user/like/', view=UserLikeView.as_view(), name='user-like'),
    path('user/like_schedule/', view=UserLikeScheduleView.as_view(), name='user-like-schedule'),
    path('user/recipes/<int:pk>/', view=UserRecipesView.as_view(), name='user-recipes'),
    path('user/schedules/<int:pk>/', view=UserSchedulesView.as_view(), name='user-schedules'),
    path('user/comments/<int:pk>/', view=UserCommentsView.as_view(), name='user-comments'),
    path('ingredient/create/', view=IngredientCreateView.as_view(), name='ingredient-create'),
    path('ingredient/update/<int:pk>/', view=IngredientUpdateView.as_view(), name='ingredient-update'),
    path('ingredient/delete/<int:pk>/', view=IngredientDeleteView.as_view(), name='ingredient-delete'),
    path('recipe/create/', view=RecipeCreateView.as_view(), name='recipe-create'),
    path('recipe/update/<int:pk>/', view=RecipeUpdateView.as_view(), name='recipe-update'),
    path('recipe/delete/<int:pk>/', view=RecipeDeleteView.as_view(), name='recipe-delete'),
    path('recipe/detail/<int:pk>/', view=RecipeDetailView.as_view(), name='recipe-detail'),
    path('recipe/list/', view=RecipeListView.as_view(), name='recipe-list'),
    path('schedule/create/', view=ScheduleCreateView.as_view(), name='schedule-create'),
    path('schedule/update/<int:pk>/', view=ScheduleUpdateView.as_view(), name='schedule-update'),
    path('schedule/delete/<int:pk>/', view=ScheduleDeleteView.as_view(), name='schedule-delete'),
    path('schedule/detail/<int:pk>/', view=ScheduleDetailView.as_view(), name='schedule-detail'),
    path('schedule/list/', view=ScheduleListView.as_view(), name='schedule-list'),
]