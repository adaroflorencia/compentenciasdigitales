import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Question, Option, TopicResult

def docente(request):
    return render(request, 'form/docentes.html')

def estudiante(request):
    return render(request, 'form/estudiantes.html')

def nodocentes(request):
    return render(request, 'form/noDocentes.html')


def get_questions_by_role(user):
    try:
        if not user.role:
            logging.warning(f"El usuario {user.email} no tiene un rol asignado")
            return Question.objects.none()

        #El admin puede visualizar todas las preguntas
        if user.role.name == 'administrador':
            questions = Question.objects.all()
            return questions

        #Traer tópicos asociados al rol
        topic = Topic.objects.filter(role=user.role)

        if not topic.exists():
            logging.warning(f"No Se encontró ningún tópico para el rol {user.role.name}")
            return Question.objects.none()

        #Almacenar preguntas por tópico
        questions = Question.objects.filter(topic__in=topic)

        return questions

    except Exception as e:
        logging.error(f"Error al obtener preguntas para el usuario {user.email}: {e}")
        return Question.objects.none()


@login_required
def evaluate(request):
    if TopicResult.objects.filter(user=request.user).exists():
        return redirect('results')

    # Obtener todas las preguntas solo si no están en la sesión
    if 'all_questions' not in request.session:
        all_questions = list(get_questions_by_role(request.user))
        request.session['all_questions'] = [q.id for q in all_questions]
    else:
        question_ids = request.session['all_questions']
        all_questions = list(Question.objects.filter(id__in=question_ids))

    # Inicializar variables de sesión
    if 'answers' not in request.session:
        request.session['answers'] = {}
    if 'current_question' not in request.session:
        request.session['current_question'] = 0
    if 'topic_scores' not in request.session:
        request.session['topic_scores'] = {}
    if 'question_scores' not in request.session:  # Nuevo: guardar puntaje por pregunta
        request.session['question_scores'] = {}

    current_question_index = request.session['current_question']

    # Verificar si es la última pregunta y todas están respondidas
    if current_question_index >= len(all_questions):
        if len(request.session['answers']) == len(all_questions):
            request.session['form_completed'] = True
            return redirect('results')
        else:
            # Redirigir a la primera pregunta sin responder
            for i, q in enumerate(all_questions):
                if str(q.id) not in request.session['answers']:
                    request.session['current_question'] = i
                    current_question_index = i
                    break

    current_question = all_questions[current_question_index]
    current_topic = current_question.topic
    options = Option.objects.filter(question=current_question)

    if request.method == 'POST':
        selected_option = request.POST.get('option')

        # Validación para el botón "next"
        if 'next' in request.POST:
            if not selected_option and str(current_question.id) not in request.session['answers']:

                context = {
                    'question': current_question,
                    'topic': current_topic,
                    'options': options,
                    'progress': int((len(request.session['answers']) / len(all_questions)) * 100),
                    'saved_answer': request.session['answers'].get(str(current_question.id), ''),
                    'has_previous': current_question_index > 0,
                    'has_next': current_question_index < len(all_questions) - 1,
                    'topic_scores': request.session.get('topic_scores', {}),
                    'current_index': current_question_index + 1,
                    'total_questions': len(all_questions),
                    'answered_questions': len(request.session['answers']),
                    'user_role': request.user.role.name if request.user.role else None,
                    'error_message': 'Por favor, seleccione una opción antes de continuar.'
                }
                return render(request, 'form/evaluate.html', context)

        if selected_option:
            try:
                option = Option.objects.get(id=selected_option)
                question_id = str(current_question.id)
                topic_name = current_topic.name

                # Actualizar respuestas y puntajes
                answers = request.session['answers']
                topic_scores = request.session['topic_scores']
                question_scores = request.session['question_scores']

                # Si ya existía una respuesta, restar el puntaje anterior
                if question_id in answers:
                    old_score = question_scores.get(question_id, 0)
                    topic_scores[topic_name] = topic_scores.get(topic_name, 0) - old_score

                # Guardar nueva respuesta y puntaje
                answers[question_id] = selected_option
                question_scores[question_id] = option.score
                topic_scores[topic_name] = topic_scores.get(topic_name, 0) + option.score

                # Actualizar sesión
                request.session['answers'] = answers
                request.session['topic_scores'] = topic_scores
                request.session['question_scores'] = question_scores

                # Si se presiona finalizar, verificar que todas las preguntas estén respondidas
                if 'finish' in request.POST:
                    if len(answers) == len(all_questions):
                        request.session['form_completed'] = True
                        request.session.modified = True
                        return redirect('results')
                    else:
                                              return redirect('evaluate')

            except Option.DoesNotExist:
                logging.error(f"Option with ID {selected_option} not found")

        # Procesar navegación
        if 'next' in request.POST and current_question_index < len(all_questions) - 1:
            request.session['current_question'] += 1
        elif 'previous' in request.POST and current_question_index > 0:
            request.session['current_question'] -= 1

        request.session.modified = True
        return redirect('evaluate')

    # Recuperar respuesta guardada
    saved_answer = request.session['answers'].get(str(current_question.id), '')

    # Calcular progreso
    progress = int((len(request.session['answers']) / len(all_questions)) * 100)

    context = {
        'question': current_question,
        'topic': current_topic,
        'options': options,
        'progress': progress,
        'saved_answer': saved_answer,
        'has_previous': current_question_index > 0,
        'has_next': current_question_index < len(all_questions) - 1,
        'topic_scores': request.session.get('topic_scores', {}),
        'current_index': current_question_index + 1,
        'total_questions': len(all_questions),
        'answered_questions': len(request.session['answers']),
        'user_role': request.user.role.name if request.user.role else None
    }

    return render(request, 'form/evaluate.html', context)


