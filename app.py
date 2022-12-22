from datetime import datetime, timedelta
from flask import Flask, render_template, request, make_response
import pdfkit
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import db_handler


app = Flask(__name__)
app.app_context().push()


@app.route('/home')
@app.route('/')
def home():
    all_cars = db_handler.get_all_row_order_by_dict("Cars", "car_price")
    to_return = []
    for car in all_cars:
        new_obj = db_handler.Cars()
        new_obj.id = car.id
        new_obj.car_name = car.car_name
        new_obj.car_price = car.car_price
        new_obj.car_type = car.car_type
        new_obj.rented = car.rented
        if car.rented:
            new_obj.rented = False
            al_customers = db_handler.get_row_by_column_list("Booking", ["car_obj", "returned"], [car.id, "0"])
            if type(al_customers) == list:
                suffix_name = " Rented: "
                for customer in al_customers:
                    hire_date = customer.hire_date.strftime("%Y-%m-%d")
                    return_date = customer.return_date.strftime("%Y-%m-%d")
                    suffix_name += "(" + hire_date + " - " + return_date + ") "
                new_obj.car_name += suffix_name
            else:
                hire_date = al_customers.hire_date.strftime("%Y-%m-%d")
                return_date = al_customers.return_date.strftime("%Y-%m-%d")
                new_obj.car_name += " Rented: " + "(" + hire_date + " - " + return_date + ") "
        to_return.append(new_obj)
    return render_template('cars.html', all_cars=to_return)


@app.route('/customers')
def customers():
    all_bookings = db_handler.get_all_row_order_by_dict_by_desc("Booking", "hire_date")
    return render_template('customers.html', all_bookings=all_bookings)


@app.route('/book_car', methods=['POST'])
def book_car():
    car_id = request.form['car_id']
    car = db_handler.get_row_by_column("Cars", "id", car_id)
    car_model = car.car_name
    car_price = car.car_price
    return render_template('booking.html', car_id=car_id, car_model=car_model, car_price=car_price)


@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    car_id = request.form['car_id']
    username = str(request.form['username'])
    useremail = str(request.form['useremail'])
    phonenumber = str(request.form['phonenumber'])
    renting_for = int(request.form['renting_for'])
    picker1 = str(request.form['renting_date'])
    start = datetime.strptime(picker1, '%Y-%m-%d %H:%M')
    return_date = start + timedelta(days=renting_for)

    booking_obj = db_handler.insert_and_get("Booking", ["car_obj", "customer_name", "email", "phone", "hire_date",
                                                        "return_date", "returned"], [car_id, username, useremail,
                                                                         phonenumber, start, return_date, "0"])
    db_handler.update_single_value_by_column("Cars", "rented", 1, "id", car_id)
    invoice_no = booking_obj.id
    invoice_date = booking_obj.hire_date
    user_name = booking_obj.customer_name
    user_email = booking_obj.email
    user_phone = booking_obj.phone
    car = db_handler.get_row_by_column("Cars", "id", car_id)
    rental_fee = car.car_price
    insurance_fee = 100
    taxes = rental_fee * 0.15
    total = rental_fee + insurance_fee + taxes
    car_model = car.car_name
    rental_days = renting_for
    rendered = render_template('invoice.html', invoice_no=invoice_no, invoice_date=invoice_date, user_name=user_name,
                               user_email=user_email, user_phone=user_phone, rental_fee=rental_fee,
                               insurance_fee=insurance_fee, taxes=taxes, total=total, car_model=car_model,
                               rental_days=rental_days)
    try:
        send_email()
    except:
        pass
    return crete_pdf(rendered)


@app.route('/get_report', methods=['POST'])
def get_report():
    picker1 = str(request.form['date'])
    start = datetime.strptime(picker1, '%Y-%m-%d ')
    # all_bookings = db_handler.get_row_by_column_between("Booking", "hire_date", start, end_date)
    all_bookings = db_handler.get_row_by_column("Booking", "hire_date", start)
    if type(all_bookings) == list:
        rendered = render_template('report.html', all_bookings=all_bookings, date=start)
    else:
        rendered = render_template('report.html', all_bookings=[all_bookings], date=start)
    return crete_pdf(rendered)


