from django import forms
from .models import ReviewRating


# for Review Rating forms of a user
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']
