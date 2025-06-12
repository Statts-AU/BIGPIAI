from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager  # Import JWTManager
from .routes.upload_phase2 import upload_phase2
from .routes.upload_phase1 import upload_phase1
from .routes.home import home  # Import your home route
from .routes.login import login  # Import your login route
from .routes.logout import logout  # Import your logout route
from flask_socketio import SocketIO
from .routes.socket_manager import createSocketManager

socketio = SocketIO(cors_allowed_origins="*")


def create_app():

    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Add these two lines to set the secret keys
    # Required for sessions/flash messages
    app.secret_key = 'dev-secret-key-change-in-production'
    # For JWT tokens
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'

    # Other JWT configurations
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # For simplicity
    JWTManager(app)  # Initialize JWTManager with your app

    # Register routes
    app.add_url_rule('/', view_func=home)  # Add the home route
    app.add_url_rule('/upload-phase1', view_func=upload_phase1,
                     methods=['POST'])  # Add the upload route
    app.add_url_rule('/upload-phase2', view_func=upload_phase2,
                     methods=['POST'])  # Add the upload route
    app.add_url_rule('/login', view_func=login,
                     methods=['GET', 'POST'])  # Add the login route
    app.add_url_rule('/logout', view_func=logout)  # Add the logout route

    createSocketManager(socketio=socketio)
    socketio.init_app(app)
    return app