def crete_pdf(rendered):
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = pdfkit.from_string(rendered, 0, options={"enable-local-file-access": ""}, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    return response


@app.route('/invoice')
def invoice():
    return render_template('invoice.html')


# function get id from url. delete the booking and update the car to not rented and redirect to home page
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    booking = db_handler.delete_by_column_and_return("Booking", "id", id)
    db_handler.update_single_value_by_column("Cars", "rented", 0, "id", booking.car_obj)

    all_bookings = db_handler.get_all_row_order_by_dict_by_desc("Booking", "hire_date")
    return render_template('customers.html', all_bookings=all_bookings)


# function get id from url. delete the booking and update the car to not rented and redirect to home page
@app.route('/return_car/<int:id>', methods=['GET', 'POST'])
def return_car(id):
    booking = db_handler.get_row_by_column("Booking", "id", id)
    all_rentals = db_handler.get_row_by_column_list("Booking", ["car_obj", "returned"], [booking.car_obj, "0"])
    db_handler.update_single_value_by_column("Booking", "returned", 1, "id", id)
    if not type(all_rentals) == list:
        db_handler.update_single_value_by_column("Cars", "rented", 0, "id", booking.car_obj)

    all_bookings = db_handler.get_all_row_order_by_dict_by_desc("Booking", "hire_date")
    return render_template('customers.html', all_bookings=all_bookings)


# function take string "info" then use it to filter the booking table using all the fields then return the result
@app.route('/search', methods=['GET', 'POST'])
def search():
    info = str(request.form['info'])
    all_bookings = db_handler.get_row_by_all_column("Booking", str(info))
    if type(all_bookings) == list:
        return render_template('customers.html', all_bookings=all_bookings)
    return render_template('customers.html', all_bookings=[all_bookings])


# function take booking id then query the booking table and get all the columns then return the result
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    booking = db_handler.get_row_by_column("Booking", "id", id)

    # get the rental days
    # convert string to date
    start = datetime.strptime(str(booking.hire_date), '%Y-%m-%d')
    end = datetime.strptime(str(booking.return_date), '%Y-%m-%d')
    renting_for = (end - start).days
    # get hire date as string
    hire_date = booking.hire_date.strftime('%Y-%m-%d')
    # get the car id
    car_id = booking.car_obj
    # get the car price and model
    car = db_handler.get_row_by_column("Cars", "id", car_id)
    car_price = car.car_price
    car_model = car.car_name
    return render_template('booking.html', booking=booking, renting_for=int(renting_for), car_id=car_id,
                           car_model=car_model,
                           car_price=car_price, hire_date=hire_date, modify=True)


# todo Add content

def send_email():
    message = Mail(
        from_email='e.m.apollo@gmail.com',
        to_emails='ali.h.alabed@gmail.com',
        subject='Car Hire Management System',
        html_content='<strong>Car Hire Management System using flask Python</strong>')

    sg = SendGridAPIClient("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")
    sg.send(message)


# function recive the booking modified data then update the booking table and redirect to home page
@app.route('/submit_modify', methods=['GET', 'POST'])
def submit_modify():
    # get the booking id
    booking_id = int(request.form['booking_id'])
    # get the car id
    car_id = int(request.form['car_id'])
    # get the rental days
    renting_for = int(request.form['renting_for'])
    # get the hire date
    hire_date = request.form['renting_date'].strip()
    # get the return date
    try:
        return_date = datetime.strptime(hire_date, '%Y-%m-%d %H:%M') + timedelta(days=renting_for)
    except:
        return_date = datetime.strptime(hire_date, '%Y-%m-%d') + timedelta(days=renting_for)

    # get the customer name
    customer_name = request.form['username']
    # get the customer email
    email = request.form['useremail']
    # get the customer phone
    phone = request.form['phonenumber']
    # get the booking object
    columns = ["hire_date", "return_date", "customer_name", "email", "phone"]
    # convert date to string
    try:
        hire_date = (datetime.strptime(hire_date, '%Y-%m-%d %H:%M')).strftime('%Y-%m-%d')
    except:
        hire_date = (datetime.strptime(hire_date, '%Y-%m-%d')).strftime('%Y-%m-%d')
    return_date = return_date.strftime('%Y-%m-%d')
    new_valus = [hire_date, return_date, customer_name, email, phone]
    booking = db_handler.update_by_column("Booking", columns, new_valus, "id", booking_id)
    # update the booking object
    # redirect to home page
    all_bookings = db_handler.get_all_row_order_by_dict_by_desc("Booking", "hire_date")
    return render_template('customers.html', all_bookings=all_bookings)


if __name__ == '__main__':
    app.run(debug=True)
