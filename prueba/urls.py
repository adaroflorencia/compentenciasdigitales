from django.urls import path
from . import views

urlpatterns = [
    path('competencias/', views.competencias, name='competencias'),

    path('activities/', views.obtener_actividad_aleatoria, name='obtener_actividad_aleatoria'),

    path('menu_activities/', views.menu_activities, name= 'menu_activities')

]
