from flask import Flask, render_template, request, redirect
import sys
from hashlib import sha256
import requests
import json
import time
import os

application = Flask(__name__)

shop_id = 5
secret_key = "SecretKey01"
pay_way = "advcash_rub"
shop_order_id = 4126
values_currency = {"EUR": 978, "USD": 840, "RUB": 643}

time_start = time.strftime("%d.%m.%y_%H.%M")


@application.route('/')
def index():
    return render_template("index.html")


@application.route('/submit', methods=['GET', 'POST'])
def submit():
    amount = request.form['num']
    get_text_area = request.form['text_area']
    currency = request.form['select_value']

    if currency == "EUR":
        data = pay_method(amount, get_text_area, values_currency[currency], currency)
        return render_template('pay_method.html', data=data)

    elif currency == "USD":
        data = bill_method(amount, get_text_area, values_currency[currency], values_currency['RUB'], currency)

        if data['data'] is None:
            return render_template('error.html', data=data)
        else:
            return redirect(data['data']['url'])

    else:
        data = invoice_method(amount, values_currency[currency], get_text_area, currency)

        if data['data'] is None:
            return render_template('error.html', data=data)
        else:
            return render_template("invoice_method.html", data=data)


def invoice_method(amount, currency, text, v_currency):
    str_for_sha256 = f"{amount}:{currency}:{pay_way}:{shop_id}:{shop_order_id}{secret_key}"

    _hash = sha256(str_for_sha256.encode('utf-8')).hexdigest()

    info = {"currency": currency, "sign": _hash, "payway": pay_way, "amount": amount,
            "shop_id": shop_id, "shop_order_id": shop_order_id, "description": text}

    headers = {"Content-Type": "application/json"}
    info = json.dumps(info)

    response = requests.post('https://core.piastrix.com/invoice/create', info, headers=headers)
    response = response.json()

    if response['data'] is None:
        write_log_file(f'Error: {response["message"]}, {amount} {v_currency}, desc = {text}')
    else:
        write_log_file(f'{amount} {v_currency}, id = {response["data"]["id"]}, desc = {text}')

    return response


def bill_method(amount, text, payer_currency, shop_currency, v_currency):
    str_for_sha256 = f"{payer_currency}:{amount}:{shop_currency}:{shop_id}:{shop_order_id}{secret_key}"

    _hash = sha256(str_for_sha256.encode('utf-8')).hexdigest()

    info = {"description": text, "payer_currency": payer_currency, "shop_amount": amount,
            "shop_currency": shop_currency, "shop_id": shop_id,
            "shop_order_id": shop_order_id, "sign": _hash}

    headers = {"Content-Type": "application/json"}
    info = json.dumps(info)

    response = requests.post('https://core.piastrix.com/bill/create', info, headers=headers)
    response = response.json()

    if response['data'] is None:
        write_log_file(f'Error: {response["message"]}, {amount} {v_currency}, desc = {text}')
    else:
        write_log_file(f'{amount} {v_currency}, id = {response["data"]["id"]}, desc = {text}')

    return response


def pay_method(amount, text, currency, v_currency):
    str_for_sha256 = f"{amount}:{currency}:{shop_id}:{shop_order_id}{secret_key}"

    _hash = sha256(str_for_sha256.encode('utf-8')).hexdigest()

    data = {"amount": amount, "currency": currency, "shop_id": shop_id,
            "shop_order_id": shop_order_id, "sign": _hash, "description": text}

    write_log_file(f'{amount} {v_currency}, desc = {text}')

    return data


def write_log_file(event):
    if os.path.exists("log"):
        pass
    else:
        os.mkdir("log")

    with open(f"log/{time_start}_log.txt", "a") as file:
        log_info = str(time.strftime("[%x %X] ")) + str(event) + "\n"
        file.write(log_info)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        application.run(host=arg_host, port=arg_port)
    else:
        application.run()
