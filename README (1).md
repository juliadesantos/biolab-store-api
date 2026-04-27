# BioLab Store API 🧬

API REST backend para un e-commerce de insumos de laboratorio biológico.
Construida con **Flask** y **SQLite**, incluye simulación de crecimiento microbiano basada en el modelo logístico.

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3 · Flask |
| Base de datos | SQLite (3 tablas relacionadas) |
| SQL avanzado | JOINs, GROUP BY, subconsultas, transacciones |
| Modelo biológico | Crecimiento logístico (ecuación diferencial) |

---

## Estructura de la base de datos

```
categorias          productos              compras
──────────          ─────────────────      ───────────────
id (PK)      ◄──── categoria_id (FK)      id (PK)
nombre              id (PK)          ◄──── producto_id (FK)
                    nombre                 cantidad
                    precio                 fecha
                    stock
                    eficiencia
```

---

## Instalación

```bash
git clone <tu-repo>
cd biolab_store
python3 -m venv venv
source venv/bin/activate
pip install flask
python3 init_db.py
python3 app.py
```

---

## Endpoints

### Productos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/productos` | Lista todos los productos con categoría (JOIN) |
| POST | `/producto` | Agrega un producto (valida campos requeridos) |
| GET | `/productos/top` | Ranking por ventas (GROUP BY + COUNT) |

**POST `/producto` — body esperado:**
```json
{
  "nombre": "Agar MacConkey",
  "precio": 15.00,
  "stock": 50,
  "eficiencia": 0.93,
  "categoria_id": 2
}
```

### Compras

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/comprar` | Registra compra y descuenta stock (transacción atómica) |
| GET | `/compras` | Historial de compras |

**POST `/comprar` — body esperado:**
```json
{
  "producto_id": 1,
  "cantidad": 3
}
```

### Simulación biológica

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/simular?id=1&tiempo=48&poblacion=200` | Modelo de crecimiento logístico |

**Respuesta ejemplo:**
```json
{
  "producto": "Agar LB",
  "eficiencia": 0.95,
  "tiempo_h": 48.0,
  "poblacion_inicial": 200,
  "poblacion_final": 987342,
  "modelo": "logístico"
}
```

### Categorías

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/categorias` | Lista todas las categorías |

---

## Decisiones técnicas

- **`row_factory = sqlite3.Row`** — las respuestas JSON son objetos nombrados, no arrays posicionales.
- **Transacciones atómicas en `/comprar`** — la verificación de stock y el descuento ocurren en la misma transacción para evitar condiciones de carrera.
- **Validación de entrada** — todos los endpoints con body verifican campos requeridos y devuelven errores descriptivos con el código HTTP correcto.
- **Modelo logístico** — la simulación usa la ecuación `N(t) = K / (1 + ((K-N₀)/N₀)·e^(-r·t))` en lugar de un random simple, mostrando cómo la eficiencia del producto afecta la tasa de crecimiento `r`.
