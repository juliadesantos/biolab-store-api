import sqlite3

conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS categorias (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS productos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL,
    precio      REAL    NOT NULL,
    stock       INTEGER NOT NULL DEFAULT 0,
    eficiencia  REAL    NOT NULL DEFAULT 1.0,
    categoria_id INTEGER REFERENCES categorias(id)
);

CREATE TABLE IF NOT EXISTS compras (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad    INTEGER NOT NULL DEFAULT 1,
    fecha       TEXT    NOT NULL DEFAULT (datetime('now'))
);
""")

# Datos de ejemplo
cursor.executemany(
    "INSERT INTO categorias (nombre) VALUES (?)",
    [("Reactivos",), ("Medios de cultivo",), ("Equipamiento",)]
)

cursor.executemany(
    "INSERT INTO productos (nombre, precio, stock, eficiencia, categoria_id) VALUES (?,?,?,?,?)",
    [
        ("Agar LB",        12.50, 100, 0.95, 2),
        ("Taq Polimerasa", 89.00,  20, 0.98, 1),
        ("Pipeta 1000 µL", 45.00,  15, 1.00, 3),
        ("Medio M9",       18.00,  60, 0.90, 2),
        ("Buffer PBS",      8.50,  80, 0.97, 1),
    ]
)

conn.commit()
conn.close()
print("Base de datos inicializada correctamente.")
