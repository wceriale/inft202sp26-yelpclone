"""Seed the database with sample restaurants, users, reviews, and menu items."""

import psycopg2
import random

DATABASE_URL = "postgresql://postgres.zhuidpxcrytshhsktygq:T6htZotVGYCwIBi6@aws-1-us-west-2.pooler.supabase.com:6543/postgres"

# ── Restaurants near Bryant Park, NYC ─────────────────────────────────────────

restaurants = [
    ("Bryant Park Grill", "25 W 40th St, New York, NY 10018"),
    ("Keens Steakhouse", "72 W 36th St, New York, NY 10018"),
    ("La Pecora Bianca", "20 W 40th St, New York, NY 10018"),
    ("The Kati Roll Company", "49 W 39th St, New York, NY 10018"),
    ("Ai Fiori", "400 Fifth Ave, New York, NY 10018"),
]

# ── 20 Users ──────────────────────────────────────────────────────────────────

users = [
    ("Marcus Chen", "marcus.chen@email.com"),
    ("Olivia Brooks", "olivia.brooks@email.com"),
    ("Jamal Washington", "jamal.washington@email.com"),
    ("Sofia Ramirez", "sofia.ramirez@email.com"),
    ("Ethan Nakamura", "ethan.nakamura@email.com"),
    ("Priya Patel", "priya.patel@email.com"),
    ("Liam O'Sullivan", "liam.osullivan@email.com"),
    ("Aisha Johnson", "aisha.johnson@email.com"),
    ("Derek Kim", "derek.kim@email.com"),
    ("Natalie Winters", "natalie.winters@email.com"),
    ("Carlos Mendez", "carlos.mendez@email.com"),
    ("Hannah Bergström", "hannah.bergstrom@email.com"),
    ("Tyrone Mitchell", "tyrone.mitchell@email.com"),
    ("Elena Volkov", "elena.volkov@email.com"),
    ("Ryan Fitzgerald", "ryan.fitzgerald@email.com"),
    ("Mei-Lin Zhang", "meilin.zhang@email.com"),
    ("Isaac Torres", "isaac.torres@email.com"),
    ("Grace Okafor", "grace.okafor@email.com"),
    ("Noah Petersen", "noah.petersen@email.com"),
    ("Zara Hussain", "zara.hussain@email.com"),
]

# ── Menu items per restaurant ─────────────────────────────────────────────────

menu_items = {
    "Bryant Park Grill": [
        ("Burrata", "Fresh burrata with heirloom tomatoes and basil", 13.50),
        ("Jumbo Lump Crab Cake", "Pan-seared crab cake with mixed green salad", 39.50),
        ("Fried Calamari", "Lightly fried with marinara dipping sauce", 13.50),
        ("Steak Frites", "Grilled hanger steak with french fries", 39.50),
        ("Lemon Chicken", "Roasted half chicken with lemon herb jus", 26.00),
        ("Grilled Filet Mignon", "8 oz Angus filet with red wine reduction", 41.00),
        ("Miso Sea Bass", "Organic miso-crusted Spanish sea bass", 32.00),
        ("Maine Lobster Roll", "Chilled lobster on a toasted brioche bun", 29.00),
    ],
    "Keens Steakhouse": [
        ("Mutton Chop", "Legendary 26 oz saddle of lamb", 62.00),
        ("Prime Porterhouse", "USDA Prime dry-aged porterhouse for two", 129.00),
        ("Filet Mignon", "USDA Prime center-cut filet, 10 oz", 59.00),
        ("Creamed Spinach", "Classic steakhouse-style creamed spinach", 8.50),
        ("Sautéed Wild Mushrooms", "Seasonal wild mushroom medley", 12.00),
        ("New York Cheesecake", "Classic New York-style cheesecake", 8.00),
        ("Crème Brûlée", "Vanilla bean custard with caramelized sugar", 7.50),
        ("Caesar Salad", "Tableside-prepared Caesar with white anchovies", 18.00),
    ],
    "La Pecora Bianca": [
        ("Rigatoni Vodka", "House-made rigatoni with spicy tomato cream", 24.00),
        ("Tagliatelle Bolognese", "Fresh tagliatelle with slow-cooked meat ragù", 26.00),
        ("Bucatini Cacio e Pepe", "Pecorino romano and black pepper", 22.00),
        ("Garganelli al Ragù", "Hand-rolled pasta with wild boar ragù", 25.00),
        ("Zucchini Fries", "Lightly battered with lemon aioli", 14.00),
        ("Roasted Eggplant", "With whipped ricotta and tomato jam", 16.00),
        ("Margherita Pizza", "San Marzano tomato, mozzarella, basil", 18.00),
        ("Olive Oil Cake", "With mascarpone cream and seasonal berries", 14.00),
    ],
    "The Kati Roll Company": [
        ("Chicken Tikka Roll", "Chicken marinated in yogurt & spices, grilled", 8.90),
        ("Achari Paneer Roll", "Indian cheese in spicy pickle marinade", 8.90),
        ("Aloo Masala Roll", "Mashed potato with tomatoes & green peppers", 7.10),
        ("Seekh Kebab Roll", "Minced lamb and lentil croquette", 9.20),
        ("Beef Kati Roll", "Cubed beef marinated with yogurt & spices", 9.20),
        ("Anda Roll", "Flatbread layered with freshly beaten egg", 6.50),
        ("Chickpea Roll", "Chickpeas with fenugreek & blackening spices", 8.30),
        ("Chicken Tikka Anda Roll", "Egg-layered flatbread with chicken tikka", 10.70),
    ],
    "Ai Fiori": [
        ("Swordfish Brochettes", "Grilled swordfish with Riviera vegetables", 48.00),
        ("Chicken Roulade", "Stuffed chicken breast with herb jus", 42.00),
        ("Fiori Burger", "Dry-aged beef blend with gruyère and truffle aioli", 40.00),
        ("Half Dozen Oysters", "East Coast oysters with mignonette", 28.00),
        ("Signature Pasta", "Rotating seasonal handmade pasta", 32.00),
        ("Fresh Verdure", "Market vegetables with lemon vinaigrette", 18.00),
        ("Branzino", "Mediterranean sea bass with olive tapenade", 46.00),
        ("Tiramisu", "Classic Italian dessert with espresso and mascarpone", 16.00),
    ],
}

