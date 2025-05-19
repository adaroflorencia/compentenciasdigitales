from django.urls import path
from . import views

urlpatterns = [
    path('competencias/', views.competencias, name='competencias'),

    path('base_student/', views.base_student, name='base_student'),

    path('sections_student/', views.informacion_datos, name='informacion_datos'),

    path('guardar_respuesta/', views.guardar_respuesta, name='guardar_respuesta'),

    path('result_form/', views.result_form, name='result_form')

]
