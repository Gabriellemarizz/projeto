from flask import Flask, render_template, url_for, request, redirect
import sqlite3, os.path
from models import User
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_required, login_user, logout_user

app = Flask(__name__)
DATABASE = 'database.db'

mysql = MySQL(app)
app.config['SECRET_KEY'] = 'muitodificil'

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    conn = get_connection()
    usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.commit() 
    conn.close()
    return render_template('pages/index.html', usuarios=usuarios)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['pass']
        user = User.get_by_email(email)
        if user and user.senha == senha:
            login_user(user)
            return render_template('pages/categorias.html')

    return render_template('pages/login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['pass']
        conexao = get_connection()
        INSERT = 'INSERT INTO usuarios(email,senha) VALUES (?,?)'
        conexao.execute(INSERT, (email, senha))
        conexao.commit()
        conexao.close()
        return redirect(url_for('index'))
    return render_template('pages/cadastro.html')


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_tarefa():
    categoria = request.args.get('categorias')
    if request.method == 'POST':
        titulo = request.form['nome']
        conteudo = request.form['conteudo']
        conn = get_connection()
        conn.execute("INSERT INTO tarefas(titulo, conteudo, categorias) VALUES(?,?,?)", (titulo, conteudo, categoria))
        conn.commit()
        conn.close()
        return redirect(url_for('ver_tarefa'))
    return render_template('pages/criar-tarefa.html', categoria=categoria)

@app.route('/tarefas', methods=['GET'])
@login_required
def ver_tarefa():
    categoria = request.args.get('categorias')
    conn = get_connection()
    tarefas = conn.execute("SELECT * FROM tarefas WHERE categorias = ?", (categoria,)).fetchall()
    conn.commit()
    conn.close()
    
    return render_template('pages/tarefas.html', tarefas=tarefas, categoria=categoria)

@app.route('/escolher_categoria', methods=['GET', 'POST'])
@login_required
def escolher_categoria():
    if request.method == 'POST':
        categoria = request.form['categorias']
        return redirect(url_for('create_tarefa', categoria=categoria))
    
    return render_template('pages/tarefas.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    conn = get_connection()
    conn.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_tarefa'))