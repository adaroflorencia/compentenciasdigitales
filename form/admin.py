
from django.contrib import admin
from .models import Topic, Question, Option, Answer

admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Answer)