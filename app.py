from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "earning_pro_vercel_99"

# Vercel ke liye database path change karna zaroori hai
if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/earningpro.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///earningpro.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='unpaid') 
    tid = db.Column(db.String(50))
    referral_code = db.Column(db.String(20))

with app.app_context():
    db.create_all()

# --- Routes (Wahi rahengay jo pehle thay) ---
@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        user = User(email=email, password=request.form['password'], referral_code=email.split('@')[0])
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

# Vercel ko app export karni hoti hai
app = app 
    
