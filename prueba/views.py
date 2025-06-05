# views.py corregido
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Activity, UserActivityAnswer
from .forms import get_activity_form
from django.urls import reverse


def base_student(request):
    return render(request, 'sections_assessment/base_student.html')


def competencias(request):
    return render(request, 'sections_alfabetizacion/competencias.html', {
    })


def informacion_datos(request):
    return render(request, 'sections_alfabetizacion/base_alfabetizacion.html')


def comunicacion_colaboracion(request):
    return render(request, 'sections_comunicacion/base_comunicacion.html')

def contenido_digital(request):
    return render(request, 'sections_contenido_digital/base_contenido.html')


def base_activity(request):
    first_activity = Activity.objects.order_by('order').first()
    if first_activity:
        return redirect('activity_flow', activity_id=first_activity.id)
    else:
        return render(request, 'activities/no_activities.html')


def evaluate_answer(activity, user_answer):
    correct = activity.correct_answer
    logging.debug(
        f"Evaluating answer for activity {activity.id}: user_answer={user_answer}, correct={correct}, type={activity.activity_type}")

    if activity.activity_type == 'checkbox':
        # Para checkbox, tanto user_answer como correct deberían ser listas
        if isinstance(correct, str):
            correct = [correct]  # Convertir a lista si es string
        if isinstance(user_answer, str):
            user_answer = [user_answer]  # Convertir a lista si es string
        return sorted(user_answer) == sorted(correct)

    elif activity.activity_type == 'image_select':
        # Para image_select con múltiples respuestas correctas
        if isinstance(correct, list) and isinstance(user_answer, str):
            return user_answer in correct
        elif isinstance(correct, list) and isinstance(user_answer, list):
            return sorted(user_answer) == sorted(correct)
        else:
            return user_answer == correct

    elif activity.activity_type in ['select', 'text_input']:
        # Para text_input, hacer comparación case-insensitive y sin espacios
        if activity.activity_type == 'text_input':
            if isinstance(user_answer, str) and isinstance(correct, str):
                return user_answer.strip().lower() == correct.strip().lower()
        return user_answer == correct

    else:
        return user_answer == correct


def base_activity_redirect(request):
    first_activity = Activity.objects.order_by('order').first()
    if first_activity:
        logging.debug(f"Redirecting to first activity: {first_activity.id}")
        return redirect('activity_flow', activity_id=first_activity.id)
    else:
        logging.error("No activities found in database")
    return render(request, 'activities/no_activities.html')


@login_required
def activity_flow(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    ActivityForm = get_activity_form(activity)
    user_answer_obj = UserActivityAnswer.objects.filter(user=request.user, activity=activity).first()

    logging.debug(f"Processing activity {activity_id}, type: {activity.activity_type}")

    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer']
            logging.debug(f"Form answer: {answer}, type: {type(answer)}")

            # No modificar la respuesta aquí, dejar que evaluate_answer maneje los tipos
            is_correct = evaluate_answer(activity, answer)
            logging.debug(f"Answer is correct: {is_correct}")

            # Guardar respuesta
            obj, created = UserActivityAnswer.objects.update_or_create(
                user=request.user,
                activity=activity,
                defaults={'answer': answer, 'is_correct': is_correct}
            )

            logging.debug(f"Answer saved: {obj.answer}, correct: {obj.is_correct}")

            # Contar total de actividades respondidas
            total_answered = UserActivityAnswer.objects.filter(user=request.user).count()
            logging.debug(f"Total answered: {total_answered}")

            # Si ya respondió 5, ir a feedback
            if total_answered >= 5:
                logging.debug("Redirecting to feedback - 5 activities completed")
                return redirect('feedback')

            # Buscar siguiente actividad por orden
            next_activity = Activity.objects.filter(order__gt=activity.order).order_by('order').first()
            logging.debug(f"Next activity: {next_activity.id if next_activity else 'None'}")

            if next_activity:
                return redirect('activity_flow', activity_id=next_activity.id)
            else:
                logging.debug("No more activities, redirecting to feedback")
                return redirect('feedback')
    else:
        # Inicializar formulario con respuesta previa si existe
        initial_data = {}
        if user_answer_obj:
            initial_data['answer'] = user_answer_obj.answer
        form = ActivityForm(initial=initial_data)

    template = f'activities/base_{activity.activity_type}.html'
    logging.debug(f"Rendering template: {template}")

    return render(request, template, {
        'activity': activity,
        'form': form,
        'user_answer': user_answer_obj
    })


@login_required
def feedback(request):
    # Obtener todas las respuestas del usuario ordenadas por el orden de la actividad
    all_answers = UserActivityAnswer.objects.filter(
        user=request.user
    ).select_related('activity').order_by('activity__order')

    logging.debug(f"Feedback: Found {all_answers.count()} answers for user {request.user}")

    # Calcular correctas ANTES de hacer slice
    correct = all_answers.filter(is_correct=True).count()

    # Tomar solo las primeras 5 respuestas para mostrar
    answers_to_show = all_answers[:5]
    total = len(answers_to_show)  # Usar len() en lugar de count() después del slice

    # Agregar feedback personalizado a cada respuesta
    for answer in answers_to_show:
        if answer.is_correct:
            answer.feedback = "¡Excelente! Respuesta correcta."
        else:
            answer.feedback = f"Respuesta incorrecta. La respuesta correcta era: {answer.activity.correct_answer}"

    return render(request, 'activities/feedback.html', {
        'answers': answers_to_show,
        'total': total,
        'correct': correct,
    })