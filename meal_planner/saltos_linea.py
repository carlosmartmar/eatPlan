import sqlite3

def actualizar_saltos_a_html():
    conn = sqlite3.connect("meal_planner.db")
    cursor = conn.cursor()

    # Reemplaza los saltos de línea (\n) por etiquetas <br>
    cursor.execute("""
        UPDATE recipes 
        SET instructions = REPLACE(instructions, CHAR(10), '<br>')
    """)

    conn.commit()
    conn.close()
    print("¡Instrucciones actualizadas con etiquetas <br>!")

if __name__ == "__main__":
    actualizar_saltos_a_html()