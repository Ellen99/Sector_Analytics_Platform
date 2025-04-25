import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    print("frontend_origin", )
    CORS(app, resources={r"/api/*": {"origins": frontend_origin}})
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app