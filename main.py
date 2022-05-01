import sqlite3, random
from flask import Flask, session, render_template, redirect, url_for, request

app = Flask('app')
app.secret_key = "password123"
productImages = 'static/images'
app.config['images'] = productImages

### This function gets basic info about the logged in user by checking the session ###
def loginInfo():
  connection = sqlite3.connect("myDatabase.db")
  connection.row_factory = sqlite3.Row
  cursor = connection.cursor()

  if 'uname' not in session:
    loggedIn = False
    fname = ''
    numItems = 0
  else:
    loggedIn = True
    cursor.execute("SELECT custid, fname FROM customer WHERE username ='" + session['uname'] + "'");
    custId, fname = cursor.fetchone()
    cursor.execute("SELECT COUNT(prodid) FROM cart WHERE custid =" + str(custId));
    numItems = cursor.fetchone()[0]

  return (loggedIn, fname, numItems)

### Function that checks if user logged is logged in or not, and directing the user to the appropiate page ###
@app.route('/loginForm')
def loginForm():
  if 'uname' in session:
    return redirect(url_for('home'))
  else:
    return render_template('login.html')

### Function that 'pop's the session when user logs out ###
@app.route('/logout')
def logout():
  session.pop('uname', None)
  return redirect(url_for('home'))

### Function for collecting products of a specific category based on the attribute 'catid' ###
@app.route("/category")
def category():
  loggedIn, firstName, numItems = loginInfo()
  categoryId = request.args.get("categoryId")
  connection = sqlite3.connect("myDatabase.db")
  connection.row_factory = sqlite3.Row
  cursor = connection.cursor()
  
  cursor.execute("SELECT product.prodid, product.name, product.price, product.image, category.name FROM product, category WHERE product.catid = category.catid AND category.catid = " + categoryId)
  data = cursor.fetchall()
  connection.close()
  categoryName = data[0][4]
  data = location(data)
  return render_template('category.html', data=data, loggedIn=loggedIn, firstName=firstName, numItems=numItems, categoryName=categoryName)

### Function that displays more information about a specific product and gives the option to add to cart ###
@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, numItems = loginInfo()
    productId = request.args.get('productId')
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
  
    cursor.execute('SELECT prodid, name, price, image, quantity FROM product WHERE prodid = ' + productId)
    productData = cursor.fetchone()
    connection.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, numItems = numItems)

### Function that validates login credentials with database ###
def validLogin(username, password):
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute('SELECT username, password FROM customer')
    data = cursor.fetchall()
    for i in data:
      if i[0] == username and i[1] == password:
        return True
    return False
  
### Function that displays the home page and collects all items in the 'product' table ###
@app.route('/', methods=['GET', 'POST'])
def home():
  loggedIn, firstName, numItems = loginInfo()
  connection = sqlite3.connect("myDatabase.db")
  connection.row_factory = sqlite3.Row
  cursor = connection.cursor()
  
  cursor.execute('SELECT * FROM product')
  productData = cursor.fetchall()
  productData = location(productData)
  cursor.execute('SELECT * FROM category')
  categoryData = cursor.fetchall()
  
  connection.close()
  return render_template('home.html', loggedIn = loggedIn, fname = firstName, numItems = numItems, categoryData = categoryData, productData = productData)

### Function that logs a user in by setting a session with the user's username. It also checks if credentials are correct by calling function 'validLogin' with the username and password passed in ###
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    uname = request.form["uname"]
    password = request.form["pass"]
    print(uname, password)

    if validLogin(uname, password):
      session['uname'] = uname
      #session['cart'] = 0
      return redirect(url_for('home'))
    else:
      errmsg = 'Invalid username/password, please try again'
      return render_template('login.html', msg = errmsg)

### Function that enables a user to register and enter new data into the table 'customer' ###
@app.route('/register', methods=['GET', 'POST'])
def register():
  connection = sqlite3.connect("myDatabase.db")
  connection.row_factory = sqlite3.Row
  cursor = connection.cursor()
  
  if request.method == 'POST':
    uname = request.form["uname"]
    password = request.form["pass"]
    password2 = request.form["pass2"]
    firstName = request.form["fname"]
    lastName = request.form["lname"]
    print(uname, password, firstName, lastName)

    if password != password2:
      errmsg = "Please re-enter password"
      return render_template('register.html', errmsg = errmsg)
    else:
      newCustid = random.randint(10000, 19999)
      
      try:
        cursor.execute("INSERT INTO customer (custid, username, password, fname, lname) VALUES (?,?,?,?,?)",(newCustid, uname, password, firstName, lastName))
        connection.commit()
        print('New registered customer!')
        msg = 'Registered Succesfully'
        return render_template('login.html', msg = msg)
      except:
        connection.rollback()
        print("error occured")
    connection.close()
    return render_template('register.html')
  return render_template('register.html')

