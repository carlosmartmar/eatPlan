import sqlite3

def get_or_create_ingredient(cursor, name):
    name_clean = name.strip()
    cursor.execute("SELECT id FROM ingredients WHERE LOWER(name) = LOWER(?)", (name_clean,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO ingredients (name) VALUES (?)", (name_clean,))
    return cursor.lastrowid

def insert_recipes():
    conn = sqlite3.connect("meal_planner.db")
    cursor = conn.cursor()

    recipes_data = [
        {
            "name": "Merluza a la plancha con tomate, queso fresco y aceitunas",
            "instructions": (
                "1. Asar en la plancha caliente el filete de merluza limpio de espinas.\n"
                "2. Emplatar la merluza asada con la ensalada de tomate con queso fresco y aceitunas aliñada con aceite de oliva."
            ),
            "ingredients": [
                ("Filete de merluza", "150g"),
                ("Aceite de oliva", "5g"),
                ("Tomate crudo", "90g"),
                ("Queso tipo Burgos natural", "50g"),
                ("Aceituna verde", "20g")
            ]
        },
        {
            "name": "Macarrones con salteado de salmón ahumado y cebolla",
            "instructions": (
                "1. Cocer los macarrones en abundante agua con sal durante 12 minutos. Escurrir y reservar.\n"
                "2. Poner a pochar la cebolla picada fina, cuando se empiece a dorar agregar el salmón ahumado cortado en tiras, añadir pimienta molida y mezclar bien para que se integren todos los sabores.\n"
                "3. Agregar los macarrones al salteado y mezclar todo el conjunto."
            ),
            "ingredients": [
                ("Macarrones", "100g"),
                ("Cebolla o cebolleta", "100g"),
                ("Aceite de oliva", "10g"),
                ("Pimienta negra", "2g"),
                ("Salmón ahumado", "80g")
            ]
        },
        {
            "name": "Espaguetis con pesto de pistachos",
            "instructions": (
                "1. Cocer los espaguetis en abundante agua con sal durante 10 minutos. Escurrir y reservar.\n"
                "2. Preparar el pesto, majando en un mortero los pistachos pelados junto con el ajo troceado, la albahaca fresca y el queso parmesano, ir añadiendo poco a poco la cantidad sugerida de aceite hasta que ligue la salsa.\n"
                "3. Emplatar los espaguetis con la salsa pesto por encima."
            ),
            "ingredients": [
                ("Espagueti", "100g"),
                ("Pistacho con cáscara", "15g"),
                ("Ajo", "10g"),
                ("Albahaca", "10g"),
                ("Queso parmesano", "25g"),
                ("Aceite de oliva", "10g")
            ]
        },
        {
            "name": "Guiso de patatas con guisantes y bonito",
            "instructions": (
                "1. Sofreír en una cazuela la cebolla, el ajo y el pimiento picados.\n"
                "2. Pelar y cortar la patata en trozos gruesos. Añadir a la cazuela junto con el perejil picado, rehogar todo junto.\n"
                "3. Cubrir de agua y cocer durante 20 minutos.\n"
                "4. Cuando la patata esté cocida, apagar el fuego y agregar los guisantes y el bonito en conserva escurrido.\n"
                "5. Dejar reposar unos minutos antes de servir."
            ),
            "ingredients": [
                ("Aceite de oliva", "8g"),
                ("Ajo", "5g"),
                ("Cebolla o cebolleta", "100g"),
                ("Patata", "340g"),
                ("Perejil", "5g"),
                ("Guisante, arveja fresco", "140g"),
                ("Bonito en aceite", "85g"),
                ("Pimiento verde", "100g")
            ]
        },
        {
            "name": "Ensalada de arroz con aceitunas y huevo duro",
            "instructions": (
                "1. Cocer el arroz en un cazo con el doble de agua, durante 15 minutos. Dejar reposar otros 5 minutos con el fuego apagado.\n"
                "2. Poner al fuego un cazo con agua, cuando empiece a hervir meter el huevo y cocer durante 10 minutos.\n"
                "3. Lavar y picar en trozos pequeños el pimiento, el tomate, la cebolla, el pepino y el ajo. Reservar.\n"
                "4. Picar los filetes de anchoa y las aceitunas. Reservar.\n"
                "5. Batir el aceite y el vinagre hasta que emulsione.\n"
                "6. Mezclar las hortalizas troceadas con el arroz, incorporar el aliño y mezclar bien.\n"
                "7. Emplatar la mezcla y añadir las anchoas troceadas, las aceitunas y el huevo cocido cortado en cuartos."
            ),
            "ingredients": [
                ("Arroz blanco crudo", "70g"),
                ("Huevo de gallina", "60g"),
                ("Aceite de oliva", "8g"),
                ("Ajo", "3g"),
                ("Cebolla o cebolleta", "30g"),
                ("Pepino", "30g"),
                ("Pimiento rojo", "30g"),
                ("Tomate crudo", "30g"),
                ("Aceituna negra", "16g"),
                ("Anchoas en aceite", "12g"),
                ("Vinagre", "7g")
            ]
        },
        {
            "name": "Espaguetis a la carbonara de queso crema y jamón cocido",
            "instructions": (
                "1. Cocer los espaguetis en abundante agua con sal durante 10 minutos. Escurrir y reservar.\n"
                "2. Batir las yemas de huevo y agregar el queso crema indicado. Mezclar bien para que se integre el huevo con el queso hasta obtener una salsa fina.\n"
                "3. Dorar en una sartén el jamón cocido cortado pequeños dados, incorporar los espaguetis y la salsa y mezclar sin dejar de mover.\n"
                "4. Servir inmediatamente."
            ),
            "ingredients": [
                ("Queso de untar ligero", "45g"),
                ("Yema de huevo", "20g"),
                ("Aceite de oliva", "8g"),
                ("Jamón cocido", "40g"),
                ("Espagueti", "80g")
            ]
        }
    ]

    for recipe in recipes_data:
        cursor.execute(
            "INSERT INTO recipes (name, instructions) VALUES (?, ?)",
            (recipe["name"], recipe["instructions"])
        )
        recipe_id = cursor.lastrowid
        print(f"Insertada receta ID {recipe_id}: {recipe['name']}")

        for ing_name, amount in recipe["ingredients"]:
            ing_id = get_or_create_ingredient(cursor, ing_name)
            cursor.execute(
                "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (?, ?, ?)",
                (recipe_id, ing_id, amount)
            )

    conn.commit()
    conn.close()
    print("¡Todas las recetas e ingredientes se han insertado correctamente!")

if __name__ == "__main__":
    insert_recipes()