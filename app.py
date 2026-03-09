from flask import Flask, render_template, request, redirect, session
import sqlite3
app = Flask(__name__)
app.secret_key = "secretkey567"
def init_db():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products(
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            size TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()
init_db()
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        size = request.form["size"]
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, size) VALUES (?, ?, ?)",
            (name, price, size)
        )
        conn.commit()
        conn.close()
        return redirect("/view")
    return render_template("index.html")
@app.route("/view")
def view():
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, price, size FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template("view.html", products=products)
@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit(product_id):
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        size = request.form["size"]
        cursor.execute(
            "UPDATE products SET name=?, price=?, size=? WHERE product_id=?",
            (name, price, size, product_id)
        )
        conn.commit()
        conn.close()
        return redirect("/view")
    cursor.execute(
        "SELECT product_id, name, price, size FROM products WHERE product_id=?",
        (product_id,)
    )
    product = cursor.fetchone()
    conn.close()
    return render_template("edit.html", product=product)
@app.route("/delete/<int:product_id>")
def delete(product_id):
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id=?", (product_id,))
    conn.commit()
    conn.close()
    return redirect("/view")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except:
            return "Username already exists!"
        conn.close()
        return redirect("/login")
    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid credentials"
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")
if __name__ == "__main__":
    app.run(debug=True)