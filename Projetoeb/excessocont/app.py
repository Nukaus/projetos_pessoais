from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Inicializar o banco de dados
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Coleta dados do formulário
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']

        # Inserir dados no banco
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO people (name, age, email) VALUES (?, ?, ?)', (name, age, email))
        conn.commit()
        conn.close()

        return redirect('/')

    # Exibe os dados já cadastrados
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM people')
    people = cursor.fetchall()
    conn.close()

    return render_template('index.html', people=people)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
