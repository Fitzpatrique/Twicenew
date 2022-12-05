from config import *
from flask import *
from flask_cors import CORS
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
from chat import get_response
import json
import string
import random
import datetime
from datetime import timedelta

SECRET_KEY = SECRET_KEY


app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png', 'gif']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
admin_email = 'rickogbonna@gmail.com'

def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            username = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, username FROM users WHERE email = '" + session['email'] + "'")
            userId, username = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = " + str(userId))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, username, noOfItems)

@app.route('/', methods=['POST','GET'])
@app.route('/index', methods=['POST','GET'])
def index():
    loggedIn, username, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, compared_price, vendor, tags, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('index.html', itemData=itemData, loggedIn=loggedIn, username=username, noOfItems=noOfItems, categoryData=categoryData)

@app.route("/<string:category_name>/<string:categoryId>")
def displayCategory(category_name,categoryId):
        loggedIn, username, noOfItems = getLoginDetails()
        categoryId = categoryId
        category_name = category_name

        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = " + str(categoryId))
            data = cur.fetchall()
        conn.close()
        # data = parse(data)
        return render_template('display_category.html', data=data, loggedIn=loggedIn, username=username, noOfItems=noOfItems, category_name = category_name)


@app.route("/admin/categories")
def adminCategory():
        loggedIn, username, noOfItems = getLoginDetails()
        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT categoryId, name, image FROM categories ORDER BY name ASC")
                data = cur.fetchall()
            conn.close()
            data = parse(data)
            return render_template('admin_category.html', data=data, loggedIn=loggedIn, username=username, noOfItems=noOfItems)
        except:
            return render_template('404.html')

@app.route("/admin/orders")
def adminOrder():
        loggedIn, username, noOfItems = getLoginDetails()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
            data = cur.fetchall()
        conn.close()
        data = parse(data)
        return render_template('admin_orders.html', data=data, loggedIn=loggedIn, username=username, noOfItems=noOfItems)
 
@app.route("/admin/products")
def adminProduct():
        loggedIn, username, noOfItems = getLoginDetails()
        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute('SELECT productId, name, price, compared_price, vendor, tags, description, image, stock, categoryId FROM products ORDER BY name ASC')
                itemData = cur.fetchall()
                cur = conn.cursor()
                cur.execute("SELECT categoryId, name FROM categories ORDER BY name DESC")
                data = cur.fetchall()
            conn.close()
            #data = parse(data)
            return render_template('admin_products.html', itemData=itemData, data=data, loggedIn=loggedIn, username=username, noOfItems=noOfItems)
        except:
            return render_template('404.html', loggedIn=loggedIn, username=username, noOfItems=noOfItems)


@app.route("/admin/<string:admin_code>/add")
def add(admin_code):
    admin_code = admin_code
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)


@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = int(request.form['price'])
        compared_price = int(request.form['compared_price'])
        description = request.form['description']
        vendor = request.form['vendor']
        tags = request.form['tags']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure    
        image = request.files['image']
        uploaded_file_extension = image.filename.split(".")[1]
        if (uploaded_file_extension.lower() in ALLOWED_EXTENSIONS):
            destination_path = f"static/upload/{image.filename}"

            image.save(destination_path)

        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('INSERT INTO products (name, price, compared_price, vendor, tags, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (name, price, compared_price, vendor, tags, description, image.filename, stock, categoryId))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('adminProduct'))

@app.route("/addCategory", methods = ["GET", "POST"])
def addCategoryr():
    if request.method == "POST":
        #Parse form data    
        name = request.form['name']
        image = request.files['image']
        uploaded_file_extension = image.filename.split(".")[1]
        if (uploaded_file_extension.lower() in ALLOWED_EXTENSIONS):
            destination_path = f"static/upload/{image.filename}"

            image.save(destination_path)

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO categories (name, image) VALUES (?,?)', (name, image.filename))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        print(msg)
        #print(name)
        return redirect(url_for('adminCategory'))







@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ' + productId)
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('adminProduct'))

