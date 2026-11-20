// Vista previa del costo total. El cálculo definitivo se hace en el servidor.
(function () {
    const vehiculo = document.getElementById("vehiculo_id");
    const inicio = document.getElementById("fecha_alquiler");
    const fin = document.getElementById("fecha_devolucion");
    const total = document.getElementById("total");
    const detalle = document.getElementById("detalle");
    if (!vehiculo) return;

    function actualizar() {
        const opcion = vehiculo.options[vehiculo.selectedIndex];
        const precio = parseFloat(opcion.dataset.precio || "0");
        const dias = Math.round((new Date(fin.value) - new Date(inicio.value)) / 86400000);
        if (inicio.value) fin.min = inicio.value;

        if (!precio || !inicio.value || !fin.value) {
            total.textContent = "S/ 0.00";
            detalle.textContent = "Seleccione el vehículo y las fechas.";
        } else if (dias < 1) {
            total.textContent = "S/ 0.00";
            detalle.textContent = "La fecha de devolución debe ser posterior a la de alquiler.";
        } else {
            total.textContent = "S/ " + (dias * precio).toFixed(2);
            detalle.textContent = dias + " día(s) × S/ " + precio.toFixed(2) + " por día";
        }
    }

    [vehiculo, inicio, fin].forEach(function (campo) {
        campo.addEventListener("change", actualizar);
    });
    actualizar();
})();
