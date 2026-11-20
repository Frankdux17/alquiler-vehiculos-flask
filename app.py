"""Aplicación web para alquiler de vehículos (Flask + SQLite).

Módulos: Vehículos, Clientes y Alquileres, cada uno con sus operaciones CRUD.
"""
import logging
import os
import sqlite3
import sys
from datetime import date, datetime

from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, url_for)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
# La configuración sale de variables de entorno (ver sesión 7: despliegue).
app.secret_key = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo")
DATABASE = os.environ.get("DATABASE_URL", os.path.join(BASE_DIR, "alquiler.db"))

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


# ---------------------------------------------------------------- Base de datos
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crea las tablas si todavía no existen."""
    conn = sqlite3.connect(DATABASE)
    with open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8") as f:
        conn.executescript(f.read())
    vacia = conn.execute("SELECT COUNT(*) FROM vehiculos").fetchone()[0] == 0
    if vacia and os.environ.get("DATOS_DEMO") == "1":
        with open(os.path.join(BASE_DIR, "datos_demo.sql"), encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()


init_db()
app.logger.info("Aplicación iniciada")


# ---------------------------------------------------------------------- Inicio
@app.route("/")
def index():
    db = get_db()
    resumen = {
        "vehiculos": db.execute("SELECT COUNT(*) FROM vehiculos").fetchone()[0],
        "clientes": db.execute("SELECT COUNT(*) FROM clientes").fetchone()[0],
        "alquileres": db.execute("SELECT COUNT(*) FROM alquileres").fetchone()[0],
        "alquilados": db.execute(
            "SELECT COUNT(DISTINCT vehiculo_id) FROM alquileres WHERE estado = 'activo'"
        ).fetchone()[0],
        "ingresos": db.execute(
            "SELECT COALESCE(SUM(costo_total), 0) FROM alquileres"
        ).fetchone()[0],
    }
    resumen["disponibles"] = resumen["vehiculos"] - resumen["alquilados"]
    return render_template("index.html", resumen=resumen)


@app.route("/health")
def health():
    return jsonify(estado="ok"), 200


# ------------------------------------------------------------------- Vehículos
SQL_VEHICULOS = """
    SELECT v.*,
           EXISTS(SELECT 1 FROM alquileres a
                  WHERE a.vehiculo_id = v.id AND a.estado = 'activo') AS alquilado
    FROM vehiculos v
