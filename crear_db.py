import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inscripciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    curso TEXT NOT NULL,
    turno TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Base de datos institucional creada correctamente")
