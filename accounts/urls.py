from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.registro_usuario, name='signup'),

    # path('tasks/', views.tasks, name='tasks'),

    path('logout/', views.signout, name='logout'),

    path('login/', views.iniciar_sesion, name='login')

]
