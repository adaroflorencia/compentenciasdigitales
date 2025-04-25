from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Actividad, ResultadoTopico, Subtopico
from django.contrib.auth.decorators import login_required
import json

def menu_activities(request):
    return render(request, 'activities/menu_activities.html')

def competencias(request):
    actividad = Actividad.objects.first()
    total_actividades = Actividad.objects.count()

    return render(request, 'form/competencias.html', {
        'actividad': actividad,
        'total_actividades': total_actividades,
    })


def obtener_actividad_aleatoria(request, subtopico_id=None):
    if subtopico_id is None:
        subtopico = Subtopico.objects.order_by('?').first()
        if not subtopico:
            return render(request, 'error.html', {'message': 'No hay subtópicos disponibles'})
    else:
        subtopico = get_object_or_404(Subtopico, id=subtopico_id)

    actividad = Actividad.objects.filter(subtopico=subtopico).order_by('?').first()
    if not actividad:
        return render(request, 'error.html', {'message': 'No hay actividades disponibles'})

    return render(request, 'activities/actividad.html', {
        'actividad': actividad,
        'subtopico': subtopico,
        'total_actividades': Actividad.objects.filter(subtopico=subtopico).count()
    })


def evaluar_respuesta(request):
    if request.method == 'POST':
        actividad_id = request.POST.get('actividad_id')
        respuesta_usuario = json.loads(request.POST.get('respuesta_usuario', '[]'))

        actividad = get_object_or_404(Actividad, id=actividad_id)
        puntaje = actividad.evaluar(respuesta_usuario)

        return render(request, 'activities/resultado.html', {
            'actividad': actividad,
            'puntaje': puntaje
        })

@login_required
def guardar_puntaje(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        actividad_id = data.get('actividad_id')
        respuesta_usuario = data.get('respuesta_usuario')

        try:
            actividad = Actividad.objects.get(id=actividad_id)

            # Evaluamos y guardamos el puntaje
            actividad.evaluar(respuesta_usuario)

            # Actualizar resultado por tópico
            subtopico = actividad.subtopico
            topico = subtopico.topico
            user = actividad.user

            resultado, creado = ResultadoTopico.objects.get_or_create(
                topico=topico,
                user=user
            )

            actividades = Actividad.objects.filter(user=user, subtopico__topico=topico)

            resultado.puntaje_total = sum(a.puntaje_total for a in actividades)
            resultado.puntaje_obtenido = sum(a.puntaje_obtenido or 0 for a in actividades)
            resultado.calcular_porcentaje()

            return JsonResponse({
                "status": "ok",
                "puntaje_obtenido": actividad.puntaje_obtenido,
                "puntaje_total": actividad.puntaje_total,
                "porcentaje_topico": resultado.porcentaje
            })

        except Actividad.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Actividad no encontrada"}, status=404)
