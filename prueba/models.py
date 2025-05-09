from django.db import models
from accounts.models import Role, CustomUser
from form.models import Topic
from django.contrib.postgres.fields import ArrayField


class Topico(models.Model):
    topicos = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='topicos')
    def __str__(self):
        return f"{self.topicos.name}"


class Subtopico(models.Model):
    titulo = models.CharField(max_length=100)
    topico = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopicos')

    def __str__(self):
        return f"{self.titulo} ({self.topico.name})"

class Answer(models.Model):
    session_id = models.CharField(max_length=64)
    activity_id = models.IntegerField()
    activity_type = models.CharField(max_length=50)
    user_response = models.JSONField()
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    subtopic = models.ForeignKey(Subtopico, on_delete=models.CASCADE, related_name='actividades')


class ResultadoTopico(models.Model):
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE, related_name='resultados')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    puntaje_obtenido = models.FloatField(default=0)
    puntaje_total = models.FloatField(default=0)
    porcentaje = models.FloatField(default=0)

    completado = models.BooleanField(default=False)

    def calcular_porcentaje(self):
        if self.puntaje_total > 0:
            self.porcentaje = round((self.puntaje_obtenido / self.puntaje_total) * 100, 2)
        else:
            self.porcentaje = 0
        self.save()

    def __str__(self):
        return f"{self.topico.titulo} - {self.porcentaje}%"
