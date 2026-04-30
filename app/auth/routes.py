from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import bp
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Nieprawidłowa nazwa użytkownika lub hasło.', 'error')
            return redirect(url_for('auth.login'))
        login_user(user)
        
        if user.role == 'szef':
            return redirect(url_for('boss.reports'))
        elif user.role == 'mechanik':
            return redirect(url_for('mechanic.my_orders'))
        elif user.role == 'recepcja':
            return redirect(url_for('reception.orders'))
        else:
            return redirect(url_for('client.my_garage'))

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    logout_user()
    flash('Zostałeś wylogowany.', 'success')
    return redirect(url_for('index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Login lub email są już zajęte.', 'error')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, role='klient',
                    first_name=request.form.get('first_name'), last_name=request.form.get('last_name'))
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Rejestracja przebiegła pomyślnie. Możesz się zalogować.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')