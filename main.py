from flask import Flask, session, render_template, redirect, url_for, request, flash
import sqlite3
import urllib.parse

app = Flask('app')
app.secret_key = "2eiw3kefn9wej!"

colors = ['#1abc9c', '#8e44ad', '#2c3e50', '#f39c12', '#c0392b', '#2980b9']

# returns list of categories (for navbar)
def getCategories():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    connection.commit()
    connection.close()

    return categories

@app.route('/', methods=['GET'])
def product_index():
    global colors
    categories = getCategories()
    
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    # get products
    args = request.args
    query = args.get('query')
    if query:
        # if search query, limit results
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY name",
            ('%' + query + '%', '%' + query + '%'))
    else:
        # no search query, return} all products
        cursor.execute("SELECT * FROM products ORDER BY name")
    products = cursor.fetchall()
    
    # commit and close database connection
    connection.commit()
    connection.close()
    
    return render_template("products.html",
                           products=products,
                           categories=categories,
                           query=query,
                           colors=colors)

@app.route('/products/<category>', methods=['GET'])
def category_products(category):
    global colors
    categories = getCategories()
    
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    # get category
    cursor.execute("SELECT id, name FROM categories WHERE id=?", (category, ))
    categoryDetails = cursor.fetchone()
    categoryName = categoryDetails['name']
    categoryId = categoryDetails['id']
    
    # get products in category
    args = request.args
    query = args.get('query')
    if query:
        # if search query, limit results
        cursor.execute(
            "SELECT * FROM products INNER JOIN category_products ON products.id = category_products.product_id WHERE category_products.category_id=? AND (products.name LIKE ? OR products.description LIKE ?) ORDER BY name",
            (category, '%' + query + '%', '%' + query + '%'))
    else:
        # no search query, return all products
        cursor.execute(
            "SELECT * FROM products INNER JOIN category_products ON products.id = category_products.product_id WHERE category_products.category_id=? ORDER BY name",
            (category, ))
    products = cursor.fetchall()
    
    # commit and close database connection
    connection.commit()
    connection.close()
    return render_template("products.html",
                           products=products,
                           categories=categories,
                           pageTitle=categoryName,
                           pageId=categoryId,
                           query=query,
                           activeCat=int(category),
                           colors=colors)

