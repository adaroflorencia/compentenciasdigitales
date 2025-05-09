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
