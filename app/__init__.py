from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'

@login_manager.user_loader
def load_user(id):
    from .models.user import User
    return User.query.get(int(id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    from .routes import main, chat, agent, rpa, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(agent.bp)
    app.register_blueprint(rpa.bp)
    app.register_blueprint(auth.bp)
    
    return app 