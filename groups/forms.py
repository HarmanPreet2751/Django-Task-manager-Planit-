from django import forms
from .models import Group, Task

class GroupForm(forms.ModelForm):
    allowed_emails = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter emails separated by commas",
        required=False
    )
    
    class Meta:
        model = Group
        fields = ['name', 'allowed_emails']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title']