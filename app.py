from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User


app = Flask(__name__)


app.config['SECRET_KEY'] = 'dev-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///examination_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)

