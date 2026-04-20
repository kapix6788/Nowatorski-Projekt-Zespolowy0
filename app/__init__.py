from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.client import bp as client_bp
    app.register_blueprint(client_bp, url_prefix='/client')

    from app.reception import bp as reception_bp
    app.register_blueprint(reception_bp, url_prefix='/reception')

    from app.mechanic import bp as mechanic_bp
    app.register_blueprint(mechanic_bp, url_prefix='/mechanic')

    from app.boss import bp as boss_bp
    app.register_blueprint(boss_bp, url_prefix='/boss')

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    return app
