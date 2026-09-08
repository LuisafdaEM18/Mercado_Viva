from datetime import datetime
from extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)


class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)


class Orden(db.Model):
    __tablename__ = "ordenes"
    id = db.Column(db.Integer, primary_key=True)
    numero_orden = db.Column(db.String(30), unique=True, nullable=False)
    cliente_documento = db.Column(db.String(30), nullable=False)
    cliente_nombre = db.Column(db.String(150), nullable=False)
    fecha_compra = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="entregada")

    items = db.relationship("OrdenItem", backref="orden", lazy=True)


class OrdenItem(db.Model):
    __tablename__ = "orden_items"
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey("ordenes.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    devuelto = db.Column(db.Boolean, nullable=False, default=False)

    producto = db.relationship("Producto")


class Devolucion(db.Model):
    __tablename__ = "devoluciones"
    id = db.Column(db.Integer, primary_key=True)
    orden_item_id = db.Column(db.Integer, db.ForeignKey("orden_items.id"), nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    condicion = db.Column(db.String(20), nullable=False)
    mal_uso = db.Column(db.Boolean, nullable=False, default=False)
    monto_reembolso = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    estado_reembolso = db.Column(db.String(20), nullable=False)
    numero_seguimiento = db.Column(db.String(40), unique=True, nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    orden_item = db.relationship("OrdenItem")


class InventarioTienda(db.Model):
    __tablename__ = "inventario_tienda"
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), unique=True, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)

    producto = db.relationship("Producto")
