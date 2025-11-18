from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(200), nullable=False)
    is_vip = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    items = db.Column(db.Text)  # JSON: [{"id":1, "qty":2}, ...]
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Integer, default=1)  # 1=Confirmed, 2=Preparing, 3=Cooking, 4=Ready
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # "YYYY-MM-DD"
    time = db.Column(db.String(5), nullable=False)   # "HH:MM"
    is_premium_slot = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())