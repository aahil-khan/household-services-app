from .database import db


class User(db.Model):
    __tablename__ = 'Users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('Services.id' , ondelete = 'CASCADE'), nullable=True)
    service_name = db.Column(db.String, nullable = True)
    service_category = db.Column(db.String, nullable = True)
    experience = db.Column(db.Integer, nullable=True)
    approval_status = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    contact = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String, nullable=True)
    pincode = db.Column(db.Integer, nullable=True)
    
    __table_args__ = (
    db.CheckConstraint("role IN ('admin', 'customer', 'professional')"),
    )


class ServiceRequest(db.Model):
    __tablename__ = 'Services_requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey('Services.id', ondelete = 'CASCADE'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Users.id' , ondelete = 'CASCADE'), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('Users.id' , ondelete = 'CASCADE'), nullable=True)
    professional_name = db.Column(db.String, nullable=True)
    date_of_request = db.Column(db.String, nullable=True)
    date_of_completion = db.Column(db.String, nullable=True)
    status = db.Column(db.String, default='requested')
    remarks = db.Column(db.String, nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    __table_args__ = (
    db.CheckConstraint("status IN ('requested', 'assigned', 'closed')"),
    )


class Service(db.Model):
    __tablename__ = 'Services'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String, nullable=True)
    category = db.Column(db.String, nullable=False)