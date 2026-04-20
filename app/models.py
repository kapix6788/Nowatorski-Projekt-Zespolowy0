from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False) # 'szef', 'recepcja', 'mechanik', 'klient'
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)
    mechanic_orders = db.relationship('RepairOrder', foreign_keys='RepairOrder.mechanic_id', backref='mechanic', lazy=True)
    part_requests = db.relationship('PartRequest', backref='mechanic', lazy=True)
    notes = db.relationship('RepairNote', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    year = db.Column(db.Integer)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    vin = db.Column(db.String(17), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    orders = db.relationship('RepairOrder', backref='vehicle', lazy=True, cascade='all, delete-orphan')

class RepairOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='oczekujace')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship('User', foreign_keys=[client_id], backref='client_orders')
    parts_used = db.relationship('OrderPart', backref='repair_order', lazy=True, cascade='all, delete-orphan')
    services_used = db.relationship('OrderService', backref='repair_order', lazy=True, cascade='all, delete-orphan')
    part_requests = db.relationship('PartRequest', backref='repair_order', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('RepairNote', backref='repair_order', lazy=True, cascade='all, delete-orphan')

class ServiceCatalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    order_services = db.relationship('OrderService', backref='service', lazy=True)

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    stock_quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    order_parts = db.relationship('OrderPart', backref='part', lazy=True)

class OrderPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repair_order_id = db.Column(db.Integer, db.ForeignKey('repair_order.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

class OrderService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repair_order_id = db.Column(db.Integer, db.ForeignKey('repair_order.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service_catalog.id'), nullable=False)
    price_applied = db.Column(db.Numeric(10, 2), nullable=False)

class PartRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    repair_order_id = db.Column(db.Integer, db.ForeignKey('repair_order.id'), nullable=False)
    part_name = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='oczekuje')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RepairNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repair_order_id = db.Column(db.Integer, db.ForeignKey('repair_order.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    requires_parts = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
