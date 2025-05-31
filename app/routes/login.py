from flask import request, render_template, redirect, url_for, flash
from flask_jwt_extended import create_access_token
from ..user_data import users  # Import the users list


def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)

        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('login'))

        user = None
        for userModel in users:
            if userModel['username'] == username:
                user = userModel

        if not user or password != user['password']:
            flash('Invalid credentials')
            return redirect(url_for('login'))

        # Create JWT token and set in cookie
        token = create_access_token(identity=username)
        response = redirect(url_for('home'))
        response.set_cookie('access_token_cookie', token)
        return response
