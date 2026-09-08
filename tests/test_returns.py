def test_registrar_devolucion_exitosa(client, token, orden_elegible):
    resp = client.post(
        "/api/devoluciones",
        json={
            "orden_item_id": orden_elegible["orden_item_id"],
            "motivo": "Producto no cumple expectativas",
            "condicion": "nuevo",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["estado_reembolso"] == "aprobado"
    assert body["monto_reembolso"] == 50000.0


def test_buscar_orden_inexistente_retorna_404(client, token):
    resp = client.get(
        "/api/ordenes?numero_orden=NO-EXISTE",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_no_permite_devolver_el_mismo_item_dos_veces(client, token, orden_elegible):
    payload = {
        "orden_item_id": orden_elegible["orden_item_id"],
        "motivo": "Talla incorrecta",
        "condicion": "abierto",
    }
    headers = {"Authorization": f"Bearer {token}"}

    primera = client.post("/api/devoluciones", json=payload, headers=headers)
    assert primera.status_code == 201

    segunda = client.post("/api/devoluciones", json=payload, headers=headers)
    assert segunda.status_code == 400
    assert "ya fue devuelto" in segunda.get_json()["error"]


def test_producto_danado_por_mal_uso_no_genera_reembolso(client, token, orden_elegible):
    resp = client.post(
        "/api/devoluciones",
        json={
            "orden_item_id": orden_elegible["orden_item_id"],
            "motivo": "Se dañó",
            "condicion": "dañado",
            "mal_uso": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["estado_reembolso"] == "rechazado"
    assert body["monto_reembolso"] == 0.0
