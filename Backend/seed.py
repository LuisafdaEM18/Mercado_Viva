from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db
from models import Usuario, Producto, Orden, OrdenItem, InventarioTienda

app = create_app()

with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(username="empleado1").first():
        db.session.add(
            Usuario(
                username="empleado1",
                password_hash=generate_password_hash("Clave123"),
                nombre="Empleado de Prueba",
            )
        )

    producto = Producto.query.filter_by(sku="SKU-001").first()
    if not producto:
        producto = Producto(sku="SKU-001", nombre="Audífonos Bluetooth", precio=120000)
        db.session.add(producto)
        db.session.flush()

    if not InventarioTienda.query.filter_by(producto_id=producto.id).first():
        db.session.add(InventarioTienda(producto_id=producto.id, stock=5))

    if not Orden.query.filter_by(numero_orden="ORD-1001").first():
        orden = Orden(
            numero_orden="ORD-1001",
            cliente_documento="123456789",
            cliente_nombre="Laura Gómez",
            fecha_compra=datetime.utcnow() - timedelta(days=5),
            estado="entregada",
            metodo_pago="Tarjeta de crédito",
        )
        db.session.add(orden)
        db.session.flush()
        db.session.add(
            OrdenItem(orden_id=orden.id, producto_id=producto.id, precio_unitario=producto.precio)
        )

    if not Orden.query.filter_by(numero_orden="ORD-1002").first():
        orden_vencida = Orden(
            numero_orden="ORD-1002",
            cliente_documento="987654321",
            cliente_nombre="Carlos Ruiz",
            fecha_compra=datetime.utcnow() - timedelta(days=40),
            estado="entregada",
            metodo_pago="Tarjeta débito",
        )
        db.session.add(orden_vencida)
        db.session.flush()
        db.session.add(
            OrdenItem(orden_id=orden_vencida.id, producto_id=producto.id, precio_unitario=producto.precio)
        )

    if not Orden.query.filter_by(numero_orden="ORD-1003").first():
        orden_fresca = Orden(
            numero_orden="ORD-1003",
            cliente_documento="111222333",
            cliente_nombre="Andres Torres",
            fecha_compra=datetime.utcnow() - timedelta(days=2),
            estado="entregada",
            metodo_pago="Tarjeta de crédito",
        )
        db.session.add(orden_fresca)
        db.session.flush()
        db.session.add(
            OrdenItem(orden_id=orden_fresca.id, producto_id=producto.id, precio_unitario=producto.precio)
        )

    if not Orden.query.filter_by(numero_orden="ORD-1004").first():
        orden_danada = Orden(
            numero_orden="ORD-1004",
            cliente_documento="444555666",
            cliente_nombre="Sofia Ramirez",
            fecha_compra=datetime.utcnow() - timedelta(days=1),
            estado="entregada",
            metodo_pago="PSE",
        )
        db.session.add(orden_danada)
        db.session.flush()
        db.session.add(
            OrdenItem(orden_id=orden_danada.id, producto_id=producto.id, precio_unitario=producto.precio)
        )

    db.session.commit()
    print("Datos de prueba creados correctamente.")
