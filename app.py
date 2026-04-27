from flask import Flask, request, jsonify
import sqlite3
import math
import random

app = Flask(__name__)


# ── helpers ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row   # devuelve dicts, no tuplas
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def require_fields(data, *fields):
    missing = [f for f in fields if f not in data]
    if missing:
        return {"error": f"Faltan campos: {', '.join(missing)}"}, 400
    return None


# ── productos ─────────────────────────────────────────────────────────────────

@app.route("/productos")
def productos():
    """Lista todos los productos con su categoría (JOIN)."""
    conn = get_db()
    rows = conn.execute("""
        SELECT p.id, p.nombre, p.precio, p.stock, p.eficiencia,
               c.nombre AS categoria
        FROM   productos p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        ORDER  BY p.nombre
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/productos/top")
def productos_top():
    """Ranking de productos más vendidos usando GROUP BY + COUNT (SQL avanzado)."""
    conn = get_db()
    rows = conn.execute("""
        SELECT p.nombre,
               c.nombre        AS categoria,
               COUNT(co.id)    AS ventas_totales,
               SUM(co.cantidad) AS unidades_vendidas
        FROM   productos p
        JOIN   categorias c  ON c.id = p.categoria_id
        LEFT JOIN compras co ON co.producto_id = p.id
        GROUP  BY p.id
        ORDER  BY ventas_totales DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/producto", methods=["POST"])
def agregar_producto():
    """Agrega un producto validando campos requeridos."""
    data = request.get_json(silent=True) or {}
    err = require_fields(data, "nombre", "precio", "stock", "eficiencia", "categoria_id")
    if err:
        return jsonify(err[0]), err[1]

    try:
        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO productos (nombre, precio, stock, eficiencia, categoria_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (data["nombre"], float(data["precio"]),
             int(data["stock"]), float(data["eficiencia"]),
             int(data["categoria_id"]))
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()
        return jsonify({"mensaje": "Producto agregado", "id": nuevo_id}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400


# ── compras ───────────────────────────────────────────────────────────────────

@app.route("/comprar", methods=["POST"])
def comprar():
    """Registra una compra y actualiza el stock en una transacción atómica."""
    data = request.get_json(silent=True) or {}
    err = require_fields(data, "producto_id")
    if err:
        return jsonify(err[0]), err[1]

    cantidad = int(data.get("cantidad", 1))
    if cantidad < 1:
        return jsonify({"error": "La cantidad debe ser al menos 1"}), 400

    try:
        conn = get_db()
        row = conn.execute(
            "SELECT id, nombre, stock FROM productos WHERE id = ?",
            (data["producto_id"],)
        ).fetchone()

        if not row:
            return jsonify({"error": "Producto no encontrado"}), 404

        if row["stock"] < cantidad:
            return jsonify({
                "error": "Stock insuficiente",
                "stock_disponible": row["stock"]
            }), 409

        conn.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?",
            (cantidad, row["id"])
        )
        conn.execute(
            "INSERT INTO compras (producto_id, cantidad) VALUES (?, ?)",
            (row["id"], cantidad)
        )
        conn.commit()
        conn.close()
        return jsonify({
            "mensaje": f"Compra realizada: {cantidad}x {row['nombre']}",
            "stock_restante": row["stock"] - cantidad
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/compras")
def historial_compras():
    """Historial de compras con JOIN a productos."""
    conn = get_db()
    rows = conn.execute("""
        SELECT co.id, p.nombre AS producto, co.cantidad, co.fecha
        FROM   compras co
        JOIN   productos p ON p.id = co.producto_id
        ORDER  BY co.fecha DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ── simulación biológica ──────────────────────────────────────────────────────

@app.route("/simular")
def simular():
    """
    Simulación de crecimiento logístico.
    Modela cómo una población microbiana crece con el producto seleccionado.

    Parámetros:
      id        – id del producto
      tiempo    – horas de incubación (default 24)
      poblacion – tamaño inicial de la muestra (default 100)
    """
    producto_id = request.args.get("id")
    if not producto_id:
        return jsonify({"error": "Se requiere el parámetro 'id'"}), 400

    try:
        tiempo    = float(request.args.get("tiempo", 24))
        poblacion = float(request.args.get("poblacion", 100))
    except ValueError:
        return jsonify({"error": "Los parámetros numéricos son inválidos"}), 400

    conn = get_db()
    row = conn.execute(
        "SELECT nombre, eficiencia FROM productos WHERE id = ?",
        (producto_id,)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Producto no encontrado"}), 404

    # Modelo logístico: N(t) = K / (1 + ((K-N0)/N0) * e^(-r*t))
    K   = 1_000_000          # capacidad de carga
    r   = row["eficiencia"] * random.uniform(0.18, 0.22)  # tasa de crecimiento
    N0  = poblacion

    N_final = K / (1 + ((K - N0) / N0) * math.exp(-r * tiempo))

    return jsonify({
        "producto":         row["nombre"],
        "eficiencia":       row["eficiencia"],
        "tiempo_h":         tiempo,
        "poblacion_inicial": int(N0),
        "poblacion_final":  int(N_final),
        "modelo":           "logístico"
    })


# ── categorias ────────────────────────────────────────────────────────────────

@app.route("/categorias")
def categorias():
    conn = get_db()
    rows = conn.execute("SELECT * FROM categorias ORDER BY nombre").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
