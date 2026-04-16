from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.auth import auth_bp
from app.auth.forms import SignupForm, LoginForm
from app.models import User, Cart
from app.extensions import db


# ======================================================================
# SIGNUP
# ======================================================================

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    form = SignupForm()

    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)

        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            password=hashed_pw,
            is_admin=False
        )
        db.session.add(user)
        db.session.flush()   # get user.id before commit

        # Create an empty cart for the new user immediately
        cart = Cart(user_id=user.id)
        db.session.add(cart)

        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('products.index'))

    return render_template('auth/signup.html', form=form)


# ======================================================================
# LOGIN
# ======================================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data.strip().lower()
        ).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.username}!', 'success')

            # Respect ?next= redirect param (Flask-Login sets this)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # For now redirect to login until products blueprint is built
            # Will be updated to products.index in Step 4
            return redirect(url_for('products.index'))

        flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)


# ======================================================================
# LOGOUT
# ======================================================================

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('products.index'))