"""


def leer_vehiculo_form():
    """Devuelve (datos, error) a partir del formulario de vehículo."""
    datos = {
        "marca": request.form.get("marca", "").strip(),
        "modelo": request.form.get("modelo", "").strip(),
        "placa": request.form.get("placa", "").strip().upper(),
        "precio_dia": request.form.get("precio_dia", "").strip(),
    }
    if not all(datos.values()):
        return datos, "Todos los campos son obligatorios."
    try:
        precio = float(datos["precio_dia"])
    except ValueError:
        return datos, "El precio por día debe ser un número."
    if precio <= 0:
        return datos, "El precio por día debe ser mayor que cero."
    datos["precio_dia"] = precio
    return datos, None


@app.route("/vehiculos")
def vehiculos_listar():
    vehiculos = get_db().execute(SQL_VEHICULOS + " ORDER BY v.marca, v.modelo").fetchall()
    return render_template("vehiculos/lista.html", vehiculos=vehiculos)


@app.route("/vehiculos/nuevo", methods=["GET", "POST"])
def vehiculos_nuevo():
    datos = {}
    if request.method == "POST":
        datos, error = leer_vehiculo_form()
        if error is None:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO vehiculos (marca, modelo, placa, precio_dia) VALUES (?, ?, ?, ?)",
                    (datos["marca"], datos["modelo"], datos["placa"], datos["precio_dia"]),
                )
                db.commit()
                flash("Vehículo registrado correctamente.", "success")
                return redirect(url_for("vehiculos_listar"))
            except sqlite3.IntegrityError:
                error = f"Ya existe un vehículo con la placa {datos['placa']}."
        flash(error, "danger")
    return render_template("vehiculos/form.html", vehiculo=datos, titulo="Registrar vehículo")


@app.route("/vehiculos/<int:id>/editar", methods=["GET", "POST"])
def vehiculos_editar(id):
    db = get_db()
    vehiculo = db.execute("SELECT * FROM vehiculos WHERE id = ?", (id,)).fetchone()
    if vehiculo is None:
        flash("El vehículo no existe.", "danger")
        return redirect(url_for("vehiculos_listar"))
    if request.method == "POST":
        datos, error = leer_vehiculo_form()
        if error is None:
            try:
                db.execute(
                    "UPDATE vehiculos SET marca = ?, modelo = ?, placa = ?, precio_dia = ? WHERE id = ?",
                    (datos["marca"], datos["modelo"], datos["placa"], datos["precio_dia"], id),
                )
                db.commit()
                flash("Vehículo actualizado correctamente.", "success")
                return redirect(url_for("vehiculos_listar"))
            except sqlite3.IntegrityError:
                error = f"Ya existe un vehículo con la placa {datos['placa']}."
        flash(error, "danger")
        vehiculo = datos
    return render_template("vehiculos/form.html", vehiculo=vehiculo, titulo="Editar vehículo")


@app.route("/vehiculos/<int:id>/eliminar", methods=["POST"])
def vehiculos_eliminar(id):
    db = get_db()
    try:
        db.execute("DELETE FROM vehiculos WHERE id = ?", (id,))
        db.commit()
        flash("Vehículo eliminado.", "success")
    except sqlite3.IntegrityError:
        flash("No se puede eliminar: el vehículo tiene alquileres registrados.", "danger")
    return redirect(url_for("vehiculos_listar"))


# -------------------------------------------------------------------- Clientes
def leer_cliente_form():
    datos = {
        "nombres": request.form.get("nombres", "").strip(),
        "apellidos": request.form.get("apellidos", "").strip(),
        "dni": request.form.get("dni", "").strip(),
        "telefono": request.form.get("telefono", "").strip(),
    }
    if not all(datos.values()):
        return datos, "Todos los campos son obligatorios."
    if not (datos["dni"].isdigit() and len(datos["dni"]) == 8):
        return datos, "El DNI debe tener 8 dígitos."
    if not (datos["telefono"].isdigit() and len(datos["telefono"]) == 9):
        return datos, "El teléfono debe tener 9 dígitos."
    return datos, None


@app.route("/clientes")
def clientes_listar():
    clientes = get_db().execute("SELECT * FROM clientes ORDER BY apellidos, nombres").fetchall()
    return render_template("clientes/lista.html", clientes=clientes)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def clientes_nuevo():
    datos = {}
    if request.method == "POST":
        datos, error = leer_cliente_form()
        if error is None:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO clientes (nombres, apellidos, dni, telefono) VALUES (?, ?, ?, ?)",
                    (datos["nombres"], datos["apellidos"], datos["dni"], datos["telefono"]),
                )
                db.commit()
                flash("Cliente registrado correctamente.", "success")
                return redirect(url_for("clientes_listar"))
            except sqlite3.IntegrityError:
                error = f"Ya existe un cliente con el DNI {datos['dni']}."
        flash(error, "danger")
    return render_template("clientes/form.html", cliente=datos, titulo="Registrar cliente")


@app.route("/clientes/<int:id>/editar", methods=["GET", "POST"])
def clientes_editar(id):
    db = get_db()
    cliente = db.execute("SELECT * FROM clientes WHERE id = ?", (id,)).fetchone()
    if cliente is None:
        flash("El cliente no existe.", "danger")
        return redirect(url_for("clientes_listar"))
    if request.method == "POST":
        datos, error = leer_cliente_form()
        if error is None:
            try:
                db.execute(
                    "UPDATE clientes SET nombres = ?, apellidos = ?, dni = ?, telefono = ? WHERE id = ?",
                    (datos["nombres"], datos["apellidos"], datos["dni"], datos["telefono"], id),
                )
                db.commit()
                flash("Cliente actualizado correctamente.", "success")
                return redirect(url_for("clientes_listar"))
            except sqlite3.IntegrityError:
                error = f"Ya existe un cliente con el DNI {datos['dni']}."
        flash(error, "danger")
        cliente = datos
    return render_template("clientes/form.html", cliente=cliente, titulo="Editar cliente")


@app.route("/clientes/<int:id>/eliminar", methods=["POST"])
def clientes_eliminar(id):
    db = get_db()
    try:
        db.execute("DELETE FROM clientes WHERE id = ?", (id,))
        db.commit()
        flash("Cliente eliminado.", "success")
    except sqlite3.IntegrityError:
        flash("No se puede eliminar: el cliente tiene alquileres registrados.", "danger")
    return redirect(url_for("clientes_listar"))


# ------------------------------------------------------------------ Alquileres
def calcular_dias(fecha_alquiler, fecha_devolucion):
    """Días de alquiler entre dos fechas ISO (AAAA-MM-DD)."""
    inicio = datetime.strptime(fecha_alquiler, "%Y-%m-%d").date()
    fin = datetime.strptime(fecha_devolucion, "%Y-%m-%d").date()
    return (fin - inicio).days


@app.route("/alquileres")
def alquileres_listar():
    alquileres = get_db().execute(
        """
        SELECT a.*, c.nombres || ' ' || c.apellidos AS cliente, c.dni,
               v.marca || ' ' || v.modelo AS vehiculo, v.placa
        FROM alquileres a
        JOIN clientes c ON c.id = a.cliente_id
        JOIN vehiculos v ON v.id = a.vehiculo_id
        ORDER BY a.id DESC
        """
    ).fetchall()
    return render_template("alquileres/lista.html", alquileres=alquileres)


@app.route("/alquileres/nuevo", methods=["GET", "POST"])
def alquileres_nuevo():
    db = get_db()
    datos = {"fecha_alquiler": date.today().isoformat()}
    if request.method == "POST":
        datos = {
            "cliente_id": request.form.get("cliente_id", ""),
            "vehiculo_id": request.form.get("vehiculo_id", ""),
            "fecha_alquiler": request.form.get("fecha_alquiler", ""),
            "fecha_devolucion": request.form.get("fecha_devolucion", ""),
        }
        error = None
        vehiculo = db.execute(
            SQL_VEHICULOS + " WHERE v.id = ?", (datos["vehiculo_id"],)
        ).fetchone()
        cliente = db.execute(
            "SELECT id FROM clientes WHERE id = ?", (datos["cliente_id"],)
        ).fetchone()
        if not all(datos.values()):
            error = "Todos los campos son obligatorios."
        elif cliente is None or vehiculo is None:
            error = "Seleccione un cliente y un vehículo válidos."
        elif vehiculo["alquilado"]:
            error = "El vehículo seleccionado ya está alquilado."
        else:
            try:
                dias = calcular_dias(datos["fecha_alquiler"], datos["fecha_devolucion"])
            except ValueError:
                dias, error = 0, "Las fechas no son válidas."
            if error is None and dias < 1:
                error = "La fecha de devolución debe ser posterior a la fecha de alquiler."
        if error is None:
            costo_total = round(dias * vehiculo["precio_dia"], 2)
            db.execute(
                """INSERT INTO alquileres
                   (cliente_id, vehiculo_id, fecha_alquiler, fecha_devolucion, dias, costo_total)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (datos["cliente_id"], datos["vehiculo_id"], datos["fecha_alquiler"],
                 datos["fecha_devolucion"], dias, costo_total),
            )
            db.commit()
            flash(f"Alquiler registrado: {dias} día(s), costo total S/ {costo_total:.2f}.", "success")
            return redirect(url_for("alquileres_listar"))
        flash(error, "danger")
    clientes = db.execute("SELECT * FROM clientes ORDER BY apellidos, nombres").fetchall()
    vehiculos = db.execute(SQL_VEHICULOS + " ORDER BY v.marca, v.modelo").fetchall()
    disponibles = [v for v in vehiculos if not v["alquilado"]]
    return render_template("alquileres/form.html", clientes=clientes,
                           vehiculos=disponibles, alquiler=datos)


@app.route("/alquileres/<int:id>/devolver", methods=["POST"])
def alquileres_devolver(id):
    db = get_db()
    db.execute("UPDATE alquileres SET estado = 'devuelto' WHERE id = ?", (id,))
    db.commit()
    flash("Devolución registrada: el vehículo vuelve a estar disponible.", "success")
    return redirect(url_for("alquileres_listar"))


@app.route("/alquileres/<int:id>/eliminar", methods=["POST"])
def alquileres_eliminar(id):
    db = get_db()
    db.execute("DELETE FROM alquileres WHERE id = ?", (id,))
    db.commit()
    flash("Alquiler eliminado.", "success")
    return redirect(url_for("alquileres_listar"))


@app.template_filter("fecha")
def formato_fecha(valor):
    """AAAA-MM-DD -> DD/MM/AAAA."""
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return valor


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1",
            port=int(os.environ.get("PORT", 5000)))
