from decimal import Decimal
from io import BytesIO

import requests
from PIL import Image
from bs4 import BeautifulSoup
from django.shortcuts import render

from clickhouse_driver import Client

from products.forms import ParseForm


def parse_emoji(emoji):
    emoji_u = emoji.decode('UTF-8').rsplit('0')[-1]
    response = requests.get(f'https://symbl.cc/ru/{emoji_u}/')
    soup = BeautifulSoup(response.content, features="html.parser")
    link = soup.find_all('img')[0]['src']
    return link


def products_parse(request):
    count_empty_attrs = 0
    count_symbol_in_attr = 0
    count_imgs_in_attr = 0
    emoji = '\U0001F923'
    split_line = None

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
                "SELECT * FROM product_attr AS pa "
                f"WHERE pa.product_id='{product_id}'")

            products_attrs_dicts = [
                {
                    'attr_id': attr[0],
                    'name': attr[1],
                    'value': attr[2],
                    'required ': attr[3],
                    'category_id': attr[4],
                }
                for attr in products_attrs]
            count_attrs = len(products_attrs_dicts)

            for attr in products_attrs_dicts:
                if attr['name'] == 'NULL' or len(attr['name']) == 0 or attr['name'] is None:
                    count_empty_attrs += 1
                count_symbol_in_attr = (len(attr['value']))

                if attr['name'] == 'images':
                    count_imgs_in_attr = len(attr['name'])
                    if attr['value'] is not None and attr['value'] != 'NULL':
                        for img_url in attr['value'].split(', '):
                            emoji_url = parse_emoji(emoji.encode('unicode_escape'))
                            with Image.open(BytesIO(requests.get(emoji_url).content)) as emoji_img:
                                with Image.open(img_url) as image:
                                    image.paste(emoji_img, (300, 300))
                                    image.save(img_url)

                for line in attr['value'].split('\n'):
                    if line[:5] == '   ' and line[5] != ' ' and line[5:] != '\n':
                        split_line = line
                        break
                if split_line is not None:
                    split_text = attr['value'].split(split_line, 1)
                    print(split_text[0])
                    attr['value'] = split_text[0] + emoji + '\n' + split_line + split_text[1]
            empty_attrs = str(Decimal(count_empty_attrs / count_attrs * 100).quantize(Decimal('1.00'))) + ' %'

            print(count_attrs)
            print(empty_attrs)
            print(count_symbol_in_attr)
            print(count_imgs_in_attr)

            client.execute('INSERT INTO category_attrs (attribute_id, attribute_name, description, required, dictionary_value,'
                           'data_type, value, category_id) VALUES', products_attrs_dicts)

    else:
        form = ParseForm()
    return render(request, 'parse.html', {'form': form})
