from datetime import datetime 


from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy() # stored as object

class User(UserMixin, db.Model):
    __tablename__ = "users" 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) # to store unique email 
    password_hash = db.Column(db.String(255), nullable=False) # password hash 
    role = db.Column(db.String(50), nullable=False, default='user') # define role 
    contact_details = db.Column(db.String(255),) # to store contact details
    department = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

     

    

