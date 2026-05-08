from flask import Flask
import os
from config import Config
from routes.auth import auth_bp
from routes.api import api_bp
from routes.views import views_bp
from services.logging_service import LoggingService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    LoggingService.setup_logging()
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)
    
    return app

app = create_app()

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)