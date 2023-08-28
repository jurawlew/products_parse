from django import forms


class ParseForm(forms.Form):
    category_id = forms.CharField(required=True)
    product_id = forms.CharField(required=True)
