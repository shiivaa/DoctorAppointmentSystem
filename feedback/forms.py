from django import forms
from .models import Feedback
from django.utils.translation import gettext_lazy as _

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rate', 'comment']
        widgets = {
            'rate': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with the visit and the doctor...'
            }),
        }
        labels = {
            'rate': 'Your Rating',
            'comment': 'Review / Comment',
        }