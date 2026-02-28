from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "earning_pro_ultra_secure_101"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///earningpro.db'
db = SQLAlchemy(app)

# --- Database Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='unpaid') # unpaid, pending, active
    tid = db.Column(db.String(50))
    referral_code = db.Column(db.String(20), unique=True)
    referred_by = db.Column(db.String(20))

with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        ref = request.form.get('ref')
        
        if User.query.filter_by(email=email).first():
            flash("Email already exists!")
            return redirect(url_for('register'))
            
        new_user = User(email=email, password=password, referred_by=ref, referral_code=email.split('@')[0])
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('payment'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("Invalid Credentials!")
    return render_template('login.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session: return redirect(url_for('login'))
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
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.status != 'active': return redirect(url_for('waiting'))
    return render_template('dashboard.html', user=user)

# --- Video Task Logic (Security) ---
@app.route('/complete_task', methods=['POST'])
def complete_task():
    if 'user_id' not in session: return jsonify({"status": "error"}), 403
    user = User.query.get(session['user_id'])
    # Yahan hum check kar sakte hain ke 30 sec guzray ya nahi
    user.balance += 0.50
    db.session.commit()
    return jsonify({"status": "success", "new_balance": user.balance})

# --- Admin Routes ---
@app.route('/admin/panel')
def admin_panel():
    # Sirf pending users dikhayega
    users = User.query.filter_by(status='pending').all()
    return render_template('admin.html', users=users)

@app.route('/admin/approve/<int:id>')
def approve_user(id):
    user = User.query.get(id)
    if user:
        user.status = 'active'
        # Referral Bonus ($1)
        if user.referred_by:
            boss = User.query.filter_by(referral_code=user.referred_by).first()
            if boss: boss.balance += 1.0
        db.session.commit()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True, port=8158)
    