@app.route("/removeCategory")
def removeCategory():
    categoryId = request.args.get('categoryId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM categories WHERE categoryID = ' + categoryId)
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('adminCategory'))

@app.route("/admin/login", methods = ['POST','GET'])
def adminlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password) and email == admin_email:
            session['email'] = email
            return redirect(url_for('admin'))
        elif is_valid(email, password) and email != admin_email:
            error = 'This user does not have administrative permission'
            return render_template('admin_login.html', error=error)
        else:
            error = 'Invalid UserId / Password'
            return render_template('admin_login.html', error=error)

@app.route("/admin/portal")
def adminForm():
    return render_template("admin_login.html")


@app.route("/admin")
def admin():
    if ('email' not in session) or (session['email'] != admin_email):
        return redirect(url_for('index'))
    loggedIn, username, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, compared_price, vendor, tags, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
        cur.execute('SELECT userId, productId, amount, variants, price, created_at, delivery_date, payment_status FROM orders')
        orderData = cur.fetchall()
    itemData = parse(itemData)
    return render_template("admin_home.html", loggedIn=loggedIn, username=username, noOfItems=noOfItems, itemData=itemData, categoryData=categoryData, orderData=orderData)

@app.route("/account/profile/edit")
def editHome():
    if 'email' not in session:
        return redirect(url_for('index'))
    loggedIn, username, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, username, delivery_address, subscription_status, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("edit_profile.html", loggedIn=loggedIn, username=username, noOfItems=noOfItems, profileData=profileData)

@app.route("/account/profile/view")
def viewProfile():
    if 'email' not in session:
        return redirect(url_for('index'))
    loggedIn, username, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, username, delivery_address, subscription_status, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("customers_profile.html", profileData=profileData, loggedIn=loggedIn, username=username, noOfItems=noOfItems, email=email, admin_email=admin_email)

