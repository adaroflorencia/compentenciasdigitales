
from django.contrib import admin
from .models import Topico, Subtopico, Answer, ResultadoTopico

admin.site.register(Topico)
admin.site.register(Subtopico)
admin.site.register(Answer)
admin.site.register(ResultadoTopico)