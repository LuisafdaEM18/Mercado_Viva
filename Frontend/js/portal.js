document.getElementById("form-consulta").addEventListener("submit", async (e) => {
  e.preventDefault();

  const errorEl = document.getElementById("consulta-error");
  const resultadoEl = document.getElementById("resultado");
  errorEl.hidden = true;
  resultadoEl.hidden = true;

  const numeroSeguimiento = document.getElementById("numero-seguimiento").value.trim();

  try {
    const respuesta = await fetch(`${API_BASE_URL}/api/devoluciones/${encodeURIComponent(numeroSeguimiento)}`);
    const cuerpo = await respuesta.json().catch(() => ({}));

    if (!respuesta.ok) {
      throw new Error(cuerpo.error || "Ocurrió un error inesperado.");
    }

    mostrarResultado(cuerpo);
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.hidden = false;
  }
});

const ESTADO_TEXTO = {
  aprobado: "Aprobada — tu reembolso fue procesado",
  pendiente: "Pendiente — el producto dañado está en revisión manual",
  rechazado: "Rechazada — no genera reembolso",
};

function mostrarResultado(devolucion) {
  const resultadoEl = document.getElementById("resultado");

  resultadoEl.innerHTML = `
    <p><strong>Número de seguimiento:</strong> ${devolucion.numero_seguimiento}</p>
    <p><strong>Estado:</strong> ${ESTADO_TEXTO[devolucion.estado_reembolso]}</p>
    <p><strong>Monto del reembolso:</strong> $${devolucion.monto_reembolso.toLocaleString("es-CO")}</p>
    <p><strong>Método de pago original:</strong> ${devolucion.metodo_pago}</p>
    <p><strong>Fecha de registro:</strong> ${new Date(devolucion.fecha_registro).toLocaleDateString("es-CO")}</p>
  `;
  resultadoEl.hidden = false;
}