# ── Review comments pool ─────────────────────────────────────────────────────

positive_comments = [
    "Absolutely loved this place! Will definitely be back.",
    "The food was incredible and the service was top-notch.",
    "Great atmosphere, perfect for a night out in the city.",
    "One of the best meals I've had in Midtown.",
    "Amazing flavors, every dish was a hit.",
    "Such a gem near Bryant Park. Highly recommend!",
    "The staff was so friendly and attentive.",
    "Exceeded my expectations in every way.",
    "Perfect spot for lunch during a work break.",
    "Fantastic food and a wonderful ambiance.",
    "A must-visit if you're in the area.",
    "Really solid menu with great options for everyone.",
    "Came here for a birthday dinner and it was perfect.",
    "The portions are generous and everything tastes fresh.",
    "I've been here three times now and it never disappoints.",
    "Consistently great quality. This is my go-to spot.",
    "Delicious food at reasonable prices for Midtown.",
    "Love the vibe here, feels cozy yet upscale.",
    "My friend recommended this place and I'm so glad they did.",
    "Everything on the menu is worth trying.",
]

okay_comments = [
    "Pretty good overall, though nothing mind-blowing.",
    "Decent food but the wait was a bit long.",
    "Solid choice for the area, but I've had better.",
    "Good food, average service. Would still come back.",
    "It was fine for a quick meal. Nothing to complain about.",
    "The food was okay. Some dishes were better than others.",
    "Nice location but the prices are a bit steep for what you get.",
    "A reliable option near Bryant Park.",
    "Not bad at all, just not exceptional.",
    "Good enough for a weekday lunch.",
]


def seed():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Clear existing data
    cur.execute("DELETE FROM review")
    cur.execute("DELETE FROM menu_item")
    cur.execute('DELETE FROM "user"')
    cur.execute("DELETE FROM restaurant")

    # Insert restaurants
    for name, address in restaurants:
        cur.execute(
            "INSERT INTO restaurant (name, address) VALUES (%s, %s)",
            (name, address),
        )
    cur.execute("SELECT id, name FROM restaurant ORDER BY id")
    restaurant_ids = {name: rid for rid, name in cur.fetchall()}

    # Insert users
    for name, email in users:
        cur.execute(
            'INSERT INTO "user" (name, email) VALUES (%s, %s)', (name, email)
        )
    cur.execute('SELECT id FROM "user" ORDER BY id')
    user_ids = [row[0] for row in cur.fetchall()]

    # Insert menu items
    for rest_name, items in menu_items.items():
        rid = restaurant_ids[rest_name]
        for item_name, desc, price in items:
            cur.execute(
                "INSERT INTO menu_item (restaurant_id, name, description, price) VALUES (%s, %s, %s, %s)",
                (rid, item_name, desc, price),
            )

    # Insert reviews: ~4 per user (80 total across 5 restaurants)
    random.seed(42)
    for uid in user_ids:
        reviewed_restaurants = random.sample(list(restaurant_ids.values()), 4)
        for rid in reviewed_restaurants:
            rating = random.choice([3, 3, 4, 4, 4, 4, 5, 5, 5, 5])
            if rating >= 4:
                comment = random.choice(positive_comments)
            else:
                comment = random.choice(okay_comments)
            cur.execute(
                "INSERT INTO review (user_id, restaurant_id, rating, comment) VALUES (%s, %s, %s, %s)",
                (uid, rid, rating, comment),
            )

    conn.commit()

    # Print summary
    print("Seeded successfully!")
    cur.execute("SELECT COUNT(*) FROM restaurant")
    print(f"  Restaurants: {cur.fetchone()[0]}")
    cur.execute('SELECT COUNT(*) FROM "user"')
    print(f"  Users:       {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM review")
    print(f"  Reviews:     {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM menu_item")
    print(f"  Menu Items:  {cur.fetchone()[0]}")

    # Show avg ratings
    print("\nAverage Ratings:")
    cur.execute("""
        SELECT r.name, ROUND(AVG(rev.rating), 1) AS avg, COUNT(rev.id) AS cnt
        FROM restaurant r LEFT JOIN review rev ON r.id = rev.restaurant_id
        GROUP BY r.id ORDER BY avg DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}/5 ({row[2]} reviews)")

    cur.close()
    conn.close()


if __name__ == "__main__":
    seed()
