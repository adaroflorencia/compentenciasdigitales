from django.urls import path
from . import views

urlpatterns = [
    path('competencias/', views.competencias, name='competencias'),
    path('base_student/', views.base_student, name='base_student'),
    path('sections_alfabetizacion/', views.informacion_datos, name='informacion_datos'),
    path('sections_comunicacion/', views.comunicacion_colaboracion, name='comunicacion_colaboracion'),
    path('contenido_digital/', views.contenido_digital, name='contenido_digital'),
    path('seguridad_digital/', views.seguridad_digital, name= 'seguridad_digital'),
    path('resolucion_problemas/', views.resolucion_problemas, name= 'resolucion_problemas'),
    path('activity/<int:activity_id>/', views.activity_flow, name='activity_flow'),
    path('feedback/', views.feedback, name='feedback'),
    path('base_activity/', views.base_activity, name='base_activity'),


]
