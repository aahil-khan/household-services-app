import os
from flask import Flask , request, redirect
from flask import render_template
from application.models import User, Service , ServiceRequest
from application.database import db
from application.api import *
from flask_restful import Api
from datetime import datetime



current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir , "database/household-services-app.db")

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
        db.session.commit()
        return redirect("/customer_dashboard/" + str(user.id))
    
@app.route("/register_professional", methods=["GET", "POST"])
def register_professional():
    if request.method == "GET":
        return render_template("professional_signup.html")
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

        # service_id = Service.query.filter_by(category=service_type).first().id
        # service_name = Service.query.filter_by(id=service_id).first().name

        user = User(name=name, email=email, password=password,address=address, pincode=pincode, role="professional", experience=experience, contact=contact, service_category = service_type ,approval_status = "waiting")
        db.session.add(user)
        db.session.commit()
        return redirect("/professional_dashboard/" + str(user.id))
    
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    services = Service.query.all()
    professionals = User.query.filter_by(role="professional").all()
    service_requests = ServiceRequest.query.all()
    users = User.query.filter_by(role="customer").all()
    return render_template("admin_dashboard.html", services=services, professionals=professionals, service_requests=service_requests, role=request.args.get("role") , customers=users)

@app.route("/admin_dashboard/create_service", methods=["GET", "POST"])
def create_service():
    if request.method == "GET":
        professionals = User.query.filter_by(role="professional").all()
        return render_template("create_service.html" , professionals=professionals)
    else:
        name = request.form.get("name")
        base_price = request.form.get("base_price")
        time_required = request.form.get("time_required")
        description = request.form.get("description")
        category = request.form.get("category")
        # professional_id = request.form.get("professional_id")
        service = Service(name=name, base_price=base_price, time_required=time_required , description=description , category=category)
        db.session.add(service)
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

    return render_template("professional_dashboard.html", user=user, open_service_requests=open_service_requests , assigned_service_requests=assigned_service_requests , closed_service_requests=closed_service_requests)


@app.route("/customer_dashboard/<int:id>", methods=["GET", "POST"])
def customer_dashboard(id):
    user = User.query.filter_by(id=id).first()

    if user is None or user.role != "customer":
        return redirect("/login")
    categories = Service.query.with_entities(Service.category).distinct().all()

    service_requests = ServiceRequest.query.filter_by(customer_id=id).all()
    
    for request in service_requests:
        request.service_name = Service.query.filter_by(id=request.service_id).first().name
        request.phone = User.query.filter_by(id=request.professional_id).first().contact

    return render_template("customer_dashboard.html", id = user.id , user =user,  categories = categories , service_requests = service_requests)

@app.route("/customer_dashboard/<int:id>/<string:category>", methods=["GET", "POST"])
def customer_dashboard_category(id , category):
    user = User.query.filter_by(id=id).first()

    if user is None or user.role != "customer":
        return redirect("/login")
    
    services = Service.query.filter_by(category=category).join(
        User, Service.id == User.service_id
    ).filter(User.role == "professional").add_columns(
        Service.id, Service.name, Service.base_price, Service.time_required, 
        Service.description, Service.category, User.name.label("professional_name"), User.id.label("professional_id")
    )
    
    service_requests = ServiceRequest.query.filter_by(customer_id=id).all()
    for request in service_requests:
        request.service_name = Service.query.filter_by(id=request.service_id).first().name
        request.phone = User.query.filter_by(id=request.professional_id).first().contact

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
    return render_template("customer_dashboard_select.html", id = user.id,services = services, service_requests = service_requests)


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

    return render_template("customer_dashboard_search.html", id = user.id , services = services , type = search_type)


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

    return render_template("professional_dashboard_search.html", user=user, services_requests=services_requests)

@app.route("/rate_service/<int:id>", methods=["GET", "POST"])
def rate_service(id):
    if request.method == "GET":
        service_request = ServiceRequest.query.filter_by(id=id).first()
        service_request.service_name = Service.query.filter_by(id=service_request.service_id).first().name
        service_request.phone = User.query.filter_by(id=service_request.professional_id).first().contact
        return render_template("rate_service.html", service_request=service_request)
    else:
        rating = request.form.get("rating")
        remarks = request.form.get("remarks")
        service_request = ServiceRequest.query.filter_by(id=id).first()
        service_request.rating = rating
        service_request.remarks = remarks
        service_request.status = "closed"
        service_request.date_of_completion = datetime.now().strftime("%d-%m-%y")
        db.session.commit()
        return redirect("/customer_dashboard/" + str(service_request.customer_id))


api = Api(app)
api.add_resource(ServiceAPI,"/api/service/<int:id>")
api.add_resource(UserAPI,"/api/user/<int:id>")
api.add_resource(ProfessionalAPI,"/api/professional/<string:action>/<int:id>")
api.add_resource(ServiceRequestAPI,"/api/service_request/<int:id>" , "/api/service_request/<string:action>/<int:request_id>" , "/api/service_request/<int:customer_id>/<int:service_id>/<int:professional_id>")

if __name__ == "__main__":
    app.run(debug=True)



