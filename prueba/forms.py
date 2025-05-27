from django import forms
from .models import Activity, UserActivityAnswer

def get_activity_form(activity: Activity):
    class ActivityForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if activity.activity_type == 'text_input':
                self.fields['answer'] = forms.CharField(label=activity.question, widget=forms.TextInput)
            elif activity.activity_type == 'select':
                choices = [(opt, opt) for opt in activity.options]
                self.fields['answer'] = forms.ChoiceField(label=activity.question, choices=choices)
            elif activity.activity_type == 'checkbox':
                choices = [(opt, opt) for opt in activity.options]
                self.fields['answer'] = forms.MultipleChoiceField(
                    label=activity.question,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple
                )
            elif activity.activity_type == 'image_select':
                choices = [(opt, opt) for opt in activity.options]
                self.fields['answer'] = forms.ChoiceField(
                    label=activity.question,
                    choices=choices,
                    widget=forms.RadioSelect
                )
            else:  # Default fallback
                self.fields['answer'] = forms.CharField(label=activity.question)
    return ActivityForm