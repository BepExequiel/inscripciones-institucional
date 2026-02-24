import os
from flask import Flask, render_template, request, redirect, url_for, send_file
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-local")


# =========================
# CONEXIÓN
# =========================
def get_db():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        return psycopg2.connect(
            database_url,
            sslmode="require",
            cursor_factory=RealDictCursor
        )
    else:
        return psycopg2.connect(
            host="localhost",
            port=5432,
            database="inscripciones_local",
            user="inscripciones_user",
            password="inscripciones123",
            cursor_factory=RealDictCursor
        )


# =========================
# LISTADO + FILTROS
# =========================
@app.route("/")
def index():
    buscar = request.args.get("buscar", "")
    perfil_filtro = request.args.get("perfil", "")

    conn = get_db()
    cur = conn.cursor()

    query = "SELECT * FROM inscripciones WHERE 1=1"
    params = []

    if buscar:
        query += " AND (LOWER(nombre) LIKE LOWER(%s) OR LOWER(apellido) LIKE LOWER(%s))"
        params.extend([f"%{buscar}%", f"%{buscar}%"])

    if perfil_filtro:
        query += " AND perfil=%s"
        params.append(perfil_filtro)

    query += " ORDER BY id DESC"

    cur.execute(query, params)
    inscripciones = cur.fetchall()

    cur.execute("SELECT DISTINCT perfil FROM inscripciones ORDER BY perfil")
    perfiles = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        inscripciones=inscripciones,
        perfiles=perfiles,
        buscar=buscar,
        perfil_filtro=perfil_filtro
    )


# =========================
# AGREGAR
# =========================
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = (
            request.form["nombre"],
            request.form["apellido"],
            request.form["dni"],
            request.form["email"],
            request.form["telefono"],
            request.form["perfil"],
            request.form["turno"]
        )

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO inscripciones
            (nombre, apellido, dni, email, telefono, perfil, turno)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, data)

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("form.html")


# =========================
# EDITAR
# =========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        data = (
            request.form["nombre"],
            request.form["apellido"],
            request.form["dni"],
            request.form["email"],
            request.form["telefono"],
            request.form["perfil"],
            request.form["turno"],
            id
        )

        cur.execute("""
            UPDATE inscripciones
            SET nombre=%s, apellido=%s, dni=%s, email=%s,
                telefono=%s, perfil=%s, turno=%s
            WHERE id=%s
        """, data)

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    cur.execute("SELECT * FROM inscripciones WHERE id=%s", (id,))
    registro = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("edit.html", registro=registro)


# =========================
# ELIMINAR
# =========================
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM inscripciones WHERE id=%s", (id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("index"))


# =========================
# EXPORTAR A EXCEL
# =========================
@app.route("/export")
def export():
    conn = get_db()
    df = pd.read_sql("SELECT * FROM inscripciones ORDER BY id DESC", conn)
    conn.close()

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name="inscripciones.xlsx",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)