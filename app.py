from flask import Flask, render_template, request
import sys
from hashlib import sha256
import requests
import json

app = Flask(__name__)

shop_id = 5
secret_key = "SecretKey01"
pay_way = "advcash_rub"
shop_order_id = 4126
values_currency = {"EUR": 978, "USD": 840, "RUB": 643}


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    amount = request.form['num']
    get_text_area = request.form['text_area']
    currency = request.form['select_value']

    if currency == "EUR":
        data = pay_method(amount, get_text_area, values_currency['EUR'])
        return render_template('EUR.html', data=data)
    elif currency == "USD":
        # отлавливать моменты когда api возвращат ошибку
        data = bill_method(amount, get_text_area, values_currency['USD'], values_currency['RUB'])['data']
        return render_template('USD.html', data=data)


def bill_method(amount, text, payer_currency, shop_currency):
    str_for_sha256 = f"{payer_currency}:{amount}:{shop_currency}:{shop_id}:{shop_order_id}{secret_key}"

    _hash = sha256(str_for_sha256.encode('utf-8')).hexdigest()

    info = {"description": text, "payer_currency": payer_currency, "shop_amount": amount,
            "shop_currency": shop_currency, "shop_id": shop_id,
            "shop_order_id": shop_order_id, "sign": _hash}

    headers = {"Content-Type": "application/json"}
    info = json.dumps(info)

    response = requests.post('https://core.piastrix.com/bill/create', info, headers=headers)

    return response.json()


def pay_method(amount, text, currency):
    str_for_sha256 = f"{amount}:{currency}:{shop_id}:{shop_order_id}{secret_key}"

    _hash = sha256(str_for_sha256.encode('utf-8')).hexdigest()

    data = {"amount": amount, "currency": currency, "shop_id": shop_id,
            "shop_order_id": shop_order_id, "sign": _hash, "description": text}

    return data


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
