from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from routes.analyze import analyze_bp
from routes.download import download_bp
from routes.caption import caption_bp
from routes.proxy import proxy_bp

def create_app():
    app = Flask(__name__)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per hour", "20 per minute"],
        storage_uri="memory://"
    )

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    app.config['DOWNLOAD_FOLDER'] = '/tmp/clip_grabber_cache'

    import os
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

    app.register_blueprint(analyze_bp, url_prefix='/api')
    app.register_blueprint(download_bp, url_prefix='/api')
    app.register_blueprint(caption_bp, url_prefix='/api')
    app.register_blueprint(proxy_bp, url_prefix='/api')

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Endpoint not found"}, 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return {"error": "Rate limit exceeded. Please slow down."}, 429

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal server error"}, 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
