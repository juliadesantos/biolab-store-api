# BioLab Store 🧬

Sistema de e-commerce de insumos de laboratorio biológico con API REST e interfaz web. Desarrollado en Python con Flask y SQLite.

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3 · Flask · Flask-CORS |
| Base de datos | SQLite (3 tablas relacionadas) |
| SQL | JOINs, GROUP BY, transacciones atómicas, claves foráneas |
| Frontend | HTML · CSS · JavaScript vanilla |
| Modelo biológico | Ecuación de crecimiento logístico |

---

## Estructura del proyecto

```
biolab_store/
├── app.py           — API REST (endpoints, lógica de negocio)
├── init_db.py       — crea las tablas y carga datos de ejemplo
├── database.db      — base de datos SQLite (generada al correr init_db.py)
├── templates/
│   └── index.html   — interfaz web
└── README.md
```

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
git clone https://github.com/juliadesantos/biolab-store-api
cd biolab_store
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
python3 init_db.py
python3 app.py
```

Abrí `localhost:5000` en el navegador.

---

## Interfaz web

La app tiene tres secciones accesibles desde `localhost:5000`:

- **Productos** — tabla con nombre, categoría, precio, stock y eficiencia de cada insumo
- **Ranking** — productos más vendidos, calculados con `GROUP BY` y `COUNT`
- **Simulación** — ingresás un producto, tiempo y población inicial, y el modelo logístico calcula el crecimiento microbiano con visualización de curva

---

## Endpoints

### Productos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/productos` | Lista todos los productos con categoría (JOIN) |
| GET | `/productos/top` | Ranking por ventas (GROUP BY + COUNT) |
| POST | `/producto` | Agrega un producto |

**POST `/producto` — body:**
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
| POST | `/comprar` | Registra compra y descuenta stock |
| GET | `/compras` | Historial de compras |

**POST `/comprar` — body:**
```json
{
  "producto_id": 1,
  "cantidad": 3
}
```

### Simulación biológica

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/simular` | Modelo de crecimiento logístico |

**Ejemplo:** `localhost:5000/simular?id=1&tiempo=48&poblacion=100`

**Respuesta:**
```json
{
  "producto": "Agar LB",
  "eficiencia": 0.95,
  "tiempo_h": 48.0,
  "poblacion_inicial": 100,
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
- **Transacciones atómicas** — en `/comprar`, la verificación de stock y el descuento ocurren en la misma transacción para evitar condiciones de carrera.
- **Validación de entrada** — todos los endpoints verifican campos requeridos y devuelven errores con el código HTTP correcto (400, 404, 409).
- **Modelo logístico** — la simulación usa `N(t) = K / (1 + ((K−N₀)/N₀)·e^(−r·t))` donde la eficiencia del producto afecta directamente la tasa de crecimiento `r`.
- **CORS habilitado** — permite que el frontend se comunique con la API desde el navegador.
