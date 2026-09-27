import os
import sqlite3

DB_PATH = "meal_planner.db"


def inspect_db():
    if not os.path.exists(DB_PATH):
        print(
            f"Error: No se encuentra el archivo '{DB_PATH}' en el directorio actual."
        )
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener la lista de tablas
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    )
    tables = cursor.fetchall()

    if not tables:
        print("La base de datos no contiene tablas de usuario.")
        conn.close()
        return

    print("=" * 60)
    print(f" BASE DE DATOS: {DB_PATH}")
    print("=" * 60)

    for (table_name,) in tables:
        print(f"\n TABLA: {table_name}")
        print("-" * 60)

        # Obtener nombres de columnas
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        print(f"Columnas: {', '.join(column_names)}")

        # Obtener los registros
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        if rows:
            print(f"Registros ({len(rows)}):")
            for row in rows:
                print(f"  -> {row}")
        else:
            print("  (Tabla vacía)")

    print("\n" + "=" * 60)
    conn.close()


if __name__ == "__main__":
    inspect_db()