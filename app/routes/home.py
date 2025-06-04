from flask import render_template
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def home():
    # Try to get user identity, but don't require it
    user = None
    try:
        verify_jwt_in_request(optional=False)
        user = get_jwt_identity()
    except:
        pass

    return render_template('home.html', user=user)
