from flask import Flask, jsonify, request, Response
from .src.controller.appointments_controller import AppointmentControl
from .src.controller.customers_controller import CustomerControl
from .src.model.entities import Customer, Appointment


from pydantic import BaseModel
from datetime import datetime, timedelta


class AppointmentV(BaseModel):
    id: int | None = None
    year: int
    month: int
    day: int
    hour: int
    minute: int
    duration: int
    customer_id: int | None = None
    employee_id: int | None = None

    def to_Appointment(self):
        date = datetime(year=self.year, month=self.month, day=self.day, minute=self.minute)
        duration = timedelta(minutes=self.duration)
        return Appointment(
            id=self.id, date=date, duration=duration, customer_id=self.customer_id, employee_id=self.employee_id
        )


class CustomerV(BaseModel):
    id: int | None = None
    name: str
    surname: str | None = None
    phone: str | None = None
    email: str | None = None

    def to_Customer(self):
        return Customer(id=self.id, name=self.name, surname=self.surname, phone=self.phone, email=self.email)


app = Flask(__name__)


@app.route("/appointments")
def get_appointments() -> Response:
    data = AppointmentControl().get_appointments()
    appointments = (v for k, v in data.items())
    transformed = [[v.to_dict_api() for v in list] for list in appointments]
    return jsonify(transformed)


@app.route("/appointment/create")
def create_appointment() -> Response:
    try:
        appointment = AppointmentV.model_validate_strings(request.args.to_dict()).to_Appointment()
        result = AppointmentControl().create_appointment(appointment)
        if result is None:
            raise Exception("Failed to create appointment")
        return jsonify({"success": True, "new_id": result})

    except Exception as e:
        response = jsonify({"success": False, "reason": "Parameters are wrong", "error": str(e)})
        return response


@app.route("/appointment/delete", methods=["POST"])
def delete_appointment() -> Response:
    try:
        appointment = AppointmentV.model_validate_strings(request.args.to_dict()).to_Appointment()
        result = AppointmentControl().create_appointment(appointment)
        return jsonify({"success": result})

    except Exception as e:
        response = jsonify({"reason": "Parameters are wrong", "error": str(e)})
        response.status_code = 422
        return response


@app.route("/appointment/update", methods=["POST"])
def update_appointment() -> Response:
    try:
        appointment = AppointmentV.model_validate_strings(request.args.to_dict()).to_Appointment()
        result = AppointmentControl().create_appointment(appointment)
        return jsonify({"success": result})

    except Exception as e:
        response = jsonify({"reason": "Parameters are wrong", "error": str(e)})
        response.status_code = 422
        return response


@app.route("/appointment/id/<id>")
def get_appointment_by_id(_id) -> Response:
    id = int(_id)
    appointment = AppointmentControl().get_appointment_by_id(id)
    if appointment:
        return jsonify(appointment.to_dict_api())
    else:
        response = jsonify({"reason": "not found"})
        response.status_code = 404
        return response


@app.route("/appointment/date")
def get_appointment_by_date() -> Response:
    date = datetime(
        year=int(request.args["year"]),
        month=int(request.args.get("month") or 0),
        day=int(request.args.get("day") or 0),
        hour=int(request.args.get("hour") or 0),
        minute=int(request.args.get("minute") or 0),
    )
    apt = AppointmentControl().get_appointment_by_date(date)
    if apt:
        return jsonify(apt.to_dict_api())
    else:
        response = jsonify({"reason": "not found"})
        response.status_code = 404
        return response


@app.route("/appointments/period")
def get_appointments_from_to_date() -> Response:
    from_date = datetime(
        year=int(request.args["from_year"]),
        month=int(request.args.get("from_month") or 0),
        day=int(request.args.get("from_day") or 0),
        hour=int(request.args.get("from_hour") or 0),
        minute=int(request.args.get("from_minute") or 0),
    )
    to_date = datetime(
        year=int(request.args["to_year"]),
        month=int(request.args.get("to_month") or 0),
        day=int(request.args.get("to_day") or 0),
        hour=int(request.args.get("to_hour") or 0),
        minute=int(request.args.get("to_minute") or 0),
    )
    data = AppointmentControl().get_appointments_from_to_date(from_date, to_date)
    transformed = [v.to_dict_api() for v in data]
    return jsonify(transformed)


@app.route("/customers")
def get_customers() -> Response:
    # TODO make it better
    customers, pages = CustomerControl().get_customers(page_length=100, page_number=1)
    return jsonify({"data": [*map(Customer.to_dict_api, customers)], "pages": f"1/{pages}"})


@app.route("/customers/<page>")
def get_customers_by_page(page) -> Response:
    # TODO make it better
    customers, pages = CustomerControl().get_customers(page_length=100, page_number=int(page))
    return jsonify(
        {"data": [*map(Customer.to_dict_api, customers)], "pages": f"{page}/{pages}"},
    )


@app.route("/customers/search/<query>")
def search_customers(query):
    # TODO make it better
    customers, pages = CustomerControl().get_customers(page_length=100, page_number=1, search_query=query)
    return jsonify(
        {"data": [*map(Customer.to_dict_api, customers)], "pages": f"1/{pages}"},
    )


@app.route("/customers/search/<query>/<page>")
def search_customers_by_page(query, page):
    # TODO make it better
    customers, pages = CustomerControl().get_customers(page_length=100, page_number=page, search_query=query)
    return jsonify(
        {"data": [*map(Customer.to_dict_api, customers)], "pages": f"{page}/{pages}"},
    )


@app.route("/customer/create", methods=["POST"])
def create_customer():
    customer = CustomerV.model_validate_strings(request.args.to_dict()).to_Customer()
    id, result = CustomerControl().create_customer(customer)
    if not result:
        return jsonify({"success": False, "reason": "failed to create customer"})
    else:
        return jsonify({"success": True, "id": id})


@app.route("/customer/delete", methods=["POST"])
def delete_customer() -> Response:
    customer = CustomerV.model_validate_strings(request.args.to_dict()).to_Customer()
    result = CustomerControl().delete_customer(customer)
    if not result:
        return jsonify({"success": False, "reason": "failed to delete customer"})
    else:
        return jsonify({"success": True, "id": id})


@app.route("/customer/update", methods=["POST"])
def update_customer() -> Response:
    customer = CustomerV.model_validate_strings(request.args.to_dict()).to_Customer()
    result = CustomerControl().update_customer(customer)
    if not result:
        return jsonify({"success": False, "reason": "failed to update customer"})
    else:
        return jsonify({"success": True, "id": id})


@app.route("/customer/id/<id>")
def get_customer_by_id(id) -> Response:
    _id = int(id)
    customer = CustomerControl().get_customer_by_id(_id)
    if customer is None:
        return jsonify([])
    else:
        return jsonify([customer.to_dict_api()])


def start_server(host, port, debug=True):
    app.run(host, port, debug)
