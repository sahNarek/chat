from flask import Flask
from api import v1
from api.v1.completions_controller import completions_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(v1.v1_bp)
    app.register_blueprint(completions_bp)

    return app