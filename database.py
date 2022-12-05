import sqlite3

#Open database
conn = sqlite3.connect('database.db')

#Create table
conn.execute('''CREATE TABLE users 
		(userId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		username TEXT,
		created_at TEXT,
		delivery_address TEXT,
		subscription_status TEXT,
		city TEXT,
		state TEXT,
		country TEXT, 
		phone TEXT
		)''')

conn.execute('''CREATE TABLE products
		(productId INTEGER PRIMARY KEY,
		name TEXT,
		price INTEGER,
        compared_price INTEGER,
        vendor TEXT,
        tags TEXT,
		description TEXT,
		image TEXT,
		stock INTEGER,
		categoryId INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
		)''')

conn.execute('''CREATE TABLE kart
		(userId INTEGER,
		productId INTEGER,
        amount INTEGER,
        variants TEXT,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.execute('''CREATE TABLE categories
		(categoryId INTEGER PRIMARY KEY,
		name TEXT,
        image TEXT
		)''')

conn.execute('''CREATE TABLE orders
		(userId INTEGER,
		productId INTEGER,
        amount INTEGER,
        variants TEXT,
        price INTEGER,
        created_at TEXT,
        delivery_date TEXT,
        payment_status TEXT,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.close()

