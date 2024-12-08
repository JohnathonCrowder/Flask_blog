from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from sqlalchemy import func
from .models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Convert the email to lowercase for case-insensitive comparison
        user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.user_dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email').lower()  # Convert to lowercase before storing
        password = request.form.get('password')
        
        if User.query.filter(func.lower(User.email) == email).first():
            flash('Email already exists')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))