import pandas
from django.shortcuts import render

from clickhouse_driver import Client

from products.forms import ParseForm


def products_parse(request):
    if request.method == 'POST':
        form = ParseForm(request.POST)
        if form.is_valid():
            category_id = form.cleaned_data.get('category_id')
            product_id = form.cleaned_data.get('product_id')

            client = Client(host='',
                            user='',
                            password='',
                            port='9000')

            attrs_ca = client.execute("SELECT ca.attribute_id, ca.attribute_name, ca.description, ca.required, "
                                      "ca.dictionary_value, ca.data_type, pa.value FROM categories c "
                                      "JOIN category_attrs ca ON c.category_id=ca.category_id "
                                      "LEFT JOIN product_attr pa ON ca.attribute_id = pa.attribute_id "
                                      f"WHERE c.category_id = '{category_id}' AND pa.product_id = '{product_id}'")
            print(attrs_ca)
    else:
        form = ParseForm()
    return render(request, 'parse.html', {'form': form})
