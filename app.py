import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = "yelp_clone.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            restaurant_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        );

        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        );
    """)
    db.commit()
    db.close()


# --- Routes ---

@app.route("/")
def index():
    db = get_db()
    restaurants = db.execute("""
        SELECT restaurants.*, ROUND(AVG(reviews.rating), 1) AS avg_rating,
               COUNT(reviews.id) AS review_count
        FROM restaurants
        LEFT JOIN reviews ON restaurants.id = reviews.restaurant_id
        GROUP BY restaurants.id
        ORDER BY restaurants.name
    """).fetchall()
    return render_template("index.html", restaurants=restaurants)


# --- Restaurants ---

@app.route("/restaurants/new", methods=["GET", "POST"])
def new_restaurant():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO restaurants (name, address, cuisine) VALUES (?, ?, ?)",
            (request.form["name"], request.form["address"], request.form["cuisine"]),
        )
        db.commit()
        return redirect(url_for("index"))
    return render_template("restaurant_form.html")


@app.route("/restaurants/<int:id>")
def show_restaurant(id):
    db = get_db()
    restaurant = db.execute("SELECT * FROM restaurants WHERE id = ?", (id,)).fetchone()
    reviews = db.execute("""
        SELECT reviews.*, users.name AS user_name
        FROM reviews JOIN users ON reviews.user_id = users.id
        WHERE reviews.restaurant_id = ?
        ORDER BY reviews.created_at DESC
    """, (id,)).fetchall()
    menu_items = db.execute(
        "SELECT * FROM menu_items WHERE restaurant_id = ? ORDER BY name", (id,)
    ).fetchall()
    users = db.execute("SELECT * FROM users ORDER BY name").fetchall()
    return render_template(
        "restaurant.html",
        restaurant=restaurant, reviews=reviews,
        menu_items=menu_items, users=users,
    )


# --- Users ---

@app.route("/users")
def list_users():
    db = get_db()
    users = db.execute("""
        SELECT users.*, COUNT(reviews.id) AS review_count
        FROM users LEFT JOIN reviews ON users.id = reviews.user_id
        GROUP BY users.id ORDER BY users.name
    """).fetchall()
    return render_template("users.html", users=users)


@app.route("/users/new", methods=["GET", "POST"])
def new_user():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (request.form["name"], request.form["email"]),
        )
        db.commit()
        return redirect(url_for("list_users"))
    return render_template("user_form.html")


# --- Reviews ---

@app.route("/restaurants/<int:restaurant_id>/reviews", methods=["POST"])
def add_review(restaurant_id):
    db = get_db()
    db.execute(
        "INSERT INTO reviews (user_id, restaurant_id, rating, comment) VALUES (?, ?, ?, ?)",
        (
            request.form["user_id"],
            restaurant_id,
            request.form["rating"],
            request.form["comment"],
        ),
    )
    db.commit()
    return redirect(url_for("show_restaurant", id=restaurant_id))


# --- Menu Items ---

@app.route("/restaurants/<int:restaurant_id>/menu", methods=["POST"])
def add_menu_item(restaurant_id):
    db = get_db()
    db.execute(
        "INSERT INTO menu_items (restaurant_id, name, description, price) VALUES (?, ?, ?, ?)",
        (
            restaurant_id,
            request.form["name"],
            request.form["description"],
            request.form["price"],
        ),
    )
    db.commit()
    return redirect(url_for("show_restaurant", id=restaurant_id))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
