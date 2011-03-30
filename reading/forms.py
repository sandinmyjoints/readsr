from django import forms
from reading.models import Reading
from datetime import time

class ReadingForm(forms.ModelForm):
	description = forms.CharField(widget=forms.Textarea)

	class Meta:
		model = Reading	
		exclude = ('series',)