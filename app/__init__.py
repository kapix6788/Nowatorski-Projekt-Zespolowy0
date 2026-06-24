from flask import Flask, redirect, url_for
from app.extensions import db, login_manager, migrate
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp.'
    migrate.init_app(app, db)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.boss import bp as boss_bp
    app.register_blueprint(boss_bp, url_prefix='/boss')

    from app.reception import bp as reception_bp
    app.register_blueprint(reception_bp, url_prefix='/reception')

    from app.mechanic import bp as mechanic_bp
    app.register_blueprint(mechanic_bp, url_prefix='/mechanic')

    from app.client import bp as client_bp
    app.register_blueprint(client_bp, url_prefix='/client')

    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == 'szef':
                return redirect(url_for('boss.employees'))
            elif current_user.role == 'recepcja':
                return redirect(url_for('reception.orders'))
            elif current_user.role == 'mechanik':
                return redirect(url_for('mechanic.my_orders'))
            else:
                return redirect(url_for('client.my_garage'))
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()

    return app
