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

            categories_attrs = client.execute(
                "SELECT ca.attribute_id, ca.attribute_name, ca.description, ca.required, "
                "ca.dictionary_value, ca.data_type, ca.category_id FROM category_attrs AS ca "
                f"WHERE ca.category_id = '{category_id}'")

            products_attrs = client.execute(
                "SELECT pa.attribute_id, pa.attribute_name, pa.value, pa.product_id FROM product_attr AS pa "
                f"WHERE pa.product_id='{product_id}'")

            print(len(categories_attrs), len(products_attrs))
    else:
        form = ParseForm()
    return render(request, 'parse.html', {'form': form})
