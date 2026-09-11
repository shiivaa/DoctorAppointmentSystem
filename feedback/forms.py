from django import forms
from .models import Feedback
from django.utils.translation import gettext_lazy as _

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rate', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Write your experience of last appointment')
            }),
        }
        labels = {
            'rating': _('Rank'),
            'comment': _('Text of Comment'),
        }