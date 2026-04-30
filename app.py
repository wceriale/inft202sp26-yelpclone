import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE_URL = "postgresql://postgres.zhuidpxcrytshhsktygq:T6htZotVGYCwIBi6@aws-1-us-west-2.pooler.supabase.com:6543/postgres"


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL)
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# def init_db():
#     conn = psycopg2.connect(DATABASE_URL)
#     cur = conn.cursor()
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS "user" (
#             id SERIAL PRIMARY KEY,
#             name TEXT NOT NULL,
#             email TEXT NOT NULL UNIQUE,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );

#         CREATE TABLE IF NOT EXISTS restaurant (
#             id SERIAL PRIMARY KEY,
#             name TEXT NOT NULL,
#             address TEXT NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );

#         CREATE TABLE IF NOT EXISTS review (
#             id SERIAL PRIMARY KEY,
#             user_id INTEGER NOT NULL REFERENCES "user"(id),
#             restaurant_id INTEGER NOT NULL REFERENCES restaurant(id),
#             rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
#             comment TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );

#         CREATE TABLE IF NOT EXISTS menu_item (
#             id SERIAL PRIMARY KEY,
#             restaurant_id INTEGER NOT NULL REFERENCES restaurant(id),
#             name TEXT NOT NULL,
#             description TEXT,
#             price REAL NOT NULL
#         );
#     """)
#     # Drop the cuisine column if it still exists
#     cur.execute("""
#         ALTER TABLE restaurant DROP COLUMN IF EXISTS cuisine;
#     """)
#     conn.commit()
#     cur.close()
#     conn.close()


# --- Routes ---

@app.route("/")
def index():
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT restaurant.*, ROUND(AVG(review.rating), 1) AS avg_rating,
               COUNT(review.id) AS review_count
        FROM restaurant
        LEFT JOIN review ON restaurant.id = review.restaurant_id
        GROUP BY restaurant.id
        ORDER BY restaurant.name
    """)
    restaurants = cur.fetchall()
    cur.close()
    return render_template("index.html", restaurants=restaurants)


# --- Restaurants ---

@app.route("/restaurants/new", methods=["GET", "POST"])
def new_restaurant():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO restaurant (name, address) VALUES (%s, %s)",
            (request.form["name"], request.form["address"]),
        )
        db.commit()
        cur.close()
        return redirect(url_for("index"))
    return render_template("restaurant_form.html")


@app.route("/restaurants/<int:id>")
def show_restaurant(id):
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT * FROM restaurant WHERE id = %s", (id,))
    restaurant = cur.fetchone()

    cur.execute("""
        SELECT review.*, "user".name AS user_name
        FROM review JOIN "user" ON review.user_id = "user".id
        WHERE review.restaurant_id = %s
        ORDER BY review.created_at DESC
    """, (id,))
    reviews = cur.fetchall()

    cur.execute(
        "SELECT * FROM menu_item WHERE restaurant_id = %s ORDER BY name", (id,)
    )
    menu_items = cur.fetchall()

    cur.execute("SELECT * FROM \"user\" ORDER BY name")
    users = cur.fetchall()

    cur.close()
    return render_template(
        "restaurant.html",
        restaurant=restaurant, reviews=reviews,
        menu_items=menu_items, users=users,
    )


# --- Users ---

@app.route("/users")
def list_users():
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT "user".*, COUNT(review.id) AS review_count
        FROM "user" LEFT JOIN review ON "user".id = review.user_id
        GROUP BY "user".id ORDER BY "user".name
    """)
    users = cur.fetchall()
    cur.close()
    return render_template("users.html", users=users)


@app.route("/users/new", methods=["GET", "POST"])
def new_user():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO \"user\" (name, email) VALUES (%s, %s)",
            (request.form["name"], request.form["email"]),
        )
        db.commit()
        cur.close()
        return redirect(url_for("list_users"))
    return render_template("user_form.html")


# --- Reviews ---

@app.route("/restaurants/<int:restaurant_id>/reviews", methods=["POST"])
def add_review(restaurant_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO review (user_id, restaurant_id, rating, comment) VALUES (%s, %s, %s, %s)",
        (
            request.form["user_id"],
            restaurant_id,
            request.form["rating"],
            request.form["comment"],
        ),
    )
    db.commit()
    cur.close()
    return redirect(url_for("show_restaurant", id=restaurant_id))


# --- Menu Items ---

@app.route("/restaurants/<int:restaurant_id>/menu", methods=["POST"])
def add_menu_item(restaurant_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO menu_item (restaurant_id, name, description, price) VALUES (%s, %s, %s, %s)",
        (
            restaurant_id,
            request.form["name"],
            request.form["description"],
            request.form["price"],
        ),
    )
    db.commit()
    cur.close()
    return redirect(url_for("show_restaurant", id=restaurant_id))


if __name__ == "__main__":
    # init_db()
    app.run(debug=True)
