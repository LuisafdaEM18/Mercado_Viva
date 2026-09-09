let token = null;
let empleadoNombre = null;
let ordenActual = null;
let devolucionActual = null;

const ESTADO_TEXTO = {
  aprobado: "Aprobada — el reembolso fue procesado",
  pendiente: "Pendiente — el producto dañado está en revisión manual",
  rechazado: "Rechazada — no genera reembolso",
};

const pantallas = {
  login: document.getElementById("seccion-login"),
  buscar: document.getElementById("seccion-buscar"),
  registro: document.getElementById("seccion-registro"),
  confirmacion: document.getElementById("seccion-confirmacion"),
};

function mostrarPantalla(nombre) {
  Object.values(pantallas).forEach((el) => (el.hidden = true));
  pantallas[nombre].hidden = false;
}

function mostrarError(elementoId, mensaje) {
  const el = document.getElementById(elementoId);
  el.textContent = mensaje;
  el.hidden = false;
}

function ocultarError(elementoId) {
  document.getElementById(elementoId).hidden = true;
}

async function llamarApi(ruta, opciones = {}) {
  const headers = { "Content-Type": "application/json", ...opciones.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const respuesta = await fetch(`${API_BASE_URL}${ruta}`, { ...opciones, headers });
  const cuerpo = await respuesta.json().catch(() => ({}));

  if (!respuesta.ok) {
    throw new Error(cuerpo.error || "Ocurrió un error inesperado.");
  }
  return cuerpo;
}

document.getElementById("form-login").addEventListener("submit", async (e) => {
  e.preventDefault();
  ocultarError("login-error");

  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const data = await llamarApi("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    token = data.token;
    empleadoNombre = data.nombre;
    document.getElementById("empleado-nombre").textContent = `Empleado: ${empleadoNombre}`;
    document.getElementById("form-login").reset();
    mostrarPantalla("buscar");
  } catch (err) {
    mostrarError("login-error", err.message);
  }
});

document.getElementById("btn-cerrar-sesion").addEventListener("click", () => {
  token = null;
  empleadoNombre = null;
  mostrarPantalla("login");
});

document.getElementById("form-buscar").addEventListener("submit", async (e) => {
  e.preventDefault();
  ocultarError("buscar-error");

  const numeroOrden = document.getElementById("buscar-numero-orden").value.trim();
  const documento = document.getElementById("buscar-documento").value.trim();

  if (!numeroOrden && !documento) {
    mostrarError("buscar-error", "Ingresa un número de orden o un documento.");
    return;
  }

  const params = new URLSearchParams();
  if (numeroOrden) params.set("numero_orden", numeroOrden);
  if (documento) params.set("documento", documento);

  try {
    const orden = await llamarApi(`/api/ordenes?${params.toString()}`);
    renderizarOrden(orden);
    document.getElementById("form-buscar").reset();
    mostrarPantalla("registro");
  } catch (err) {
    mostrarError("buscar-error", err.message);
  }
});

function renderizarOrden(orden) {
  ordenActual = orden;
  const contenedor = document.getElementById("detalle-orden");
  const formDevolucion = document.getElementById("form-devolucion");
  formDevolucion.hidden = true;

  const itemsHtml = orden.items
    .map((item) => {
      const elegible = item.elegibilidad.elegible;
      const motivoNoElegible = !elegible
        ? [
            !item.elegibilidad.orden_entregada && "la orden no está entregada",
            !item.elegibilidad.dentro_de_plazo && "fuera del plazo de 30 días",
            item.elegibilidad.ya_devuelto && "ya fue devuelto",
          ]
            .filter(Boolean)
            .join(", ")
        : "";

      return `
        <div class="item-orden">
          <p><strong>${item.producto}</strong> (${item.sku}) - $${item.precio_unitario.toLocaleString("es-CO")}</p>
          ${
            elegible
              ? `<button type="button" class="btn-elegir-item" data-item-id="${item.id}">Devolver este ítem</button>`
              : `<p class="aviso">No elegible: ${motivoNoElegible}</p>`
          }
        </div>
      `;
    })
    .join("");

  contenedor.innerHTML = `
    <p><strong>Orden:</strong> ${orden.numero_orden}</p>
    <p><strong>Cliente:</strong> ${orden.cliente_nombre} (${orden.cliente_documento})</p>
    <p><strong>Fecha de compra:</strong> ${new Date(orden.fecha_compra).toLocaleDateString("es-CO")}</p>
    <p><strong>Estado:</strong> ${orden.estado}</p>
    <p><strong>Método de pago:</strong> ${orden.metodo_pago}</p>
    <h3>Ítems</h3>
    ${itemsHtml}
  `;

  document.querySelectorAll(".btn-elegir-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("devolucion-item-id").value = btn.dataset.itemId;
      formDevolucion.hidden = false;
      formDevolucion.scrollIntoView({ behavior: "smooth" });
    });
  });
}

