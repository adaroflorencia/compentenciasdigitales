import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Question, Option, TopicResult

def docente(request):
    return render(request, 'form/docentes.html')

def estudiante(request):
    return render(request, 'form/estudiantes.html')


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
    # Si ya completó el formulario, redirigir a resultados
    if TopicResult.objects.filter(user=request.user).exists():
        return redirect('results')

    # Obtener todas las preguntas solo si no están en la sesión
    if 'all_questions' not in request.session:
        all_questions = list(get_questions_by_role(request.user))

        # Guardar los IDs de las preguntas en la sesión
        request.session['all_questions'] = [q.id for q in all_questions]
    else:
        # Recuperar las preguntas usando los IDs guardados
        # Prueba de recuperación??
        question_ids = request.session['all_questions']
        all_questions = list(Question.objects.filter(id__in=question_ids))

    # Inicializar variables de sesión si no existen
    if 'answers' not in request.session:
        request.session['answers'] = {}
    if 'current_question' not in request.session:
        request.session['current_question'] = 0
    if 'topic_scores' not in request.session:
        request.session['topic_scores'] = {}
    if 'accumulated_questions' not in request.session:
        request.session['accumulated_questions'] = []
    if 'total_score' not in request.session:
        request.session['total_score'] = 0

    current_question_index = request.session['current_question']

    # Si es la última pregunta y ya fue respondida, ir a resultados
    if current_question_index >= len(all_questions):
        request.session['form_completed'] = True
        return redirect('results')

    current_question = all_questions[current_question_index]
    current_topic = current_question.topic
    options = Option.objects.filter(question=current_question)

    if request.method == 'POST':
        selected_option = request.POST.get('option')

        if selected_option:
            try:
                option = Option.objects.get(id=selected_option)

                # Guardar la respuesta
                answers = request.session['answers']
                answers[str(current_question.id)] = selected_option
                request.session['answers'] = answers

                # Actualizar puntaje solo si la pregunta no ha sido respondida antes
                accumulated_questions = request.session['accumulated_questions']
                if str(current_question.id) not in accumulated_questions:
                    request.session['total_score'] += option.score
                    accumulated_questions.append(str(current_question.id))
                    request.session['accumulated_questions'] = accumulated_questions

                    topic_scores = request.session['topic_scores']
                    topic_name = current_topic.name
                    topic_scores[topic_name] = topic_scores.get(topic_name, 0) + option.score
                    request.session['topic_scores'] = topic_scores

                # Si se presiona el botón de finalizar en la última pregunta
                if 'finish' in request.POST and current_question_index == len(all_questions) - 1:
                    request.session['form_completed'] = True
                    request.session.modified = True
                    return redirect('results')

            except Option.DoesNotExist:
                logging.error(f"Option with ID {selected_option} not found")

        # Procesar navegación
        if 'next' in request.POST:
            request.session['current_question'] += 1
        elif 'previous' in request.POST:
            request.session['current_question'] = max(0, request.session['current_question'] - 1)

        request.session.modified = True
        return redirect('evaluate')

    # Recuperar respuesta guardada
    saved_answer = request.session['answers'].get(str(current_question.id), '')

    # Calcular progreso
    progress = int((current_question_index / len(all_questions)) * 100) if all_questions else 0

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
        'total_questions': len(all_questions)
    }

    return render(request, 'form/evaluate.html', context)


@login_required
def results(request):
    try:
        # Check if results already exist in database
        existing_results = TopicResult.objects.filter(user=request.user)

        if existing_results.exists():
            # Return existing results from database
            final_results = {}
            total_score = 0
            total_questions = 0

            for result in existing_results:
                score_percentage = result.score
                final_results[result.topic.name] = {
                    'score': (score_percentage * 100) / 6,
                    'total_questions': result.total_questions,
                    'answered_questions': result.total_questions,
                    'level': result.level
                }
                total_score += result.score
                total_questions += 1

            average_total = round(total_score / total_questions, 2) if total_questions > 0 else 0

        else:
            # Check if form is completed and results need to be saved
            if not request.session.get('form_completed'):
                return redirect('evaluate')

            topic_scores = request.session.get('topic_scores')
            if not topic_scores:
                return redirect('evaluate')

            # Calculate and save results only if they haven't been saved before
            questions = get_questions_by_role(request.user)
            questions_by_topic = {}
            final_results = {}

            for question in questions:
                if question.topic not in questions_by_topic:
                    questions_by_topic[question.topic] = []
                questions_by_topic[question.topic].append(question)

            accumulated_questions = request.session.get('accumulated_questions', [])
            total_questions_answered = len(accumulated_questions)
            total_score = request.session.get('total_score', 0)

            for topic, questions_list in questions_by_topic.items():
                if topic.name in topic_scores:
                    questions_answered = len([q.id for q in questions_list if str(q.id) in accumulated_questions])

                    if questions_answered > 0:
                        average_score = (topic_scores[topic.name] * 100) / (questions_answered * 6)
                        level = determine_level(average_score)

                        # Save results to database
                        TopicResult.objects.create(
                            topic=topic,
                            user=request.user,
                            score=round(average_score, 2),
                            level=level,
                            total_questions=len(questions_list)
                        )

                        final_results[topic.name] = {
                            'score': round(average_score, 2),
                            'total_questions': len(questions_list),
                            'answered_questions': questions_answered,
                            'level': level
                        }

            average_total = round(total_score / total_questions_answered, 2) if total_questions_answered > 0 else 0

            # Clear session after saving results
            session_keys = ['answers', 'current_question', 'topic_scores',
                            'accumulated_questions', 'total_score', 'all_questions', 'form_completed']
            for key in session_keys:
                if key in request.session:
                    del request.session[key]

        total_level = determine_level(average_total)

        return render(request, 'form/results.html', {
            'results': final_results,
            'total_score': average_total,
            'user_role': request.user.role.name if request.user.role else None,
            'total_level': total_level,
        })

    except Exception as e:
        logging.error(f"Error procesando resultados para usuario {request.user.email}: {e}")
        if TopicResult.objects.filter(user=request.user).exists():
            return redirect('results')
        return redirect('evaluate')


def determine_level(score):

    if 0 <= score < 2 :
        return 'A1'
    elif score < 3:
        return 'A2'
    elif score < 4:
        return 'B1'
    elif score < 5:
        return 'B2'
    elif score < 6:
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