import secrets
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Secret key used for signing session cookies and flash messages.
# Generated securely using Python's secrets module.
# For production, set this via an environment variable instead of hardcoding it.
app.config['SECRET_KEY'] = secrets.token_hex(32)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------- MODEL ----------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'


# Create tables and instance folder automatically
with app.app_context():
    db.create_all()


# ---------------- CREATE + READ ----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        course = request.form.get('course')
        age = request.form.get('age')

        if not name or not email or not course or not age:
            flash('All fields are required!', 'danger')
            return redirect(url_for('index'))

        new_student = Student(name=name, email=email, course=course, age=age)
        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Student registered successfully!', 'success')
        except Exception:
            db.session.rollback()
            flash('Error: Email already exists or invalid data.', 'danger')

        return redirect(url_for('index'))

    students = Student.query.all()
    return render_template('index.html', students=students)


# ---------------- UPDATE ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.name = request.form.get('name')
        student.email = request.form.get('email')
        student.course = request.form.get('course')
        student.age = request.form.get('age')

        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
        except Exception:
            db.session.rollback()
            flash('Error updating student.', 'danger')

        return redirect(url_for('index'))

    students = Student.query.all()
    return render_template('index.html', students=students, edit_student=student)


# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)