document.getElementById("devolucion-condicion").addEventListener("change", (e) => {
  const wrapper = document.getElementById("devolucion-mal-uso-wrapper");
  wrapper.hidden = e.target.value !== "dañado";
  if (wrapper.hidden) document.getElementById("devolucion-mal-uso").checked = false;
});

document.getElementById("form-devolucion").addEventListener("submit", async (e) => {
  e.preventDefault();
  ocultarError("registro-error");

  const ordenItemId = Number(document.getElementById("devolucion-item-id").value);
  const motivo = document.getElementById("devolucion-motivo").value.trim();
  const condicion = document.getElementById("devolucion-condicion").value;
  const malUso = document.getElementById("devolucion-mal-uso").checked;

  try {
    const devolucion = await llamarApi("/api/devoluciones", {
      method: "POST",
      body: JSON.stringify({ orden_item_id: ordenItemId, motivo, condicion, mal_uso: malUso }),
    });
    mostrarConfirmacion(devolucion);
    document.getElementById("form-devolucion").reset();
    mostrarPantalla("confirmacion");
  } catch (err) {
    mostrarError("registro-error", err.message);
  }
});

function mostrarConfirmacion(devolucion) {
  devolucionActual = devolucion;
  const contenedor = document.getElementById("confirmacion-detalle");

  contenedor.innerHTML = `
    <p><strong>Número de seguimiento:</strong> ${devolucion.numero_seguimiento}</p>
    <p><strong>Estado:</strong> ${ESTADO_TEXTO[devolucion.estado_reembolso]}</p>
    <p><strong>Monto del reembolso:</strong> $${devolucion.monto_reembolso.toLocaleString("es-CO")}</p>
    <p><strong>Método de pago original:</strong> ${devolucion.metodo_pago}</p>
  `;
}

function generarTextoComprobante(orden, devolucion) {
  return [
    "MERCADO VIVA - COMPROBANTE DE DEVOLUCION",
    "==========================================",
    `Numero de seguimiento: ${devolucion.numero_seguimiento}`,
    `Fecha de registro: ${new Date(devolucion.fecha_registro).toLocaleString("es-CO")}`,
    "",
    `Orden: ${orden.numero_orden}`,
    `Cliente: ${orden.cliente_nombre} (${orden.cliente_documento})`,
    "",
    `Motivo: ${devolucion.motivo}`,
    `Condicion del producto: ${devolucion.condicion}`,
    `Estado del reembolso: ${ESTADO_TEXTO[devolucion.estado_reembolso]}`,
    `Monto del reembolso: $${devolucion.monto_reembolso.toLocaleString("es-CO")}`,
    `Metodo de pago original: ${devolucion.metodo_pago}`,
  ].join("\n");
}

document.getElementById("btn-descargar-comprobante").addEventListener("click", () => {
  const texto = generarTextoComprobante(ordenActual, devolucionActual);
  const blob = new Blob([texto], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = `comprobante-${devolucionActual.numero_seguimiento}.txt`;
  enlace.click();

  URL.revokeObjectURL(url);
});

document.getElementById("btn-volver-buscar").addEventListener("click", () => {
  mostrarPantalla("buscar");
});

document.getElementById("btn-nueva-devolucion").addEventListener("click", () => {
  mostrarPantalla("buscar");
});
