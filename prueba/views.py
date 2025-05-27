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

def base_activity(request):
    first_activity = Activity.objects.order_by('order').first()
    if first_activity:
        return redirect('activity_flow', activity_id=first_activity.id)
    else:
        return render(request, 'activities/no_activities.html')

def evaluate_answer(activity, user_answer):
    correct = activity.correct_answer
    if activity.activity_type == 'checkbox':
        # Both should be lists, compare after sorting
        return sorted(user_answer) == sorted(correct)
    elif activity.activity_type in ['select', 'image_select', 'text_input']:
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

    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer']
            # For checkbox, ensure it's a list
            if activity.activity_type == 'checkbox' and isinstance(answer, str):
                answer = [answer]
            is_correct = evaluate_answer(activity, answer)
            # Save or update answer
            obj, created = UserActivityAnswer.objects.update_or_create(
                user=request.user,
                activity=activity,
                defaults={'answer': answer, 'is_correct': is_correct}
            )
            # Next activity logic
            next_activity = Activity.objects.filter(
                subtopic=activity.subtopic, order__gt=activity.order
            ).order_by('order').first()
            if not next_activity:
                # Check across all subtopics (for 5 activities)
                all_acts = Activity.objects.all().order_by('order')
                user_done = UserActivityAnswer.objects.filter(user=request.user).count()
                if user_done >= 5:
                    return redirect('feedback')
                next_activity = all_acts[user_done] if user_done < all_acts.count() else None
            if next_activity:
                return redirect('activity_flow', activity_id=next_activity.id)
            else:
                return redirect('feedback')
    else:
        form = ActivityForm(initial={'answer': user_answer_obj.answer if user_answer_obj else None})

    template = f'activities/base_{activity.activity_type}.html'
    return render(request, template, {
        'activity': activity,
        'form': form,
        'user_answer': user_answer_obj
    })

@login_required
def feedback(request):
    # Get the first 5 activities answered by the user
    answers = UserActivityAnswer.objects.filter(user=request.user).order_by('answered_at')[:5]
    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    return render(request, 'activities/feedback.html', {
        'answers': answers,
        'total': total,
        'correct': correct,
    })