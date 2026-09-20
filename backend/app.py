import logging
import os
import sys

from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

from config import DOWNLOAD_FOLDER, CORS_ORIGIN, JOB_MAX_AGE_SECONDS
from extensions import limiter
from routes.analyze import analyze_bp
from routes.download import download_bp
from routes.caption import caption_bp
from routes.proxy import proxy_bp
from services import job_store
from services.ytdlp_service import cleanup_old_files

logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    cors_origins = CORS_ORIGIN.split(',') if CORS_ORIGIN != '*' else '*'
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    limiter.init_app(app)

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    job_store.init_db()

    app.register_blueprint(analyze_bp, url_prefix='/api')
    app.register_blueprint(download_bp, url_prefix='/api')
    app.register_blueprint(caption_bp, url_prefix='/api')
    app.register_blueprint(proxy_bp, url_prefix='/api')

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'}), 200

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Endpoint not found"}, 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return {"error": "Rate limit exceeded. Please slow down."}, 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception('Unhandled server error')
        return {"error": "Internal server error"}, 500

    def _run_cleanup():
        try:
            cleanup_old_files(max_age_seconds=JOB_MAX_AGE_SECONDS)
            job_store.cleanup_old_jobs(max_age_seconds=JOB_MAX_AGE_SECONDS)
        except Exception:
            logger.exception('Scheduled cleanup failed')

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(_run_cleanup, 'interval', minutes=15, next_run_time=None)
    scheduler.start()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
