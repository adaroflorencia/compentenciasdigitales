from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Subtopico, Answer
from django.contrib.auth.decorators import login_required
import json

def base_student(request):
    return render(request, 'sections_student/base_student.html')

def competencias(request):
    return render(request, 'sections_student/competencias.html', {
    })

def informacion_datos(request):
    return render(request, 'sections_student/informacion_datos.html')


@login_required
def result_form(request):
    # Obtener session_id del usuario actual
    session_id = request.session.session_key
    if not session_id:
        request.session.save()
        session_id = request.session.session_key

    # Obtener todas las respuestas asociadas con esta sesión
    respuestas = []

    # Mapeo de títulos para cada actividad
    titulos_actividades = {
        1: "Selecciona un motor de búsqueda",
        2: "Nombra el autor de un texto",
        3: "Nombra un navegador y un motor de búsqueda",
        4: "Investigación",
        5: "Enlaces de búsqueda",
        6: "Encuentra la imagen original",
        7: "¿Quién escribió el artículo?",
        8: "¿Qué es la infodemia?",
        9: "Prácticas para mejorar búsquedas en Internet",
        10: "Palabras entre comillas",
        11: "Ordenar pasos para una búsqueda efectiva",
        12: "Operador para excluir palabras",
        13: "Completar espacios en blanco"
    }

    # Mapeo de tipos de actividad para mostrar nombres amigables
    tipos_actividad = {
        'seleccion_imagenes': 'Selección de imágenes',
        'respuesta_libre': 'Respuesta de texto libre',
        'espacios_blanco': 'Completar espacios en blanco',
        'arrastrar_soltar': 'Ordenar elementos',
        'seleccion_opcion': 'Selección de opciones'
    }

    # Obtener todas las respuestas del usuario actual
    todas_respuestas = Answer.objects.filter(session_id=session_id).order_by('activity_id')

    for respuesta in todas_respuestas:
        # Formatear la respuesta del usuario para mostrarla de manera amigable
        user_response_display = respuesta.user_response

        # Si es una lista, mostrarla como texto separado por comas
        if isinstance(respuesta.user_response, list):
            user_response_display = ", ".join(map(str, respuesta.user_response))

        # Determinar la respuesta correcta según el tipo de actividad
        correct_answer = ""
        if respuesta.activity_type == 'seleccion_imagenes' and not respuesta.is_correct:
            correct_answer = "Imágenes 1 y 4 (Google y Mozilla Firefox)"
        elif respuesta.activity_id == 2 and not respuesta.is_correct:
            correct_answer = "Jorge Luis Borges"
        # Añadir más casos según sea necesario para cada actividad

        # Añadir la información formateada
        respuestas.append({
            'id': respuesta.id,
            'titulo': titulos_actividades.get(respuesta.activity_id, f"Actividad {respuesta.activity_id}"),
            'activity_type': respuesta.activity_type,
            'activity_type_display': tipos_actividad.get(respuesta.activity_type, respuesta.activity_type),
            'user_response': respuesta.user_response,
            'user_response_display': user_response_display,
            'is_correct': respuesta.is_correct,
            'correct_answer': correct_answer
        })

    # Calcular estadísticas
    correctas = sum(1 for r in respuestas if r['is_correct'])
    incorrectas = len(respuestas) - correctas
    porcentaje_completado = 0

    # Calcular el porcentaje de actividades completadas (asumiendo un total de 13)
    total_actividades = 13  # Según la plantilla competencias.html
    if total_actividades > 0:
        porcentaje_completado = int((len(respuestas) / total_actividades) * 100)

    context = {
        'respuestas': respuestas,
        'correctas': correctas,
        'incorrectas': incorrectas,
        'total': len(respuestas),
        'porcentaje_completado': porcentaje_completado,
    }

    return render(request, 'sections_student/result_form.html', context)


@login_required
def guardar_respuesta(request):
    try:
        data = json.loads(request.body)

        activity_id = data.get('activity_id')
        activity_type = data.get('activity_type')
        user_response = data.get('user_response')
        is_correct = data.get('is_correct')
        subtopic_id = data.get('subtopic_id')

        # Validación
        if None in [activity_id, activity_type, user_response, is_correct, subtopic_id]:
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)

        subtopic = Subtopico.objects.get(id=subtopic_id)

        session_id = request.session.session_key
        if not session_id:
            request.session.save()
            session_id = request.session.session_key

        Answer.objects.create(
            session_id=session_id,
            activity_id=activity_id,
            activity_type=activity_type,
            user_response=user_response,
            is_correct=is_correct,
            subtopic=subtopic
        )

        return JsonResponse({'status': 'ok'})

    except Subtopico.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Subtópico no encontrado'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)