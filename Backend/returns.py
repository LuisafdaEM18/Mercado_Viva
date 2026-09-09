import uuid
from flask import Blueprint, request, jsonify
from extensions import db
from models import Orden, OrdenItem, Devolucion
from auth import token_required
from business_rules import (
    validar_elegibilidad,
    evaluar_elegibilidad,
    calcular_resultado_reembolso,
    ReglaNegocioError,
    CONDICIONES_VALIDAS,
)
from inventory import incrementar_stock

returns_bp = Blueprint("returns", __name__)


@returns_bp.route("/api/ordenes", methods=["GET"])
@token_required
def buscar_orden():
    numero_orden = (request.args.get("numero_orden") or "").strip()
    documento = (request.args.get("documento") or "").strip()

    if not numero_orden and not documento:
        return jsonify({"error": "Debe indicar numero_orden o documento."}), 400

    query = Orden.query
    if numero_orden:
        query = query.filter_by(numero_orden=numero_orden)
    if documento:
        query = query.filter_by(cliente_documento=documento)

    orden = query.first()
    if orden is None:
        return jsonify({"error": "Orden no encontrada."}), 404

    return jsonify(serializar_orden(orden)), 200


@returns_bp.route("/api/devoluciones", methods=["POST"])
@token_required
def registrar_devolucion():
    data = request.get_json(silent=True) or {}

    orden_item_id = data.get("orden_item_id")
    motivo = (data.get("motivo") or "").strip()
    condicion = (data.get("condicion") or "").strip()
    mal_uso = bool(data.get("mal_uso", False))

    if not orden_item_id or not motivo or not condicion:
        return jsonify({"error": "orden_item_id, motivo y condicion son obligatorios."}), 400

    if condicion not in CONDICIONES_VALIDAS:
        return jsonify(
            {"error": f"Condición inválida. Use uno de: {', '.join(CONDICIONES_VALIDAS)}."}
        ), 400

    orden_item = db.session.get(OrdenItem, orden_item_id)
    if orden_item is None:
        return jsonify({"error": "Ítem de orden no encontrado."}), 404

    orden = orden_item.orden

    try:
        validar_elegibilidad(orden, orden_item)
    except ReglaNegocioError as err:
        return jsonify({"error": err.mensaje}), err.codigo

    estado_reembolso, monto = calcular_resultado_reembolso(orden_item, condicion, mal_uso)

    devolucion = Devolucion(
        orden_item_id=orden_item.id,
        motivo=motivo,
        condicion=condicion,
        mal_uso=mal_uso,
        monto_reembolso=monto,
        estado_reembolso=estado_reembolso,
        numero_seguimiento=f"DEV-{uuid.uuid4().hex[:10].upper()}",
    )
    orden_item.devuelto = True
    incrementar_stock(orden_item.producto_id, 1)

    db.session.add(devolucion)
    db.session.commit()

    return jsonify(serializar_devolucion(devolucion)), 201


@returns_bp.route("/api/devoluciones/<numero_seguimiento>", methods=["GET"])
def consultar_devolucion(numero_seguimiento):
    devolucion = Devolucion.query.filter_by(numero_seguimiento=numero_seguimiento).first()
    if devolucion is None:
        return jsonify({"error": "No se encontró una devolución con ese número de seguimiento."}), 404

    return jsonify(serializar_devolucion(devolucion)), 200


def serializar_orden(orden):
    return {
        "id": orden.id,
        "numero_orden": orden.numero_orden,
        "cliente_nombre": orden.cliente_nombre,
        "cliente_documento": orden.cliente_documento,
        "fecha_compra": orden.fecha_compra.isoformat(),
        "estado": orden.estado,
        "items": [
            {
                "id": item.id,
                "producto": item.producto.nombre,
                "sku": item.producto.sku,
                "precio_unitario": float(item.precio_unitario),
                "devuelto": item.devuelto,
                "elegibilidad": evaluar_elegibilidad(orden, item),
            }
            for item in orden.items
        ],
    }


def serializar_devolucion(devolucion):
    return {
        "id": devolucion.id,
        "numero_seguimiento": devolucion.numero_seguimiento,
        "estado_reembolso": devolucion.estado_reembolso,
        "monto_reembolso": float(devolucion.monto_reembolso),
        "condicion": devolucion.condicion,
        "motivo": devolucion.motivo,
        "fecha_registro": devolucion.fecha_registro.isoformat(),
    }