### Function that enables a user to search for a specific product ###
@app.route("/search", methods=['GET', 'POST'])
def search():
  loggedIn, firstName, numItems = loginInfo()
  if request.method == 'POST':
    searchData = request.form["searchData"]
    print(searchData)

  connection = sqlite3.connect("myDatabase.db")
  connection.row_factory = sqlite3.Row
  cursor = connection.cursor()

  cursor.execute('SELECT prodid, name, price, image FROM product WHERE name LIKE ? ', ( '%'+searchData+'%',))
  product = cursor.fetchall()
  connection.close()
  return render_template("search.html", product = product, loggedIn = loggedIn, fname = firstName, numItems = numItems)

### Function that displays the cart which includes all products added to cart ###
@app.route("/cart")
def cart():
  if 'uname' not in session:
    return redirect(url_for('loginForm'))
    
  loggedIn, firstName, numItems = loginInfo()
  uname = session['uname']

  connection = sqlite3.connect("myDatabase.db")
  connection.row_factory = sqlite3.Row
  cursor = connection.cursor()
  cursor.execute("SELECT custid FROM customer WHERE username = '" + uname + "'")
  custid = cursor.fetchone()[0]
  
  cursor.execute("SELECT product.prodid, product.name, product.price, product.image FROM product, cart WHERE product.prodid = cart.prodid AND cart.custid = " + str(custid))
  products = cursor.fetchall()
  try:
    cursor.execute("SELECT specificid FROM cart WHERE custid = " + str(custid))
    specificId = cursor.fetchone()[0]
  except:
    connection.rollback()
    specificId = 000000
    
  totalPrice = 0
  connection.close()
  for row in products:
    totalPrice += row[2]
  return render_template("cart.html", products = products, specificId = specificId, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, numItems=numItems)

### Function that adds products to the cart by collecting data about the product and passing the data to the 'cart' table ###
@app.route("/addToCart")
def addToCart():
  # print("Got here!1")
  if 'uname' not in session:
      return redirect(url_for('loginForm'))
  else:
    # print("Got here!2")
    productId = int(request.args.get('prodid'))
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    cursor.execute("SELECT custid FROM customer WHERE username = '" + session['uname'] + "'")
    userId = cursor.fetchone()[0]
    newSpecificId = random.randint(100000, 199999)
    try:
      cursor.execute("INSERT INTO cart (custid, prodid, specificid) VALUES (\"{0}\", \"{1}\", \"{2}\");" .format(userId, productId, newSpecificId))
      connection.commit()
      print('product added!')
    except:
      connection.rollback()
      print("error occured")
    connection.close()
    return redirect(url_for('home'))

### Function that removes products from the cart by deleting the product from the 'cart' table ###
@app.route("/removeFromCart")
def removeFromCart():
    if 'uname' not in session:
        return redirect(url_for('loginForm'))
    uname = session['uname']
    specificId = int(request.args.get('specificId'))
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT custid FROM customer WHERE username = '" + uname + "'")
    custid = cursor.fetchone()[0]
    try:
      cursor.execute("DELETE FROM cart WHERE custid = " + str(custid) + " AND specificid = " + str(specificId))
      connection.commit()
      msg1 = "Item Has Been Removed"
      print(msg1)
    except:
      connection.rollback()
      msg2 = "Error occured"
      print(msg2)
    connection.close()
    return redirect(url_for('cart'))

### Function that decreases the quantity of the products that a user checks out with ###
@app.route("/checkout", methods=['GET','POST'])
def checkOut():
    if 'uname' not in session:
        return redirect(url_for('loginForm'))
      
    loggedIn, firstName, numItems = loginInfo()
    uname = session['uname']

    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    cursor.execute("SELECT custid FROM customer WHERE username = '" + uname + "'")
    custid = cursor.fetchone()[0]
  
    cursor.execute("SELECT product.prodid, product.name, product.price, product.image FROM product, cart WHERE product.prodid = cart.prodid AND cart.custid = " + str(custid))
    products = cursor.fetchall()

    cursor.execute("SELECT specificid FROM cart WHERE custid = " + str(custid))
    specificItem = cursor.fetchone()[0]

    cursor.execute("SELECT prodid FROM cart WHERE specificid = "+ str(specificItem))
    prodIdOfSpecProd = cursor.fetchone()[0]
  
    try:
      cursor.execute("UPDATE product SET quantity = quantity - 1 WHERE prodid = " + str(prodIdOfSpecProd))
    
      connection.commit()
      print("Product quantity decreased!")
    except:
      connection.rollback()
      print("Error occured")
      
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
        #print(row)
    connection.commit()
    return render_template("checkout.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, numItems=numItems)

def location(data):
    loc = []
    i = 0
    while i < len(data):
        cur = []
        for j in range(5):
            if i >= len(data):
                break
            cur.append(data[i])
            i += 1
        loc.append(cur)
    return loc

app.run(host='0.0.0.0', port=8080)
