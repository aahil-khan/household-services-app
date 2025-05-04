from database import db

class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    # Relationship to Address
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.address_id'), nullable=True)
    address = db.relationship('Address', back_populates='customer')

    # Relationship to ServiceRequest (One-to-Many)
    service_requests = db.relationship('ServiceRequest', back_populates='customer')

class Professional(db.Model):
    __tablename__ = 'professionals'

    professional_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    skill = db.Column(db.String(50), nullable=True)
    last_assigned_date = db.Column(db.Date, nullable=True)

    # Relationship to ServiceRequest (One-to-Many)
    service_requests = db.relationship('ServiceRequest', back_populates='professional')

    # Relationship to Address
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.address_id'), nullable=True)
    address = db.relationship('Address', back_populates='professional')

class Service(db.Model):
    __tablename__ = 'services'

    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationship to ServiceRequest (One-to-Many)
    service_requests = db.relationship('ServiceRequest', back_populates='service')

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    request_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.professional_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    # Relationships
    customer = db.relationship('Customer', back_populates='service_requests')
    professional = db.relationship('Professional', back_populates='service_requests')
    service = db.relationship('Service', back_populates='service_requests')

class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_requests.request_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    method = db.Column(db.String(20), nullable=False)

    # Relationship
    service_request = db.relationship('ServiceRequest', back_populates='payments')

class Review(db.Model):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_requests.request_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    # Relationship
    service_request = db.relationship('ServiceRequest', back_populates='reviews')

class Address(db.Model):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)

    # Relationship back to Customer and Professional
    customer = db.relationship('Customer', back_populates='address', uselist=False)
    professional = db.relationship('Professional', back_populates='address', uselist=False)

# Define additional relationships for ServiceRequest, Payment, and Review tables
Customer.service_requests = db.relationship('ServiceRequest', back_populates='customer')
Professional.service_requests = db.relationship('ServiceRequest', back_populates='professional')
Service.service_requests = db.relationship('ServiceRequest', back_populates='service')
ServiceRequest.payments = db.relationship('Payment', back_populates='service_request')
ServiceRequest.reviews = db.relationship('Review', back_populates='service_request')

# Indexes for faster lookup
db.Index('idx_customer_email', Customer.email)
db.Index('idx_professional_email', Professional.email)
db.Index('idx_request_status', ServiceRequest.status)
