from datetime import datetime, timedelta

PLAZO_DIAS = 30
CONDICIONES_VALIDAS = {"nuevo", "abierto", "dañado"}


class ReglaNegocioError(Exception):
    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


def validar_elegibilidad(orden, orden_item):
    if orden.estado != "entregada":
        raise ReglaNegocioError(
            f"La orden no está en estado 'entregada' (estado actual: {orden.estado})."
        )

    limite = orden.fecha_compra + timedelta(days=PLAZO_DIAS)
    if datetime.utcnow() > limite:
        raise ReglaNegocioError(
            "La orden está fuera del plazo de 30 días calendario para devoluciones."
        )

    if orden_item.devuelto:
        raise ReglaNegocioError("Este ítem ya fue devuelto anteriormente.")


def evaluar_elegibilidad(orden, orden_item):
    limite = orden.fecha_compra + timedelta(days=PLAZO_DIAS)
    dentro_de_plazo = datetime.utcnow() <= limite
    orden_entregada = orden.estado == "entregada"

    return {
        "orden_entregada": orden_entregada,
        "dentro_de_plazo": dentro_de_plazo,
        "ya_devuelto": orden_item.devuelto,
        "elegible": orden_entregada and dentro_de_plazo and not orden_item.devuelto,
    }


def calcular_resultado_reembolso(orden_item, condicion, mal_uso):
    if condicion == "dañado" and mal_uso:
        return "pendiente", 0

    return "aprobado", float(orden_item.precio_unitario)
