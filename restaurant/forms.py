import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Order


class CheckoutForm(forms.ModelForm):
    customer_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name',
        }),
        label='Full Name'
    )
    customer_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
            'autocomplete': 'tel',
        }),
        label='Phone Number'
    )
    table_number = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Table number (optional)',
        }),
        label='Table Number'
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'table_number']

    def clean_customer_name(self):
        name = self.cleaned_data['customer_name'].strip()
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        return name

    def clean_customer_phone(self):
        phone = self.cleaned_data['customer_phone'].strip()
        phone_digits = re.sub(r'\D', '', phone)
        if len(phone_digits) < 10:
            raise ValidationError(
                'Please enter a valid phone number with at least 10 digits.'
            )
        if len(phone_digits) > 15:
            raise ValidationError('Phone number is too long.')
        return phone

    def clean_table_number(self):
        table = self.cleaned_data.get('table_number', '').strip()
        return table
