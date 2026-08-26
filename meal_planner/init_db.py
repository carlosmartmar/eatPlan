import sqlite3
import os

DB_PATH = 'meal_planner.db'

def init_db():
    # Remove existing db if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            instructions TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE recipe_ingredients (
            recipe_id INTEGER,
            ingredient_id INTEGER,
            amount TEXT,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id),
            FOREIGN KEY(ingredient_id) REFERENCES ingredients(id),
            PRIMARY KEY(recipe_id, ingredient_id)
        )
    ''')

    # user: 'Carlos' or 'Almu'
    # meal: 'Desayuno', 'Comida', 'Cena'
    # day: 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'
    cursor.execute('''
        CREATE TABLE weekly_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            day TEXT NOT NULL,
            meal TEXT NOT NULL,
            recipe_id INTEGER,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id),
            UNIQUE(user, day, meal)
        )
    ''')

    cursor.execute('''
        CREATE TABLE shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER,
            amount TEXT,
            bought BOOLEAN DEFAULT 0,
            FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
        )
    ''')

    # Insert mock data
    cursor.executemany('INSERT INTO ingredients (name) VALUES (?)', [
        ('Pollo',), ('Arroz',), ('Huevos',), ('Pan',), ('Leche',), ('Tomate',), ('Pasta',)
    ])

    cursor.executemany('INSERT INTO recipes (name, instructions) VALUES (?, ?)', [
        ('Pollo con Arroz', 'Cocinar el pollo. Hervir el arroz. Mezclar.'),
        ('Huevos fritos con Pan', 'Freír los huevos. Servir con pan.'),
        ('Pasta con Tomate', 'Hervir pasta. Añadir salsa de tomate.')
    ])

    cursor.executemany('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (?, ?, ?)', [
        (1, 1, '200g'), (1, 2, '100g'),
        (2, 3, '2 unidades'), (2, 4, '2 rebanadas'),
        (3, 7, '150g'), (3, 6, '1 lata')
    ])

    # Carlos plan
    cursor.executemany('INSERT INTO weekly_plan (user, day, meal, recipe_id) VALUES (?, ?, ?, ?)', [
        ('Carlos', 'Lunes', 'Desayuno', 2),
        ('Carlos', 'Lunes', 'Comida', 1),
        ('Carlos', 'Lunes', 'Cena', 3),
        ('Carlos', 'Martes', 'Comida', 1)
    ])

    # Almu plan
    cursor.executemany('INSERT INTO weekly_plan (user, day, meal, recipe_id) VALUES (?, ?, ?, ?)', [
        ('Almu', 'Lunes', 'Desayuno', 2),
        ('Almu', 'Lunes', 'Comida', 3),
        ('Almu', 'Lunes', 'Cena', 1)
    ])

    # Populating some mock shopping list items
    cursor.executemany('INSERT INTO shopping_list (ingredient_id, amount, bought) VALUES (?, ?, ?)', [
        (1, '500g', 0),
        (2, '1kg', 0),
        (3, '1 docena', 1)
    ])

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
