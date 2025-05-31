from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Create database and table
conn = sqlite3.connect('students.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT NOT NULL,
        section TEXT,
        marks INTEGER,
        dob TEXT,
        added_on TEXT
    )
''')
conn.close()

# Home route with sorting
@app.route('/')
def index():
    sort = request.args.get('sort', 'last')  # default sort

    if sort == 'name':
        order_clause = 'name COLLATE NOCASE'
    elif sort == 'roll':
        order_clause = 'roll'
    else:
        order_clause = 'id DESC'  # last inserted

    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    students = conn.execute(f'SELECT * FROM students ORDER BY {order_clause}').fetchall()
    conn.close()

    return render_template('index.html', students=students, sort=sort)

# Add student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        section = request.form.get('section')
        marks = request.form.get('marks')
        dob = request.form.get('dob')

        if not name or not roll:
            return render_template('add.html', error='Name and Roll are required.', name=name, roll=roll, section=section, marks=marks, dob=dob)

        added_on = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect('students.db')
        conn.execute('INSERT INTO students (name, roll, section, marks, dob, added_on) VALUES (?, ?, ?, ?, ?, ?)',
                     (name, roll, section, marks, dob, added_on))
        conn.commit()
        conn.close()

        return render_template('success.html')

    return render_template('add.html')

# Edit student
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        section = request.form.get('section')
        marks = request.form.get('marks')
        dob = request.form.get('dob')

        if not name or not roll:
            error = 'Name and Roll are required.'
            student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
            return render_template('edit.html', student=student, error=error)

        conn.execute('''
            UPDATE students 
            SET name = ?, roll = ?, section = ?, marks = ?, dob = ?
            WHERE id = ?
        ''', (name, roll, section, marks, dob, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # GET method
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()
    if student is None:
        return "Student not found", 404
    return render_template('edit.html', student=student)

# Search student by roll number
@app.route('/search', methods=['GET', 'POST'])
def search():
    student = None
    error = None
    if request.method == 'POST':
        roll = request.form['roll']
        conn = sqlite3.connect('students.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM students WHERE roll = ?', (roll,))
        student = cur.fetchone()
        conn.close()

        if not student:
            error = 'Student not found.'

    return render_template('search.html', student=student, error=error)

# Delete student by ID
@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    conn = sqlite3.connect('students.db')
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
