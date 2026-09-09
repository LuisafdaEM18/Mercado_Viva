# Mercado VIVA — Devolución de una compra digital en tienda física

MVP que permite a un cliente que compró por el canal digital devolver su producto en una tienda física de Mercado VIVA. El empleado de tienda busca la orden, valida su elegibilidad (plazo de 30 días, estado de la orden, condición del producto) y registra la devolución; el sistema calcula el resultado del reembolso y actualiza el inventario de la tienda en tiempo real.

## Aplicación publicada

| Componente | URL |
|---|---|
| Frontend (Vercel) | https://mercado-viva.vercel.app/ |
| Backend / API (Render) | https://mercado-viva-backend.onrender.com |
| Base de datos | PostgreSQL gestionado en Neon |

> El backend está en el plan gratuito de Render: si nadie lo usa por un rato "se duerme" y la primera petición puede tardar 30-50 segundos en responder. No es un error.

## Cómo usar la aplicación

1. Entra a https://mercado-viva.vercel.app/
2. Elige tu perfil:
   - **Soy empleado de tienda** → panel para buscar una orden y registrar una devolución.
   - **Soy cliente** → portal para consultar el estado de una devolución con su número de seguimiento.

### Flujo del empleado

1. Inicia sesión con las credenciales de prueba (ver tabla abajo).
2. Busca una orden por número de orden o documento del cliente.
3. Si el ítem es elegible, haz clic en "Devolver este ítem".
4. Completa el motivo y la condición del producto (si eliges "Dañado", puedes marcar si fue por mal uso del cliente).
5. Confirma la devolución. El sistema muestra el resultado (aprobado / pendiente / rechazado) y genera un número de seguimiento.
6. Puedes descargar el comprobante de la devolución.

### Flujo del cliente

1. Entra al portal con el número de seguimiento que le dio el empleado.
2. Consulta el estado y el monto de su devolución.

### Datos de prueba

| Dato | Valor |
|---|---|
| Usuario (empleado) | `empleado1` |
| Contraseña | `Clave123` |
| Orden elegible (caso exitoso) | `ORD-1001` |
| Orden fuera de plazo (caso rechazado) | `ORD-1002` |
| Orden fresca | `ORD-1003` |
| Orden fresca (para probar "dañado por mal uso") | `ORD-1004` |

Estas órdenes se crean con `Backend/seed.py`. Una vez que un ítem se devuelve, deja de estar disponible — usa `Backend/reset_demo.py` para reiniciar todas las devoluciones antes de una demo (ver más abajo).

## Arquitectura

- **Frontend**: HTML, CSS y JavaScript sin frameworks, publicado en Vercel.
  - `index.html` — página de entrada (elegir Cliente/Empleado).
  - `panel.html` — panel de devoluciones del empleado.
  - `portal.html` — portal de consulta del cliente.
- **Backend**: API REST en Python (Flask), publicada en Render.
- **Autenticación**: JWT (JSON Web Tokens) para proteger los endpoints del panel de empleado.
- **Base de datos**: PostgreSQL gestionado en Neon.

## Estructura del repositorio

```
Mercado_Viva/
├── Backend/
│   ├── app.py              # Fabrica la aplicacion Flask
│   ├── config.py           # Configuracion (lee variables de entorno)
│   ├── extensions.py       # Instancia de SQLAlchemy
│   ├── models.py           # Modelos de datos
│   ├── business_rules.py   # Reglas de elegibilidad y calculo de reembolso
│   ├── auth.py             # Login y verificacion de JWT
│   ├── inventory.py        # Actualizacion de inventario
│   ├── returns.py          # Endpoints de ordenes y devoluciones
│   ├── seed.py             # Datos de prueba
│   ├── reset_demo.py       # Reinicia las devoluciones para repetir la demo
│   ├── run.py               # Punto de entrada para desarrollo local
│   ├── wsgi.py              # Punto de entrada para produccion (Render)
│   └── tests/               # Pruebas automatizadas (pytest)
└── Frontend/
    ├── index.html, panel.html, portal.html
    ├── css/styles.css
    └── js/config.js, app.js, portal.js
```

## Cómo correr el backend en local

```bash
cd Backend
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y define tus variables (ver tabla abajo). Luego:

```bash
python seed.py       # crea las tablas y los datos de prueba
python -m pytest -v  # corre las 4 pruebas automatizadas
python run.py         # arranca el servidor en http://localhost:5000
```

### Variables de entorno (`Backend/.env`)

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL (Neon). Si se omite, usa SQLite local (`dev.db`) — útil solo para desarrollo rápido, no para producción. |
| `SECRET_KEY` | Clave secreta usada para firmar los tokens JWT. |
| `JWT_EXP_MINUTES` | Minutos de validez del token de sesión del empleado (por defecto 120). |

## Cómo correr el frontend en local

No requiere instalación ni build. Con el backend corriendo:

1. Abre `Frontend/js/config.js` y cambia `API_BASE_URL` a `http://localhost:5000`.
2. Abre `Frontend/index.html` con la extensión **Live Server** de VS Code (clic derecho → "Open with Live Server"). Abrir el archivo con doble clic (`file://`) no funciona por restricciones de seguridad del navegador.

## Pruebas automatizadas

4 pruebas con `pytest` (`Backend/tests/test_returns.py`), usando una base de datos SQLite en memoria independiente de Neon:

1. Registrar una devolución exitosa.
2. Buscar una orden inexistente (404).
3. No permitir devolver el mismo ítem dos veces.
4. Producto dañado por mal uso → estado "pendiente", sin reembolso automático.

## Reiniciar los datos antes de una demo

Como las devoluciones registradas marcan el ítem como "ya devuelto", si vas a repetir la demo (por ejemplo, para el profesor), corre:

```bash
cd Backend
python reset_demo.py
```

Esto borra las devoluciones de prueba y deja todas las órdenes elegibles otra vez, sin afectar las órdenes, productos ni usuarios.


