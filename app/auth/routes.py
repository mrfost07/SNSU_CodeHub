from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.models import User
from werkzeug.urls import url_parse

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        try:
            # Check if username or email already exists
            if User.query.filter_by(username=request.form['username']).first():
                flash('Username already exists. Please choose another one.', 'danger')
                return redirect(url_for('auth.register'))
            
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email already registered. Please use another email.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Create new user
            user = User(
                username=request.form['username'],
                email=request.form['email']
            )
            user.set_password(request.form['password'])
            
            # Add and commit to database
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login with your credentials.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
            
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
