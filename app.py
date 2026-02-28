from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "earnpro_v3_secure"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///earnpro.db'
db = SQLAlchemy(app)

# User Table Structure
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='unpaid') # unpaid, pending, active
    tid = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['email'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('payment'))
    return render_template('register.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session: return redirect(url_for('register'))
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.tid = request.form['tid']
        user.status = 'pending'
        db.session.commit()
        return redirect(url_for('waiting'))
    return render_template('payment.html')

@app.route('/waiting')
def waiting():
    return render_template('waiting.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('register'))
    user = User.query.get(session['user_id'])
    if user.status != 'active': return redirect(url_for('waiting'))
    return render_template('dashboard.html', user=user)

# --- Admin Function (Account Activate Karne ke liye) ---
@app.route('/admin/approve/<int:uid>')
def approve(uid):
    user = User.query.get(uid)
    user.status = 'active'
    db.session.commit()
    return f"User {user.username} activated!"

if __name__ == '__main__':
    app.run(debug=True, port=8158)
  
