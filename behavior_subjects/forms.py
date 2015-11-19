from django import forms
from .models import Mouse, Session


class UploadForm(forms.Form):
    file = forms.FileField(label="Add a session", help_text='max. 42 megabytes')

class MouseForm(forms.ModelForm):
    class Meta:
        model = Mouse
        fields = ['mouse_number', 'surgery_date', 'dob', 'sex', 'genotype']

class SessionNotesForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['bad', 'notes']
