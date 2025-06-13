from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm

urlpatterns = [
    path('signup/', views.registro_usuario, name='signup'),

    # path('tasks/', views.tasks, name='tasks'),

    path('logout/', views.signout, name='logout'),

    path('login/', views.iniciar_sesion, name='login'),

    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),

    # Mantener solo las que necesitás (sin done)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

]
