from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# =========================
# CONEXIÓN A POSTGRESQL
# =========================
def get_db():
    return psycopg2.connect(
        os.environ.get("DATABASE_URL"),
        cursor_factory=RealDictCursor,
        sslmode="require"
    )

@app.before_first_request
def crear_tablas():
    init_db()
# =========================
# INICIALIZAR BASE
# =========================
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inscripciones (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            dni TEXT,
            email TEXT,
            telefono TEXT,
            curso TEXT NOT NULL,
            turno TEXT NOT NULL,
            perfil TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

# =========================
# LISTADO + FILTROS
# =========================
@app.route("/")
def index():
    search = request.args.get("search", "")
    curso = request.args.get("curso", "")

    conn = get_db()
    cur = conn.cursor()

    query = "SELECT * FROM inscripciones WHERE 1=1"
    params = []

    if search:
        query += " AND (nombre ILIKE %s OR apellido ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    if curso:
        query += " AND curso = %s"
        params.append(curso)

    cur.execute(query, params)
    inscripciones = cur.fetchall()

    cur.execute("SELECT DISTINCT curso FROM inscripciones")
    cursos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        inscripciones=inscripciones,
        cursos=cursos
    )

# =========================
# AGREGAR REGISTRO
# =========================
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        dni = request.form["dni"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        curso = request.form["curso"]
        turno = request.form["turno"]
        perfil = request.form["perfil"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO inscripciones
            (nombre, apellido, dni, email, telefono, curso, turno, perfil)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre, apellido, dni, email,
            telefono, curso, turno, perfil
        ))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("form.html")

# =========================
# EDITAR REGISTRO
# =========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        dni = request.form["dni"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        curso = request.form["curso"]
        turno = request.form["turno"]
        perfil = request.form["perfil"]

        cur.execute("""
            UPDATE inscripciones
            SET nombre=%s, apellido=%s, dni=%s, email=%s,
                telefono=%s, curso=%s, turno=%s, perfil=%s
            WHERE id=%s
        """, (
            nombre, apellido, dni, email,
            telefono, curso, turno, perfil, id
        ))

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
# START
# =========================
if __name__ == "__main__":
    
    app.run()