@app.route("/account/orders")
def viewOrder():
    if 'email' not in session:
        return redirect(url_for('index'))
    loggedIn, username, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT users.userId, products.productId, users.username, products.name, orders.amount, orders.variants, orders.created_at, orders.delivery_date, orders.payment_status FROM orders, users, products WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("customer_orders.html", profileData=profileData, loggedIn=loggedIn, username=username, noOfItems=noOfItems)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('sign_in'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = '" + session['email'] + "'")
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("change_password.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("change_password.html", msg=msg)
    else:
        return render_template("change_password.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        delivery_address = request.form['delivery_address']
        subscription_status = request.form['subscription_status']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET username = ?,  delivery_address = ?, subscription_status = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?', (username, delivery_address, subscription_status, city, state, country, phone, email))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('editProfile'))

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('index'))
    else:
        return render_template('sign_in.html', error='')

@app.errorhandler(404)
def page_not_found(e):
    loggedIn, username, noOfItems = getLoginDetails()
    return render_template('404.html',loggedIn=loggedIn, username=username, noOfItems=noOfItems), 404
 
 
 
@app.errorhandler(500)
def internal_server_error(e):
    loggedIn, username, noOfItems = getLoginDetails()
    return render_template('500.html',loggedIn=loggedIn, username=username, noOfItems=noOfItems)


@app.route("/products/<string:category_name>/<string:product_name>/<string:productId>")
def productDescription(category_name,product_name,productId):
    loggedIn, username, noOfItems = getLoginDetails()
    productId = str(productId)
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, compared_price, vendor, tags, description, image, stock FROM products WHERE productId = ' + productId)
        productData = cur.fetchone()
    conn.close()

    return render_template("product.html", data=productData, loggedIn = loggedIn, username = username, noOfItems = noOfItems)

    
    

@app.route("/addToCart", methods=["POST"])
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        if request.method == "POST":
            productId = int(request.form['productId'])
            amount = int(request.form['amount'])
            variants = request.form['size'] + ', ' + request.form['color']

            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
                userId = cur.fetchone()[0]
                try:
                    cur.execute("INSERT INTO kart (userId, productId, amount,variants) VALUES (?, ?, ?, ?)", (userId, productId, amount, variants))
                    conn.commit()
                    msg = "Added successfully"
                except:
                    conn.rollback()
                    msg = "Error occured"
            conn.close()
            return redirect(url_for('index'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))

    loggedIn, username, noOfItems = getLoginDetails()
    email = session['email']

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, phone FROM users WHERE email = '" + email + "'")
        data = cur.fetchone()
        userId = data[0]
        phone = data[1]
        cur.execute("SELECT products.productId, products.name, products.price, kart.amount, kart.variants, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall() 
    totalPrice = 0
    for row in products:
        totalPrice = totalPrice + (row[2]*row[3])

    def data_function(SECRET_KEY=SECRET_KEY,email=email,phone=phone,amount=str(int(totalPrice)*100)):
        rand = ''.join(
            [random.choice(
                string.ascii_letters + string.digits) for n in range(16)])

        RANDOM_REF = rand

        data = {"SECRET_KEY":SECRET_KEY,"RANDOM_REF":RANDOM_REF,"EMAIL":email,"PHONE_NUMBER":phone,"AMOUNT":amount}

        file_path = f'static/data.json'

        with open(file_path, "w+") as fh:
            json.dump(data, fp=fh)

    data_function()
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, username=username, noOfItems=noOfItems)



@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM kart WHERE userId = " + str(userId) + " AND productId = " + str(productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route('/checkout', methods=['POST','GET'])
def checkout():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, username, noOfItems = getLoginDetails()
    email = session['email']
    try:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, phone FROM users WHERE email = '" + email + "'")
            data = cur.fetchone()
            userId = data[0]
            phone = data[1]
            cur.execute("SELECT products.productId, products.name, products.price, kart.amount, kart.variants, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
            products = cur.fetchall()
        totalPrice = 0
        for row in products:
            totalPrice = totalPrice + (row[2]*row[3])
        return render_template('checkout.html', products = products, totalPrice=totalPrice, loggedIn=loggedIn, username=username, noOfItems=noOfItems)
    except:
        return redirect(url_for('index'))

@app.route('/static/data.json', methods=['POST','GET'])
def data():
    return app.send_static_file('data.json')

@app.route('/confirmation_successful', methods=['POST','GET'])
def payment():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, username, noOfItems = getLoginDetails()
    email = session['email']

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        data = cur.fetchone()
        userId = data[0]
        cur.execute("SELECT products.productId, products.name, products.price, kart.amount, kart.variants, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = cur.fetchall()
    totalPrice = 0
    payment_status = 'False'
    created_at = datetime.date.today()
    for row in products:
        totalPrice = totalPrice + (row[2]*row[3])
        print(row)
        cur.execute("INSERT INTO orders (userId, productId, amount, variants, price, created_at,delivery_date,payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (userId, row[0], row[3], row[4],totalPrice, str(created_at),str(created_at + timedelta(days=7)),payment_status))
    cur.execute("DELETE FROM kart WHERE userId = " + str(userId))
    conn.commit()
    return render_template("confirmation_successful.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, username=username, noOfItems=noOfItems)

@app.route('/delete/order', methods=['GET','POST'])
def deleteOrder():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, username, noOfItems = getLoginDetails()
    email = session['email']

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM orders " )
        conn.commit()
    return redirect(url_for('admin'))

@app.route('/predict', methods=['POST'])
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer":response}
    return jsonify(message)

@app.route("/login", methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('index'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('sign_in.html', error=error)

@app.route("/register", methods = [ 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        username = request.form['username']
        delivery_address = request.form['delivery_address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        created_at = datetime.date.today()

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, username, created_at, delivery_address,  city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, username, str(created_at), delivery_address, city, state, country, phone))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("sign_in.html", error=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("sign_in.html")

@app.route("/add/category")
def categoryForm():
    return render_template("add_category.html")


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == "__main__":
    app.secret_key = PUBLIC_KEY

    app.run(debug=True, port=5000)