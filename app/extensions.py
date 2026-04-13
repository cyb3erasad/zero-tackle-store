from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

# Initialize extensions without binding to app yet.
# They will be wired to the app inside create_app() via init_app().

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Redirect unauthorized users to the login page
login_manager.login_view = 'auth.login'

# Flash message shown when a login is required
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'