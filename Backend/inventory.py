from extensions import db
from models import InventarioTienda


def incrementar_stock(producto_id, cantidad=1):
    item = InventarioTienda.query.filter_by(producto_id=producto_id).first()
    if item is None:
        item = InventarioTienda(producto_id=producto_id, stock=0)
        db.session.add(item)

    item.stock += cantidad
    return item