@login_required
def results(request):
    try:
        existing_results = TopicResult.objects.filter(user=request.user)

        if existing_results.exists():
            # Resultados ya existen en la base de datos
            final_results = {}
            total_points = 0
            total_possible_points = 0

            for result in existing_results:
                # Cada pregunta vale 6 puntos máximo
                max_points_per_topic = result.total_questions * 6
                points = (result.score * max_points_per_topic) / 100

                final_results[result.topic.name] = {
                    'score': round(result.score, 2),  # Ya está en porcentaje
                    'total_questions': result.total_questions,
                    'answered_questions': result.total_questions,
                    'level': result.level
                }
                total_points += points
                total_possible_points += max_points_per_topic

            average_total = round((total_points / total_possible_points) * 100, 2) if total_possible_points > 0 else 0

        else:
            # Verificar si el formulario está completo
            if not request.session.get('form_completed'):
                return redirect('evaluate')

            topic_scores = request.session.get('topic_scores', {})
            answers = request.session.get('answers', {})

            if not topic_scores or not answers:
                return redirect('evaluate')

            # Calcular y guardar resultados
            questions = get_questions_by_role(request.user)
            questions_by_topic = {}
            final_results = {}
            total_points = 0
            total_possible_points = 0

            # Agrupar preguntas por tópico
            for question in questions:
                if question.topic not in questions_by_topic:
                    questions_by_topic[question.topic] = []
                questions_by_topic[question.topic].append(question)

            # Calcular resultados por tópico
            for topic, questions_list in questions_by_topic.items():
                if topic.name in topic_scores:
                    total_questions = len(questions_list)
                    max_points_possible = total_questions * 6  # 6 puntos máximo por pregunta
                    topic_points = topic_scores[topic.name]

                    # Calcular porcentaje real
                    score_percentage = (topic_points / max_points_possible) * 100 if max_points_possible > 0 else 0

                    # Determinar nivel basado en el porcentaje
                    level = determine_level(score_percentage)

                    # Guardar en la base de datos
                    TopicResult.objects.create(
                        topic=topic,
                        user=request.user,
                        score=round(score_percentage, 2),
                        level=level,
                        total_questions=total_questions
                    )

                    final_results[topic.name] = {
                        'score': round(score_percentage, 2),
                        'total_questions': total_questions,
                        'answered_questions': len([q.id for q in questions_list if str(q.id) in answers]),
                        'level': level
                    }

                    total_points += topic_points
                    total_possible_points += max_points_possible

            # Calcular promedio total
            average_total = round((total_points / total_possible_points) * 100, 2) if total_possible_points > 0 else 0

            # Limpiar la sesión
            session_keys = [
                'answers', 'current_question', 'topic_scores',
                'question_scores', 'all_questions', 'form_completed'
            ]
            for key in session_keys:
                request.session.pop(key, None)

        total_level = determine_level(average_total)

        context = {
            'results': final_results,
            'total_score': average_total,
            'user_role': request.user.role.name if request.user.role else None,
            'total_level': total_level,
        }



        return render(request, 'form/results.html', context)

    except Exception as e:
        logging.error(f"Error procesando resultados para usuario {request.user.email}: {e}")
        if TopicResult.objects.filter(user=request.user).exists():
            return redirect('results')
        return redirect('evaluate')


def determine_level(percentage):
    if 0 <= percentage <= 16.66:
        return 'A1'
    elif percentage <= 33.33:
        return 'A2'
    elif percentage <= 50:
        return 'B1'
    elif percentage <= 66.66:
        return 'B2'
    elif percentage <= 83.33:
        return 'C1'
    else:
        return 'C2'


@login_required
def submit_answers(request):
    try:
        if not request.session.get('answers'):
            return redirect('evaluate.html')

        return redirect('results.html')

    except Exception as e:
        logging.error(f"Error en submit_answers: {e}")
        return redirect('results.html')