from flask import Flask, render_template, jsonify, request, g
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meal_planner.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    ingredients = query_db('SELECT * FROM ingredients ORDER BY name')
    return jsonify([dict(row) for row in ingredients])

@app.route('/api/ingredients', methods=['POST'])
def add_ingredient():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute('INSERT INTO ingredients (name) VALUES (?)', (name,))
        db.commit()
        return jsonify({'id': cursor.lastrowid, 'name': name}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Ingredient already exists'}), 400

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    recipes = query_db('SELECT * FROM recipes ORDER BY name')
    result = []
    for recipe in recipes:
        r = dict(recipe)
        ingredients = query_db('''
            SELECT i.id, i.name, ri.amount
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        ''', (r['id'],))
        r['ingredients'] = [dict(row) for row in ingredients]
        result.append(r)
    return jsonify(result)

@app.route('/api/recipes', methods=['POST'])
def add_recipe():
    data = request.json
    name = data.get('name')
    instructions = data.get('instructions', '')
    ingredients = data.get('ingredients', [])

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute('INSERT INTO recipes (name, instructions) VALUES (?, ?)', (name, instructions))
        recipe_id = cursor.lastrowid

        for ing in ingredients:
            cursor.execute('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (?, ?, ?)',
                           (recipe_id, ing['ingredient_id'], ing.get('amount', '')))

        db.commit()
        return jsonify({'id': recipe_id, 'name': name}), 201
    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({'error': 'Recipe already exists or invalid ingredient'}), 400

@app.route('/api/plan', methods=['GET'])
def get_plan():
    user = request.args.get('user')
    query = '''
        SELECT wp.id, wp.user, wp.day, wp.meal, wp.recipe_id, r.name as recipe_name
        FROM weekly_plan wp
        LEFT JOIN recipes r ON wp.recipe_id = r.id
    '''
    args = ()
    if user:
        query += ' WHERE wp.user = ?'
        args = (user,)

    plan = query_db(query, args)
    return jsonify([dict(row) for row in plan])

@app.route('/api/plan', methods=['POST'])
def update_plan():
    data = request.json
    user = data.get('user')
    day = data.get('day')
    meal = data.get('meal')
    recipe_id = data.get('recipe_id')

    if not all([user, day, meal]):
        return jsonify({'error': 'User, day and meal are required'}), 400

    db = get_db()
    cursor = db.cursor()

    if recipe_id:
        cursor.execute('''
            INSERT INTO weekly_plan (user, day, meal, recipe_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user, day, meal)
            DO UPDATE SET recipe_id=excluded.recipe_id
        ''', (user, day, meal, recipe_id))
    else:
        cursor.execute('DELETE FROM weekly_plan WHERE user=? AND day=? AND meal=?', (user, day, meal))

    db.commit()
    return jsonify({'success': True})

@app.route('/api/shopping_list', methods=['GET'])
def get_shopping_list():
    items = query_db('''
        SELECT sl.id, sl.ingredient_id, i.name as ingredient_name, sl.amount, sl.bought
        FROM shopping_list sl
        JOIN ingredients i ON sl.ingredient_id = i.id
    ''')
    return jsonify([dict(row) for row in items])

@app.route('/api/shopping_list/generate', methods=['POST'])
def generate_shopping_list():
    # Consolidate items from the weekly plan
    db = get_db()
    cursor = db.cursor()

    # clear current list
    cursor.execute('DELETE FROM shopping_list')

    # get all ingredients needed
    ingredients = query_db('''
        SELECT ri.ingredient_id, ri.amount
        FROM weekly_plan wp
        JOIN recipe_ingredients ri ON wp.recipe_id = ri.recipe_id
    ''')

    # a simplistic insertion, could aggregate amounts in a real scenario
    for ing in ingredients:
        cursor.execute('INSERT INTO shopping_list (ingredient_id, amount, bought) VALUES (?, ?, 0)',
                       (ing['ingredient_id'], ing['amount']))
    db.commit()
    return jsonify({'success': True})

@app.route('/api/shopping_list/toggle', methods=['POST'])
def toggle_shopping_item():
    data = request.json
    item_id = data.get('id')
    bought = data.get('bought')

    if item_id is None or bought is None:
        return jsonify({'error': 'ID and bought status required'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE shopping_list SET bought = ? WHERE id = ?', (bought, item_id))
    db.commit()

    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    recipes_count = query_db('SELECT COUNT(*) as c FROM recipes', one=True)['c']
    ingredients_count = query_db('SELECT COUNT(*) as c FROM ingredients', one=True)['c']
    shopping_items_count = query_db('SELECT COUNT(*) as c FROM shopping_list WHERE bought=0', one=True)['c']

    carlos_plan_count = query_db("SELECT COUNT(*) as c FROM weekly_plan WHERE user='Carlos'", one=True)['c']
    almu_plan_count = query_db("SELECT COUNT(*) as c FROM weekly_plan WHERE user='Almu'", one=True)['c']

    return jsonify({
        'recipes': recipes_count,
        'ingredients': ingredients_count,
        'shopping_items': shopping_items_count,
        'carlos_plan': carlos_plan_count,
        'almu_plan': almu_plan_count
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
