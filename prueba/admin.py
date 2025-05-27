from django.contrib import admin
from .models import Topico, Subtopico, Activity, UserActivityAnswer

admin.site.register(Topico)
admin.site.register(Subtopico)
admin.site.register(Activity)
admin.site.register(UserActivityAnswer)

