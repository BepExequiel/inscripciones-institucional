from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

@app.route("/")
def index():
    search = request.args.get("search", "")
    curso = request.args.get("curso", "")

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM inscripciones WHERE 1=1"
    params = []

    if search:
        query += " AND (nombre LIKE ? OR apellido LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if curso:
        query += " AND curso = ?"
        params.append(curso)

    cursor.execute(query, params)
    inscripciones = cursor.fetchall()

    cursos = cursor.execute(
        "SELECT DISTINCT curso FROM inscripciones"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        inscripciones=inscripciones,
        cursos=cursos
    )

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        curso = request.form["curso"]
        turno = request.form["turno"]

        conn = get_db()
        conn.execute(
            "INSERT INTO inscripciones (nombre, apellido, curso, turno) VALUES (?, ?, ?, ?)",
            (nombre, apellido, curso, turno)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("form.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        curso = request.form["curso"]
        turno = request.form["turno"]

        cursor.execute(
            """
            UPDATE inscripciones
            SET nombre=?, apellido=?, curso=?, turno=?
            WHERE id=?
            """,
            (nombre, apellido, curso, turno, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    inscripcion = cursor.execute(
        "SELECT * FROM inscripciones WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()
    return render_template("edit.html", inscripcion=inscripcion)

if __name__ == "__main__":
    app.run(debug=True)
