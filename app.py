import os
from flask import Flask , request, redirect
from flask import render_template
from application.models import User, Service , ServiceRequest, ServiceCategory, Review, Coupon, Wallet, Payment
from application.database import db
from application.api import *
from flask_restful import Api
from datetime import datetime



current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder="templates")
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir , "database/household-services-app.db")

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:pgadmin@localhost/household-services-app'

db.init_app(app)
app.app_context().push()



@app.route("/", methods=["GET", "POST"])
def hello_world():
    users = User.query.all()
    return render_template("index.html", users = users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html" , test="get")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
       
        if user is not None:
            if user.password == password:

                if(user.role == "admin"):
                    return redirect("/admin_dashboard")
                elif(user.role == "professional"):
                    return redirect("/professional_dashboard/" + str(user.id))
                else:
                    return redirect("/customer_dashboard/" + str(user.id))
            else:
                return render_template("login.html", message="Invalid email or password")
        else:
            return render_template("login.html", message="No user found with this email")
        
@app.route("/register_customer", methods=["GET", "POST"])
def register_customer():
    if request.method == "GET":
        return render_template("customer_signup.html")
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user is not None:
            return render_template("customer_signup.html", message="User with this email already exists")
        password = request.form.get("password")

        address = request.form.get("address")
        pincode = request.form.get("pin_code")
        user = User(name=name, email=email, password=password,address=address, pincode=pincode, role="customer")
        db.session.add(user)
        db.session.flush()

        wallet = Wallet(user_id=user.id, balance=10000.0)
        db.session.add(wallet)

        db.session.commit()
        return redirect("/customer_dashboard/" + str(user.id))
    
@app.route("/register_professional", methods=["GET", "POST"])
def register_professional():
    if request.method == "GET":
        service_categories = ServiceCategory.query.all()
        return render_template("professional_signup.html" , service_categories=service_categories)
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user is not None:
            return render_template("professional_signup.html", message="User with this email already exists")
        password = request.form.get("password")
        address = request.form.get("address")
        pincode = request.form.get("pin_code")
        experience = request.form.get("experience")
        contact = request.form.get("contact")
        service_type = request.form.get("service_type")
        category_id = ServiceCategory.query.filter_by(name=service_type).first().id

        #service_id = ServiceCategory.query.filter_by(category=service_type).first().id
        #service_name = Service.query.filter_by(id=service_id).first().name

        user = User(name=name, email=email, password=password,address=address, pincode=pincode, role="professional", experience=experience, contact=contact, category_id = category_id,approval_status = "waiting")
        db.session.add(user)
        db.session.flush()

        wallet = Wallet(user_id=user.id, balance=0.0)
        db.session.add(wallet)

        db.session.commit()
        return redirect("/professional_dashboard/" + str(user.id))
    
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    services = db.session.query(Service, ServiceCategory).join(
        ServiceCategory, Service.category_id == ServiceCategory.id
    ).add_columns(
        Service.id, Service.name, Service.base_price, Service.time_required, 
        Service.description, ServiceCategory.name.label("category")
    ).all()

    professionals = User.query.filter_by(role="professional").all()

    professionals = db.session.query(User, ServiceCategory, Service).join(
        ServiceCategory, User.category_id == ServiceCategory.id
    ).outerjoin(
        Service, User.service_id == Service.id
    ).filter(User.role == "professional").add_columns(
        User.id, User.name, User.email, User.address, User.pincode, 
        User.experience, User.contact, User.approval_status, 
        ServiceCategory.name.label("service_category"), 
        Service.name.label("service_name")
    ).all()

    service_requests = ServiceRequest.query.all()
    for srequest in service_requests:
        srequest.professional_name = User.query.filter_by(id=srequest.professional_id).first().name
        srequest.customer_name = User.query.filter_by(id=srequest.customer_id).first().name
        srequest.service_name = Service.query.filter_by(id=srequest.service_id).first().name
        srequest.review = Review.query.filter_by(servicereq_id=srequest.id).first().comment

    coupons = Coupon.query.all()

    payments = Payment.query.all()
    for payment in payments:
        payment.customer_name = User.query.filter_by(id=payment.customer_id).first().name
        payment.professional_name = User.query.filter_by(id=payment.professional_id).first().name
        payment.service_name = ServiceRequest.query.filter_by(id=payment.servicereq_id).first().service.name

    users = User.query.filter_by(role="customer").all()
    return render_template("admin_dashboard.html", services=services, professionals=professionals, service_requests=service_requests, role=request.args.get("role") , customers=users , coupons=coupons , payments=payments)

@app.route("/admin_dashboard/create_service", methods=["GET", "POST"])
def create_service():
    if request.method == "GET":
        professionals = User.query.filter_by(role="professional").all()
        service_categories = ServiceCategory.query.all()
        return render_template("create_service.html" , professionals=professionals, service_categories=service_categories)
    else:
        name = request.form.get("name")
        base_price = request.form.get("base_price")
        time_required = request.form.get("time_required")
        description = request.form.get("description")
        category = request.form.get("category")
        categoryid = ServiceCategory.query.filter_by(name=category).first().id

        # professional_id = request.form.get("professional_id")
        service = Service(name=name, base_price=base_price, time_required=time_required , description=description , category_id=categoryid)
        db.session.add(service)
        db.session.commit()
        return redirect("/admin_dashboard")

@app.route("/admin_dashboard/create_coupon", methods=["GET", "POST"])
def create_coupon():
    if request.method == "GET":
        return render_template("create_coupon.html")
    else:
        code = request.form.get("code")
        discount = request.form.get("discount")
        valid_from = request.form.get("valid_from")
        valid_to = request.form.get("valid_to")
        valid_from = datetime.strptime(valid_from, "%Y-%m-%d").date()
        valid_to = datetime.strptime(valid_to, "%Y-%m-%d").date()
        if valid_from > valid_to:
            return render_template("create_coupon.html", message="Invalid date range")
        max_uses = request.form.get("max_uses")
        coupon = Coupon(code=code, discount_percent=discount, valid_from=valid_from, valid_to=valid_to, max_uses=max_uses)
        db.session.add(coupon)
        db.session.commit()
        return redirect("/admin_dashboard")

@app.route("/admin_dashboard/edit_coupon/<int:id>", methods=["GET", "POST"])
def edit_coupon(id):
    if request.method == "GET":
        coupon = Coupon.query.filter_by(id=id).first()
        if coupon is not None:
            return render_template("edit_coupon.html", coupon=coupon)
        else:
            return redirect("/admin_dashboard")
    else:
        code = request.form.get("code")
        discount = request.form.get("discount")
        valid_from = request.form.get("valid_from")
        valid_to = request.form.get("valid_to")
        valid_from = datetime.strptime(valid_from, "%Y-%m-%d").date()
        valid_to = datetime.strptime(valid_to, "%Y-%m-%d").date()
        if valid_from > valid_to:
            return render_template("create_coupon.html", message="Invalid date range")
        max_uses = request.form.get("max_uses")
        coupon = Coupon.query.filter_by(id=id).first()
        coupon.code = code
        coupon.discount_percent = discount
        coupon.valid_from = valid_from
        coupon.valid_to = valid_to
        coupon.max_uses = max_uses
        db.session.commit()
        return redirect("/admin_dashboard")


@app.route("/admin_dashboard/edit_service/<int:id>", methods=["GET", "POST"])
def edit_service(id):
    if request.method == "GET":
        service = Service.query.filter_by(id=id).first()
        if service is not None:
            return render_template("edit_service.html", service=service)
        else:
            return redirect("/admin_dashboard")
    else:
        name = request.form.get("name")
        base_price = request.form.get("base_price")
        time_required = request.form.get("time_required")
        description = request.form.get("description")
        service = Service.query.filter_by(id=id).first()
        service.name = name
        service.base_price = base_price
        service.time_required = time_required
        service.description = description
        db.session.commit()
        return redirect("/admin_dashboard")


@app.route("/admin_dashboard/search", methods=["GET", "POST"])
def admin_dashboard_search():
    if request.method == "GET":
        return render_template("admin_dashboard_search.html")
    else:
        search = request.form.get("search")
        search_type = request.form.get("search_type")
        service_requests = ['empty']
        services = ['empty']
        services_data = Service.query.all()
        customers = ['empty']
        professionals = ['empty']
        if search_type == "service_request":
            service_requests = ServiceRequest.query.filter(ServiceRequest.professional_name.like("%" + search + "%")).all()
            for req in service_requests:
                req.customer_name = User.query.filter_by(id=req.customer_id).first().name
                req.service_name = Service.query.filter_by(id=req.service_id).first().name
        elif search_type == "service":
            services = Service.query.filter(Service.name.like("%" + search + "%")).all()
        elif search_type == "professional":
            customers = User.query.filter(User.name.like("%" + search + "%")).filter_by(role="professional").all()
        elif search_type == "customer":
            professionals = User.query.filter(User.name.like("%" + search + "%")).filter_by(role="customer").all()

        return render_template("admin_dashboard_search.html",searched='true',services_data=services_data, service_requests=service_requests, services=services, customers=customers, professionals=professionals)
    
@app.route("/professional_dashboard/<int:id>", methods=["GET", "POST"])
def professional_dashboard(id):
    user = User.query.filter_by(id=id).first()
    if user is None or user.role != "professional":
        return redirect("/login")

    open_service_requests = ServiceRequest.query.filter_by(status="requested").filter_by(professional_id=id).all()
    for request in open_service_requests:
        request.customer_name = User.query.filter_by(id=request.customer_id).first().name
        request.service_name = Service.query.filter_by(id=request.service_id).first().name

    assigned_service_requests = ServiceRequest.query.filter_by(status="assigned").filter_by(professional_id=id).all()
    for request in assigned_service_requests:
        request.customer_name = User.query.filter_by(id=request.customer_id).first().name
        request.service_name = Service.query.filter_by(id=request.service_id).first().name
    
    closed_service_requests = ServiceRequest.query.filter_by(status="closed").filter_by(professional_id=id).all()
    for request in closed_service_requests:
        request.customer_name = User.query.filter_by(id=request.customer_id).first().name
        request.service_name = Service.query.filter_by(id=request.service_id).first().name
        request.rating = Review.query.filter_by(servicereq_id=request.id).first().rating
        request.review = Review.query.filter_by(servicereq_id=request.id).first().comment

    wallet = Wallet.query.filter_by(user_id=id).first()

    return render_template("professional_dashboard.html",wallet=wallet, user=user, open_service_requests=open_service_requests , assigned_service_requests=assigned_service_requests , closed_service_requests=closed_service_requests)


@app.route("/customer_dashboard/<int:id>", methods=["GET", "POST"])
def customer_dashboard(id):
    user = User.query.filter_by(id=id).first()
    wallet = Wallet.query.filter_by(user_id=id).first()

    if user is None or user.role != "customer":
        return redirect("/login")
    categories = ServiceCategory.query.all()

    service_requests = ServiceRequest.query.filter_by(customer_id=id).all()
    for request in service_requests:
        request.service_name = Service.query.filter_by(id=request.service_id).first().name
        request.phone = User.query.filter_by(id=request.professional_id).first().contact
        request.professional_name = User.query.filter_by(id=request.professional_id).first().name

    return render_template("customer_dashboard.html", id = user.id , user =user, wallet = wallet, categories = categories , service_requests = service_requests)

@app.route("/customer_dashboard/<int:id>/<string:category>", methods=["GET", "POST"])
def customer_dashboard_category(id , category):
    user = User.query.filter_by(id=id).first()

    if user is None or user.role != "customer":
        return redirect("/login")
    
    category_id = ServiceCategory.query.filter_by(name=category).first().id
    
    services = Service.query.filter_by(category_id=category_id).join(
        User, Service.id == User.service_id
    ).filter(User.role == "professional").add_columns(
        Service.id, Service.name, Service.base_price, Service.time_required, 
        Service.description, User.name.label("professional_name"), User.id.label("professional_id")
    )
    
    service_requests = ServiceRequest.query.filter_by(customer_id=id).all()
    for request in service_requests:
        request.service_name = Service.query.filter_by(id=request.service_id).first().name
        request.phone = User.query.filter_by(id=request.professional_id).first().contact
        request.professional_name = User.query.filter_by(id=request.professional_id).first().name

    available_services = []
    for service in services:
        is_assigned = any(
            request.service_name == service.name and request.status == "assigned"
            for request in service_requests
        )
        is_requested = any(
            request.service_name == service.name and request.status == "requested"
            for request in service_requests
        )
        if not is_assigned and not is_requested:
            available_services.append(service)
    services = available_services

    wallet = Wallet.query.filter_by(user_id=id).first()
    return render_template("customer_dashboard_select.html",wallet = wallet, id = user.id,services = services, service_requests = service_requests)


@app.route("/customer_dashboard/search/<int:id>", methods=["GET", "POST"])
def customer_dashboard_search(id):
    user = User.query.filter_by(id=id).first()
    search_type = "name"

    if user is None or user.role != "customer":
        return redirect("/login")
    services = ['empty']
    if request.method == "POST":
        search = request.form.get("search")
        search_type = request.form.get("search_type")
        if search_type == "name":
            services = Service.query.filter(Service.name.contains(search)).all()
        elif search_type == "professional_name":
            services = []
            professionals = User.query.filter(User.name.contains(search)).all()
            for professional in professionals:
                services.extend(Service.query.filter_by(id=professional.service_id).all())

        booked_service_ids = [s.service_id for s in ServiceRequest.query.filter_by(customer_id=id).filter_by(status="assigned").filter_by(status="requested").all()]
        print(booked_service_ids)
        services = [s for s in services if s.id not in booked_service_ids]

    wallet = Wallet.query.filter_by(user_id=id).first()
    return render_template("customer_dashboard_search.html", id = user.id ,wallet = wallet, services = services , type = search_type)


@app.route("/professional_dashboard/search/<int:id>", methods=["GET", "POST"])
def professional_dashboard_search(id):
    user = User.query.filter_by(id=id).first()

    if user is None or user.role != "professional":
        return redirect("/login")
    
    services_requests = ['empty']
    if request.method == "POST":
        search = request.form.get("search")
        search_type = request.form.get("search_type")
        
        if search_type == "date":
            services_requests = ServiceRequest.query.filter(
                ServiceRequest.date_of_request.contains(search),
                ServiceRequest.professional_id == id
            ).all()
        elif search_type == "customer_name":
            services_requests = ServiceRequest.query.join(User, ServiceRequest.customer_id == User.id).filter(
                User.name.contains(search),
                ServiceRequest.professional_id == id
            ).all()
        for req in services_requests:
            req.customer_name = User.query.filter_by(id=req.customer_id).first().name
            req.contact = User.query.filter_by(id=req.customer_id).first().contact
    wallet = Wallet.query.filter_by(user_id=id).first()

    return render_template("professional_dashboard_search.html",wallet = wallet, user=user, services_requests=services_requests)

@app.route("/rate_service/<int:id>", methods=["GET", "POST"])
def rate_service(id):
    if request.method == "GET":
        service_request = ServiceRequest.query.filter_by(id=id).first()
        service_request.service_name = Service.query.filter_by(id=service_request.service_id).first().name
        service_request.phone = User.query.filter_by(id=service_request.professional_id).first().contact
        service_request.professional_name = User.query.filter_by(id=service_request.professional_id).first().name
        service_request.price = service_request.service.base_price
        message = request.args.get("message", "")
        return render_template("rate_service.html", service_request=service_request, message=message)
    else:
        rating = request.form.get("rating")
        remarks = request.form.get("remarks")
        coupon_code = request.form.get("coupon_code")
        if coupon_code == "":
            pass
        else:
            coupon = Coupon.query.filter_by(code=coupon_code).first()
            if coupon is not None:
                if coupon.valid_from > datetime.now() or coupon.valid_to < datetime.now():
                    return redirect("/rate_service/" + str(id) + "?message=Coupon code is not valid")
                coupon.current_uses += 1
                if coupon.max_uses == coupon.current_uses:
                    db.session.delete(coupon)
            else:
                return redirect("/rate_service/" + str(id) + "?message=Invalid coupon code")
            
        review = Review(servicereq_id=id, rating=rating, comment=remarks)
        db.session.add(review)
        db.session.flush()  # Ensure the review ID is generated

        #trigger?
        service_request = ServiceRequest.query.filter_by(id=id).first()
        service_request.status = "closed"
        service_request.date_of_completion = datetime.now().strftime("%d-%m-%y")
        
        #payment
        if coupon_code == "":
            price = service_request.service.base_price
        else:
            price = service_request.service.base_price - (service_request.service.base_price * coupon.discount_percent / 100)
            
        
        payment = Payment(customer_id=service_request.customer_id, professional_id=service_request.professional_id, amount=price , servicereq_id=service_request.id)
        db.session.add(payment)

        #update wallets
        wallet_customer = Wallet.query.filter_by(user_id=service_request.customer_id).first()
        wallet_professional = Wallet.query.filter_by(user_id=service_request.professional_id).first()

        wallet_customer.balance -= price
        wallet_professional.balance += price


        db.session.commit()
        return redirect("/customer_dashboard/" + str(service_request.customer_id))


api = Api(app)
api.add_resource(ServiceAPI,"/api/service/<int:id>")
api.add_resource(UserAPI,"/api/user/<int:id>")
api.add_resource(ProfessionalAPI,"/api/professional/<string:action>/<int:id>")
api.add_resource(ServiceRequestAPI,"/api/service_request/<int:id>" , "/api/service_request/<string:action>/<int:request_id>" , "/api/service_request/<int:customer_id>/<int:service_id>/<int:professional_id>")
api.add_resource(CouponAPI,"/api/coupon/<int:id>")

if __name__ == "__main__":
    app.run(debug=True, port = 5005)



