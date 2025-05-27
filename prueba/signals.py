from django.db.models.signals import post_migrate
from django.apps import apps
from django.core.management import call_command

def load_initial_activities(sender, **kwargs):
    if sender.name == 'activities':
        call_command('loaddata', 'initial_activities.json', app_label='prueba')

post_migrate.connect(load_initial_activities)