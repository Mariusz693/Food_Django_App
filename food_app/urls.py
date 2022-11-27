from django.urls import path

from .views import IndexView, UserRegisterView, UserActiveView, UserLoginView, UserLogoutView, UserPanelView, \
    UserUpdateView, UserPasswordUpdateView, UserPasswordResetView, UserPasswordSetView, UserDeleteView

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
]