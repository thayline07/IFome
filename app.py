from flask import Flask, render_template, request, jsonify, redirect, flash, url_for, session
import sqlite3
from jinja2 import Template, Environment, FileSystemLoader
import base64
import logging


logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)


def conectar():
    return sqlite3.connect("db.sqlite")


app.secret_key = "chave_secreta_segura"


#Jinja
env = Environment(loader=FileSystemLoader('templates'))
env.trim_blocks = True
env.lstrip_blocks = True


def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            nome TEXT NOT NULL PRIMARY KEY,
            imagem BLOB,
            descricao TEXT UNIQUE NOT NULL,
            link TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT NOT NULL PRIMARY KEY,
            password TEXT NOT NULL    
        )
    ''')
    
    conexao.commit()
    conexao.close()


criar_tabelas()

# Principal
@app.route('/')
def home():
    return render_template("login.html")


# Perfil
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'GET':
        return render_template("perfil.html")
    elif request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        link = request.form.get('link')
        imagem = request.files.get('imagem')

        print(f"Nome: {nome}, Descrição: {descricao}, Link: {link}, Imagem: {imagem.filename if imagem else 'Nenhuma'}")

        if not nome or not imagem or not descricao or not link:
            flash("Todos os campos são obrigatórios!")
            return redirect(url_for('perfil'))

        if imagem:
            imagem_binaria = imagem.read()  
        else:
            flash("Imagem inválida!")
            return redirect(url_for('perfil'))

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute('''
                INSERT INTO produtos (nome, imagem, descricao, link)
                VALUES (?, ?, ?, ?)
            ''', (nome, imagem_binaria, descricao, link))
            conexao.commit()
            conexao.close()

            flash("Produto adicionado com sucesso!")
            return redirect(url_for('perfil'))
        except sqlite3.IntegrityError:
            flash("Erro: Produto já cadastrado.")
            return redirect(url_for('perfil'))



# Principal 2
@app.route('/principal')
def principal():
    conexao = conectar()
    cursor = conexao.cursor()
    produtos = cursor.execute('SELECT * FROM produtos').fetchall()
    conexao.close()

    produtos_com_imagens = []
    for produto in produtos:
        nome, imagem_blob, descricao, link = produto
        if imagem_blob:
            imagem_base64 = base64.b64encode(imagem_blob).decode('utf-8')
            imagem_data_uri = f"data:image/jpeg;base64,{imagem_base64}"
        else:
            imagem_data_uri = None

        produtos_com_imagens.append({
            "nome": nome,
            "imagem": imagem_data_uri,
            "descricao": descricao,
            "link": link
        })

    return render_template("principal.html", produtos=produtos_com_imagens)


# Página do produto
@app.route('/produto')
def produto():
    return render_template("produto.html")


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

    if not email or not password:
            flash("Todos os campos são obrigatórios!")
            return redirect(url_for('login'))

    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = ? AND password = ?', (email, password))
        usuario = cursor.fetchone()
        conexao.close()

        if usuario:
            session['user_email'] = email 
            flash("Login realizado com sucesso!")
            return redirect(url_for('principal'))
        else:
            flash("Email ou senha inválidos!")
            return redirect(url_for('login'))

    except Exception as e:
        flash(f"Erro ao tentar fazer login: {e}")
        return redirect(url_for('login'))
    
    return render_template('login.html') 


# Cadastro
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Todos os campos são obrigatórios!")
            return redirect(url_for('cadastrar'))

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute('''
                INSERT INTO usuarios (email, password)
                VALUES (?, ?)
            ''', (email, password))
            conexao.commit()
            conexao.close()
            flash("Cadastro realizado com sucesso!")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Erro: Email já cadastrado.")
            return redirect(url_for('cadastrar'))
    return render_template('cadastro.html')


if __name__ == '__main__':
    app.run(debug=True)