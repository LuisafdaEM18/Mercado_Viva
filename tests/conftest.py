import pytest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db as _db
from models import Usuario, Producto, Orden, OrdenItem, InventarioTienda


@pytest.fixture
def app():
    application = create_app(
        config_overrides={
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True,
            "SECRET_KEY": "test-secret",
        }
    )

    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def token(app, client):
    with app.app_context():
        _db.session.add(
            Usuario(
                username="empleado1",
                password_hash=generate_password_hash("Clave123"),
                nombre="Empleado Test",
            )
        )
        _db.session.commit()

    resp = client.post("/api/auth/login", json={"username": "empleado1", "password": "Clave123"})
    return resp.get_json()["token"]


@pytest.fixture
def orden_elegible(app):
    with app.app_context():
        producto = Producto(sku="SKU-TEST", nombre="Producto Test", precio=50000)
        _db.session.add(producto)
        _db.session.flush()

        _db.session.add(InventarioTienda(producto_id=producto.id, stock=2))

        orden = Orden(
            numero_orden="ORD-TEST-1",
            cliente_documento="111",
            cliente_nombre="Cliente Test",
            fecha_compra=datetime.utcnow() - timedelta(days=3),
            estado="entregada",
        )
        _db.session.add(orden)
        _db.session.flush()

        item = OrdenItem(orden_id=orden.id, producto_id=producto.id, precio_unitario=50000)
        _db.session.add(item)
        _db.session.commit()

        return {"orden_item_id": item.id, "producto_id": producto.id}