@app.route('/product/<id>/add')
def add_to_cart(id):
    # ensure only logged in users can add items to cart
	if 'username' not in session:
		flash("You must be logged in to add an item to your cart.", 'warning')
		return redirect(url_for('login'))

	# Check if cart has been initalized, initialize if not
	if 'cart' not in session:
		session['cart'] = {}

	connection = sqlite3.connect("database.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	# get product
	cursor.execute("SELECT name, stock FROM products WHERE id=?", (id, ))
	product = cursor.fetchone()

	# commit and close database connection
	connection.commit()
	connection.close()

	# Check if item id is valid
	if len(product) == 0:
		# Invalid product, go to product index
		return redirect(url_for('product_index'))

	# Check that stock is >0
	if product['stock'] == 0:
		flash(
		    f"Sorry, {product['name']} is out of stock and cannot be added to your cart.",
		    'warning')
		return redirect(url_for('view_cart'))

	# Check if product already in cart
	if id not in session['cart'].keys():
		# Item not in cart, add it
		session['cart'][id] = 1
	else:
		# Item in cart, increase quantity
		session['cart'][id] += 1

		# Check if new quantity is ≤ stock
		if session['cart'][id] > product['stock']:
			session['cart'][id] = product['stock']
			flash(
			    f"Sorry, we're running low on {product['name']}. We've adjusted the quantity in your cart based on our inventory.",
			    'info')

	# fix for bug where after the first item was added, changes wouldn't persist
	session['cart'] = session['cart']

	return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    global colors
    
    # ensure that only logged in users can view cart
    if 'username' not in session:
        flash("You must be logged in to view your cart.", 'warning')
        return redirect(url_for('login'))
    
    # check for empty cart
    if 'cart' not in session or not session['cart']:
        # Nothing in cart, redirect to home
        flash('Cart empty', 'info')
        return redirect(url_for('product_index'))

    cart = []
    cartTotal = 0
    
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    # get information for each product in cart
    for item in session['cart']:
        cursor.execute(
            "SELECT id, name, price, image_url, stock FROM products WHERE id=?",
            (item, ))
        product = cursor.fetchone()
    
        current = {}
        current['id'] = product['id']
        current['name'] = product['name']
        current['image_url'] = product['image_url']
        current['price'] = product['price']
        current['stock'] = product['stock']
        current['qty'] = session['cart'][item]
        current['total'] = current['qty'] * current['price']
        cartTotal += current['total']
        cart.append(current)
    
    
    # commit and close database connection
    connection.commit()
    connection.close()
    
    categories = getCategories()
    
    return render_template("cart.html",
                           cart=cart,
                           cartTotal=cartTotal,
                           categories=categories,
                           hideNav=True,
                           colors=colors)

@app.route('/cart/empty')
def empty_cart():
    # only logged in users can empty a cart
	if 'username' not in session:
		flash("You must be logged in to empty your cart.", 'warning')
		return redirect(url_for('login'))

	session.pop('cart', None)
	return redirect(url_for('product_index'))

@app.route('/cart/<id>/update', methods=["POST"])
def update_cart(id):
    # only logged in users can update their cart
    if 'username' not in session:
        flash("You must be logged in to update your cart.", 'warning')
        return redirect(url_for('login'))
    
    qty = int(request.form["quantity"])
    if qty == 0:
        session['cart'].pop(id, None)
    else:
        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
    
        # get product
        cursor.execute("SELECT name, stock FROM products WHERE id=?", (id, ))
        product = cursor.fetchone()
    
        # commit and close database connection
        connection.commit()
        connection.close()
    
        # Check if item id is valid
        if len(product) == 0:
            # Invalid product, go to cart
            return redirect(url_for('view_cart'))
    
        # ensures no negative value and no more than available stock
        session['cart'][id] = max(1, qty)
        if session['cart'][id] > product['stock']:
            session['cart'][id] = product['stock']
            flash(
                f"Sorry, we're running low on {product['name']}. We've adjusted the quantity in your cart based on our inventory.",
                'info')
    
    # fix for bug where after the first item was modified, changes wouldn't persist
    session['cart'] = session['cart']
    return redirect(url_for('view_cart'))

@app.route('/cart/<id>/remove')
def cart_remove_item(id):
    # only logged in users can update their cart
	if 'username' not in session:
		flash("You must be logged in to update your cart.", 'warning')
		return redirect(url_for('login'))

	session['cart'].pop(id, None)

	# fix for bug where after the first item was modified, changes wouldn't persist
	session['cart'] = session['cart']
	return redirect(url_for('view_cart'))

@app.route('/cart/checkout')
def checkout():
	# ensure user logged in
	if 'username' not in session:
		flash("You must be logged in to checkout.", 'warning')
		return redirect(url_for('login'))

	# check for empty cart
	if 'cart' not in session or not session['cart']:
		flash('Cart empty', 'info')
		return redirect(url_for('product_index'))

	connection = sqlite3.connect("database.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	# verify availability of every item (if not, adjust and go back to cart)
	productsRemoved = False
	productsUpdated = False
	for pid in session['cart']:
		# ensure quantity is >0
		if session['cart'][pid] <= 0:
            # remove item from cart
			session['cart'].pop(pid, None)
			continue

		# get product
		cursor.execute("SELECT name, stock FROM products WHERE id=?", (pid, ))
		product = cursor.fetchone()

		# Check if item id is valid
		if len(product) == 0:
			# Invalid product, remove item
			session['cart'].pop(pid, None)
			continue

		# Check that stock is >0
		if product['stock'] == 0:
			flash(
			    f"Sorry, {product['name']} is out of stock and has been removed from your cart.",
			    'warning')
			session['cart'].pop(pid, None)
			productsRemoved = True

		# Check if quantity is ≤ stock
		if session['cart'][pid] > product['stock']:
			session['cart'][pid] = product['stock']
			flash(
			    f"Sorry, we're running low on {product['name']}. We've adjusted the quantity in your cart based on our inventory.",
			    'info')
			productsUpdated = True

	session['cart'] = session['cart']
	if productsRemoved or productsUpdated:
		return redirect(url_for('view_cart'))

	# create order
	cursor.execute("INSERT INTO orders (user_id) VALUES (?)",
	               (session['userid'], ))
	orderId = cursor.lastrowid

	# adjust inventory and add to order
	for pid in session['cart']:
		# reduce stock of product
		cursor.execute("SELECT price, stock FROM products WHERE id=?", (pid, ))
		product = cursor.fetchone()
		stock = product['stock']
		stock -= session['cart'][pid]
		cursor.execute("UPDATE products SET stock=? WHERE id=?", (stock, pid))

		# add products to order
		cursor.execute("INSERT INTO order_products VALUES (?, ?, ?, ?)",
		               (orderId, pid, session['cart'][pid], product['price']))

	# commit and close database connection
	connection.commit()
	connection.close()

	# empty cart
	session.pop('cart', None)

	# redirect to order page
	flash("Thank you for your order!", "success")
	return redirect(url_for('view_order', id=orderId))


@app.route('/account', methods=['GET'])
def account():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    categories = getCategories()

    args = request.args
    query = args.get('query')

    sort = args.get('sort')
    if not sort:
        sort = "DESC"
    
    # get orders
    if query:
        print(query)
        if sort == 'ASC':
            cursor.execute("SELECT DISTINCT(orders.id), orders.date_placed FROM orders INNER JOIN order_products ON order_products.order_id = orders.id INNER JOIN products on order_products.product_id = products.id WHERE orders.user_id=? AND products.name LIKE ? ORDER BY date_placed ASC",
               (session['userid'], '%' + query + '%'))
        else:
            cursor.execute("SELECT DISTINCT(orders.id), orders.date_placed FROM orders INNER JOIN order_products ON order_products.order_id = orders.id INNER JOIN products on order_products.product_id = products.id WHERE orders.user_id=? AND products.name LIKE ? ORDER BY date_placed DESC",
               (session['userid'], '%' + query + '%'))
    else:
        if sort == 'ASC':
            cursor.execute("SELECT id, date_placed FROM orders WHERE user_id=? ORDER BY date_placed ASC",
               (session['userid'], ))
        else:
            cursor.execute("SELECT id, date_placed FROM orders WHERE user_id=? ORDER BY date_placed DESC",
               (session['userid'], ))
    
    dbOrders = cursor.fetchall()
    
    orders = []
    for order in dbOrders:
        current = {}
        current['id'] = order['id']
        current['date'] = order['date_placed']
    
        cursor.execute(
            "SELECT SUM(price_per * quantity) AS total FROM order_products WHERE order_id=?",
            (order['id'], ))
        current['total'] = cursor.fetchone()['total']
    
        orders.append(current)
    
    # commit and close database connection
    connection.commit()
    connection.close()
    
    return render_template("account.html",
                           categories=categories,
                           orders=orders)

@app.route('/account/login', methods=['GET', 'POST'])
def login():
	if 'username' in session:
		return redirect(url_for('account'))

	connection = sqlite3.connect("database.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	if request.method == 'POST':
		cursor.execute("SELECT username, fname FROM users")
		user = cursor.fetchall()

		cursor.execute(
		    "SELECT id, username, fname FROM users WHERE username=? AND password=?",
		    (request.form["username"], request.form["password"]))
		user = cursor.fetchone()

		if user:
            # correct credentials, set session variables
			session['username'] = user['username']
			session['userid'] = user['id']
			session['fname'] = user['fname']
			return redirect(url_for('account'))
		else:
			# Login credentials incorrect, flash error message
			flash('Username and/or password incorrect', 'danger')


    # get categories (for nav bar)
	categories = getCategories()

	# commit and close database connection
	connection.commit()
	connection.close()

	return render_template("login.html", categories=categories)


@app.route('/account/signup', methods=['GET', 'POST'])
def signup():
	if 'username' in session:
		return redirect(url_for('account'))

	connection = sqlite3.connect("database.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	if request.method == 'POST':
		# check for existing username
		cursor.execute("SELECT username FROM users WHERE username=?",
		               (request.form["username"], ))
		userExists = cursor.fetchone()
		if userExists:
			flash(
			    "That username is taken. Please use a different username",
			    'danger')
		else:
			cursor.execute(
			    "INSERT INTO users (username, password, fname, lname) VALUES (?, ?, ?, ?)",
			    (request.form["username"], request.form["password"],
			     request.form["fname"], request.form["lname"]))
			cursor.fetchone()

			# ensure we added user correctly and successfully
			cursor.execute(
			    "SELECT id, username, fname FROM users WHERE username=? AND password=?",
			    (request.form["username"], request.form["password"]))
			user = cursor.fetchone()

			if user:
				session['username'] = user['username']
				session['userid'] = user['id']
				session['fname'] = user['fname']
				connection.commit()
				connection.close()
				return redirect(url_for('account'))
			else:
				# Login credentials incorrect, flash error message
				flash('Error creating account. Please try again.', 'danger')

	categories = getCategories()

	# commit and close database connection
	connection.commit()
	connection.close()

	return render_template("signup.html", categories=categories)


@app.route('/account/logout')
def logout():
	# Log the user out (clear session) and redirect them to the login page
	session.clear()
	return redirect(url_for('product_index'))


@app.route('/account/orders/<id>')
def view_order(id):
    global colors
    categories = getCategories()
    
    if 'username' not in session:
        return redirect(url_for('login'))
    
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    # get order
    cursor.execute("SELECT id, date_placed FROM orders WHERE id=?", (id, ))
    order = cursor.fetchone()
    
    # get order total
    cursor.execute(
        "SELECT SUM(price_per * quantity) AS total FROM order_products WHERE order_id=?",
        (id, ))
    total = cursor.fetchone()['total']
    
    # get order products
    cursor.execute(
        "SELECT order_products.quantity, order_products.price_per, products.name, products.image_url FROM order_products INNER JOIN products ON order_products.product_id = products.id WHERE order_id=?",
        (id, ))
    products = cursor.fetchall()
    
    # commit and close database connection
    connection.commit()
    connection.close()
    
    return render_template("order.html",
                           categories=categories,
                           order=order,
                           products=products,
                           total=total,
                           colors=colors)

app.run(host='0.0.0.0', port=8080)
