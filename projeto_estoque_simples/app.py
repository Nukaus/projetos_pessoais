from flask import Flask, render_template, request, jsonify, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'goblin'

def conectar_banco():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="1346",
        database="db_estoque"
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome-cadastro']
        email = request.form['email-cadastro']
        senha = request.form['senha-cadastro']
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        senha_hash_str = senha_hash.decode('utf-8')

        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cadastro (nome, email, senha) VALUES (%s, %s, %s)', (nome, email,  senha_hash_str))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template("cadastro.html")
    else:
        return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        email = request.form['email-login']
        senha = request.form['senha-login']

        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute('SELECT nome, senha FROM cadastro WHERE email = %s', (email,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            nome, senha_hash = resultado
            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                session['usuario'] = nome
                return render_template("estoque.html")
            else:
                return "Senha incorreta", 401
        else:
            return "Usuário não encontrado", 404
    else:
        return render_template('login.html')


@app.route('/adicionar', methods=['POST'])
def adicionar_usuario():
    dados = request.get_json()

    produto = dados['produto']
    quantidade = int(dados['quantidade'])
    preco = float(dados['preco'])
    preco_total = quantidade * preco

    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Verifica se o produto já existe
    cursor.execute("SELECT id FROM produtos WHERE produto = %s", (produto,))
    resultado = cursor.fetchone()

    if resultado:
        # Produto existe → Atualiza
        id_existente = resultado[0]
        cursor.execute("""
                UPDATE produtos
                SET quantidade = %s, preco_unitario = %s, preco = %s
                WHERE id = %s
            """, (quantidade, preco, preco_total, id_existente))
        novo_id = id_existente
    else:
        cursor.execute("""
            INSERT INTO produtos (produto, quantidade, preco_unitario, preco)
            VALUES (%s, %s, %s, %s)
        """, (produto, quantidade, preco, preco_total))
        novo_id = cursor.lastrowid
    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({
        "sucesso": True,
        "id": novo_id,
        "produto": produto,
        "quantidade": quantidade,
        "preco": preco,
        "preco_final": preco_total
    })

    
@app.route('/excluir/<int:id>', methods=['DELETE'])
def excluir_usuario(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))
    conexao.commit()

    sucesso = cursor.rowcount > 0

    cursor.close()
    conexao.close()

    return jsonify({ "sucesso": sucesso })

@app.route("/estoque")
def estoque():
    return render_template("estoque.html.html")
    
if __name__ == "__main__":
    app.run(debug=True)