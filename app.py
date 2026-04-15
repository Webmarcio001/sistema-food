from flask import Flask, render_template, request, redirect, session
import sqlite3, datetime

app = Flask(__name__)
app.secret_key = "123"

def db():
    return sqlite3.connect("banco.db")

def criar():
    conn = db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS produtos(
        id INTEGER PRIMARY KEY,
        nome TEXT,
        categoria TEXT,
        codigo TEXT,
        preco REAL,
        estoque INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS vendas(
        id INTEGER PRIMARY KEY,
        produto TEXT,
        valor REAL,
        data TEXT
    )""")

    conn.commit()
    conn.close()

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["user"] == "admin" and request.form["pass"] == "123":
            session["logado"] = True
            return redirect("/home")
    return render_template("login.html")

# HOME
@app.route("/home")
def home():
    if not session.get("logado"):
        return redirect("/")
    return render_template("index.html")

# PRODUTOS
@app.route("/produtos", methods=["GET","POST"])
def produtos():
    conn = db()
    c = conn.cursor()

    if request.method == "POST":
        c.execute("INSERT INTO produtos(nome,categoria,codigo,preco,estoque) VALUES (?,?,?,?,?)",
        (request.form["nome"], request.form["categoria"], request.form["codigo"], request.form["preco"], request.form["estoque"]))
        conn.commit()

    busca = request.args.get("q")
    if busca:
        c.execute("SELECT * FROM produtos WHERE nome LIKE ? OR codigo LIKE ?",('%'+busca+'%','%'+busca+'%'))
    else:
        c.execute("SELECT * FROM produtos")

    dados = c.fetchall()
    conn.close()

    return render_template("produtos.html", produtos=dados)

# PDV
@app.route("/pdv", methods=["GET","POST"])
def pdv():
    conn = db()
    c = conn.cursor()

    if request.method == "POST":
        nome = request.form["produto"]
        valor = float(request.form["valor"])

        c.execute("INSERT INTO vendas(produto,valor,data) VALUES (?,?,?)",
        (nome, valor, str(datetime.date.today())))

        c.execute("UPDATE produtos SET estoque = estoque - 1 WHERE nome=?", (nome,))
        conn.commit()

    c.execute("SELECT * FROM produtos")
    produtos = c.fetchall()

    conn.close()

    return render_template("pdv.html", produtos=produtos)

# FINANCEIRO
@app.route("/financeiro")
def financeiro():
    conn = db()
    c = conn.cursor()

    c.execute("SELECT SUM(valor) FROM vendas")
    total = c.fetchone()[0] or 0

    c.execute("SELECT * FROM vendas")
    vendas = c.fetchall()

    conn.close()

    return render_template("financeiro.html", vendas=vendas, total=total)

criar()

if __name__ == "__main__":
    app.run(debug=True)