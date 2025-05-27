from django.db import models
from accounts.models import Role, CustomUser
from form.models import Topic
from django.core.exceptions import ValidationError

class Topico(models.Model):
    nombre_topico = models.ForeignKey(Topic, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.nombre_topico}"


class Subtopico(models.Model):
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE)
    nombre_subtopico = models.TextField()

    def __str__(self):
        return f"{self.topico.nombre_topico} - {self.nombre_subtopico}"

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('image_select', 'Image Select'),
        ('checkbox', 'Checkbox'),
        ('text_input', 'Text Input'),
        ('select', 'Select'),
        ('other', 'Other'),
    ]
    subtopic = models.ForeignKey(Subtopico, on_delete=models.CASCADE, related_name='activities')
    order = models.PositiveIntegerField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='text_input')
    question = models.TextField()
    subquestion = models.TextField()
    options = models.JSONField(blank=True, null=True, help_text="Lista de opciones si aplica")
    correct_answer = models.JSONField(help_text="Respuesta(s) correcta(s) según el tipo", default=list)
    custom_style = models.TextField(blank=True, null=True, help_text="CSS opcional")
    image = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.subtopic} - {self.question[:30]}..."

class UserActivityAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    answer = models.JSONField()
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'activity')


