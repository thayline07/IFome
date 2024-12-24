from flask import Flask, render_template, request, jsonify, redirect, flash, url_for
import sqlite3


app = Flask(__name__)


def conectar():
    return sqlite3.connect("db.sqlite")

if __name__ == '__main__':
    app.run(debug=True)


def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER NOT NULL PRIMARY KEY,
            nome TEXT NOT NULL,
            imagem BLOB,
            descricao TEXT UNIQUE NOT NULL,
            link TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT NOT NULL PRIMARY KEY,
            password TEXT NOT NULL,
            produto_id INTEGER NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)     
        )
    ''')
    
    conexao.commit()
    conexao.close()


criar_tabelas()


@app.route('/')
def home():
    return render_template("principal.html")


@app.route('/perfil')
def perfil():
    return render_template("perfil.html")


@app.route('/principal')
def principal():
    return render_template("principal.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/cadastro')
def cadastro():
    return render_template("cadastro.html")


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        
        if usuario:
            flash('Email já cadastrado! Tente outro.', 'error')
            return redirect(url_for('cadastro'))
        
        cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha))
        conexao.commit()
        conexao.close()
        
        flash('Cadastro realizado com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')
