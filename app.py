from config import *
from flask import *
import json
import string
import random

SECRET_KEY = SECRET_KEY
email = 'fitzogbonna@gmail.com'
phone = '+2348032308094'
amount = '5000'

app = Flask(__name__) 

@app.route('/', methods=['POST','GET'])
@app.route('/index', methods=['POST','GET'])
def index():
    return render_template('index.html')
    #return redirect(url_x, code=302)

@app.route('/cart', methods=['POST','GET'])
def cart():
    def data_function(SECRET_KEY=SECRET_KEY,email=email,phone=phone,amount=str(int(amount)*100)):
        rand = ''.join(
            [random.choice(
                string.ascii_letters + string.digits) for n in range(16)])

        RANDOM_REF = rand

        data = {"SECRET_KEY":SECRET_KEY,"RANDOM_REF":RANDOM_REF,"EMAIL":email,"PHONE_NUMBER":phone,"AMOUNT":amount}

        file_path = f'static/data.json'

        with open(file_path, "w+") as fh:
            json.dump(data, fp=fh)

    data_function()
    return render_template('cart.html')

@app.route('/checkout', methods=['POST','GET'])
def checkout():
    return render_template('checkout.html')

@app.route('/confirmation_successful', methods=['POST','GET'])
def payment():
    return render_template('confirmation_successful.html')

@app.route('/static/data.json', methods=['POST','GET'])
def data():
    return app.send_static_file('data.json')

if __name__ == "__main__":
    app.run(debug=True, port=8080)