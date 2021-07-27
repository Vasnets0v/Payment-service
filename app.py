from flask import Flask, render_template, redirect, request
import sys

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    get_num = request.form['num']
    get_text_area = request.form['text_area']
    get_value = request.form['select_value']
    print(get_num, get_text_area, get_value)
    return redirect('/')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()