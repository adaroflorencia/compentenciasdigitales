from django.urls import path
from . import views

urlpatterns = [
    path('generar-pdf/<str:template_name>/', views.generar_pdf, name='generar_pdf'),
]
