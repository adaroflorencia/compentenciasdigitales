from django.db import models
from accounts.models import Role, CustomUser
from django.contrib.postgres.fields import ArrayField


class Topico(models.Model):
    titulo = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='topicos')

    def __str__(self):
        return f"{self.titulo} ({self.role.name})"


class Subtopico(models.Model):
    titulo = models.CharField(max_length=100)
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE, related_name='subtopicos')

    def __str__(self):
        return f"{self.titulo} ({self.topico.titulo})"


from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class Actividad(models.Model):
    TIPO_ACTIVIDAD = [
        ('opcion_multiple', 'Opción Múltiple'),
        ('seleccion_multiple', 'Selección Múltiple'),
        ('seleccion_imagenes', 'Selección de Imágenes'),
        ('vf', 'Verdadero/Falso'),
        ('completar', 'Completar'),
        ('respuesta_libre', 'Respuesta Libre')
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_ACTIVIDAD)
    titulo = models.TextField()
    contenido = models.TextField()
    subtopico = models.ForeignKey(Subtopico, on_delete=models.CASCADE, related_name='actividades')
    orden = models.PositiveIntegerField()
    opciones = ArrayField(models.CharField(max_length=200), blank=True, null=True)  # Para opción/selección múltiple
    opciones_imagenes = models.JSONField(blank=True, null=True)  # Ej: [{"imagen": "ruta.jpg", "es_correcta": true}]
    respuesta_correcta = models.JSONField()  # Formato varía por tipo
    respuesta_usuario = models.JSONField(blank=True, null=True)
    puntaje_total = models.FloatField(default=1.0)
    puntaje_obtenido = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ['orden']

    def get_template(self):
        return f"activities/{self.tipo}.html"

    def evaluar(self, respuesta_usuario):
        self.respuesta_usuario = respuesta_usuario
        self.puntaje_obtenido = 0.0

        if not self.respuesta_correcta:
            self.save()
            return 0.0

        try:
            if self.tipo == 'opcion_multiple':
                self.puntaje_obtenido = self.puntaje_total if respuesta_usuario == self.respuesta_correcta else 0.0

            elif self.tipo == 'seleccion_multiple':
                correctas = set(self.respuesta_correcta)
                usuario = set(respuesta_usuario)
                self.puntaje_obtenido = round(
                    (len(correctas.intersection(usuario)) / len(correctas)) * self.puntaje_total, 2)

            elif self.tipo == 'seleccion_imagenes':
                correctas = {idx for idx, img in enumerate(self.opciones_imagenes) if img['es_correcta']}
                usuario = set(respuesta_usuario)
                self.puntaje_obtenido = round(
                    len(correctas.intersection(usuario)) / (len(correctas) * self.puntaje_total),
                    2
                )

            elif self.tipo == 'completar':
                self.puntaje_obtenido = self.puntaje_total if respuesta_usuario.strip().lower() == self.respuesta_correcta.strip().lower() else 0.0

            elif self.tipo == 'respuesta_libre':
                coincidencias = sum(
                    1 for palabra in self.respuesta_correcta if palabra.lower() in respuesta_usuario.lower())
                self.puntaje_obtenido = round((coincidencias / len(self.respuesta_correcta)) * self.puntaje_total, 2)

                self.save()
            return self.puntaje_obtenido

        except (TypeError, AttributeError):
            return 0.0


class ResultadoTopico(models.Model):
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE, related_name='resultados')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    puntaje_obtenido = models.FloatField(default=0)
    puntaje_total = models.FloatField(default=0)
    porcentaje = models.FloatField(default=0)

    def calcular_porcentaje(self):
        if self.puntaje_total > 0:
            self.porcentaje = round((self.puntaje_obtenido / self.puntaje_total) * 100, 2)
        else:
            self.porcentaje = 0
        self.save()

    def __str__(self):
        return f"{self.topico.titulo} - {self.porcentaje}%"
