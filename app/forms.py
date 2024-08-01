from django import forms
from .models import Product

class ProductSearchForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
