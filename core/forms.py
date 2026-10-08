# core/forms.py
from django import forms
from .models import Product_Reivew


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Product_Reivew
        fields = ['rating', 'review']  # rating & review are from your Product_Reivew model.

        widgets = {
            'rating': forms.RadioSelect(
                choices=[
                    (1, '1 - ★☆☆☆☆'),
                    (2, '2 - ★★☆☆☆'),
                    (3, '3 - ★★★☆☆'),
                    (4, '4 - ★★★★☆'),
                    (5, '5 - ★★★★★'),
                ]
            ),
            'review': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'})
        }
class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        label="Verification Code",
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit code'}),
    )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise forms.ValidationError("Code must contain only digits.")
        return code