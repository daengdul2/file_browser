from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.abspath('./uploads')
    app.secret_key = 'inikuncirahasia'

    from .routes import main
    app.register_blueprint(main)

    return app
