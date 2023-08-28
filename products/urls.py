from django.urls import path

from products.views import products_parse

urlpatterns = [
    path('parse', products_parse, name='parse')
]
