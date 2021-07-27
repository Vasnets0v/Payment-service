from flask import Flask, render_template, redirect, request
import sys
from hashlib import sha256

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
    elif currency == "USD":
        data = bill_method()

    return render_template('submit.html', data=data)


def bill_method():
    pass


def pay_method(amount, text, currency):
    str_for_sha256 = str(amount) + ":" + str(currency) + ":" + \
                     str(shop_id) + ":" + str(shop_order_id) + str(secret_key)

    hash = sha256(str_for_sha256.encode('utf-8')).hexdigest()

    data = {"amount": amount, "currency": currency, "shop_id": shop_id,
            "shop_order_id": shop_order_id, "sign": hash, "description": text}

    return data


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()