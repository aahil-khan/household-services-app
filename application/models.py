from .database import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id' , ondelete = 'CASCADE'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('service_category.id' , ondelete = 'CASCADE'), nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    approval_status = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    contact = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String, nullable=True)
    pincode = db.Column(db.Integer, nullable=True)
    
    __table_args__ = (
    db.CheckConstraint("role IN ('admin', 'customer', 'professional')"),
    )


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('service_category.id'))


class ServiceCategory(db.Model):
    __tablename__ = 'service_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)


class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    servicereq_id = db.Column(db.Integer, db.ForeignKey('services_requests.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Add rating validation constraint
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 10', name='check_valid_rating'),
    )


class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    balance = db.Column(db.Float, default=10000.0)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Add balance constraint
    __table_args__ = (
        db.CheckConstraint('balance >= 0', name='check_positive_balance'),
    )


class Coupon(db.Model):
    __tablename__ = 'coupon'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_percent = db.Column(db.Float, nullable=False)
    valid_from = db.Column(db.DateTime)
    valid_to = db.Column(db.DateTime)
    max_uses = db.Column(db.Integer)
    current_uses = db.Column(db.Integer, default=0)


class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id' , ondelete = 'CASCADE'), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id' , ondelete = 'CASCADE'), nullable=True)
    servicereq_id = db.Column(db.Integer, db.ForeignKey('services_requests.id' , ondelete = 'CASCADE'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


class ServiceRequest(db.Model):
    __tablename__ = 'services_requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete = 'CASCADE'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id' , ondelete = 'CASCADE'), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id' , ondelete = 'CASCADE'), nullable=True)
    date_of_request = db.Column(db.String, nullable=True)
    date_of_completion = db.Column(db.String, nullable=True)
    status = db.Column(db.String, default='requested')

    service = db.relationship('Service', backref='service_requests', foreign_keys=[service_id])

    __table_args__ = (
    db.CheckConstraint("status IN ('requested', 'assigned', 'closed')"),
    )