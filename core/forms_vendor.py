# forms_vendor.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Vendor
from django.forms.widgets import FileInput
import os

User = get_user_model()

class VendorSignupForm(UserCreationForm):
    title       = forms.CharField(max_length=150, required=True, label="Vendor Name")
    contact     = forms.CharField(max_length=15, required=True, label="Contact Number")
    email       = forms.EmailField(required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)
    address     = forms.CharField(widget=forms.Textarea, required=True)
    iso_certificate = forms.FileField(
        required=True,
        help_text="Upload your ISO 14000 certificate in PDF format."
    )

    class Meta:
        model  = get_user_model()
        fields = ['title','contact','email','password1','password2']

    def clean_iso_certificate(self):
        certificate = self.cleaned_data.get('iso_certificate', None)
        if certificate:
            ext = os.path.splitext(certificate.name)[1].lower()
            if ext != '.pdf':
                raise forms.ValidationError("Please upload a PDF file.")
        return certificate

from django import forms
from .models import Product, Product_Images, Category, Vendor
from taggit.forms import TagWidget

class MultiFileInput(FileInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['multiple'] = 'multiple'
        return super().render(name, value, attrs, renderer)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'image', 'description', 'category', 'price', 'old_price',
            'specifications', 'carbon_footprint_level', 'material_sourcing',
            'recyclability_level', 'water_usage', 'energy_efficiency',
            'biodegradability_level', 'durability', 'product_status',
            'in_stock', 'featured', 'digital', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'specifications': forms.Textarea(attrs={'rows': 4}),
            'tags': TagWidget(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'carbon_footprint_level': forms.Select(attrs={'class': 'form-control'}),
            'material_sourcing': forms.Select(attrs={'class': 'form-control'}),
            'recyclability_level': forms.Select(attrs={'class': 'form-control'}),
            'water_usage': forms.Select(attrs={'class': 'form-control'}),
            'energy_efficiency': forms.Select(attrs={'class': 'form-control'}),
            'biodegradability_level': forms.Select(attrs={'class': 'form-control'}),
            'product_status': forms.Select(attrs={'class': 'form-control'}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'digital': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['in_stock', 'featured', 'digital']:
                field.widget.attrs.update({'class': 'form-control'})

class ProductImagesForm(forms.Form):
    images = forms.FileField(
        widget=MultiFileInput(attrs={'class': 'form-control'}),
        required=False
    )