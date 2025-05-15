from flask import redirect, url_for

def logout():
    response = redirect(url_for('home'))
    response.delete_cookie('access_token_cookie')
    return response 