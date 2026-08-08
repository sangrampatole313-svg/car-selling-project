
from flask import (Flask, render_template,request, redirect, url_for,session, flash)
from db import get_db_connection

# FLASK APPLICATION
app = Flask(__name__)

# Used for Flask sessions
app.secret_key = "car-selling-secret-key"

# HOME
@app.route("/")
def home():
    return render_template("home.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        if connection is None:
            return "Database connection failed."

        cursor = connection.cursor(dictionary=True)

        try:

            sql = """ SELECT * FROM users WHERE email = %s AND password = %s """

            cursor.execute(sql, (email, password))

            user = cursor.fetchone()

            if user:

                # Store user information in session
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]

                flash("Login successful!", "success")

                # If the user was trying to book a car
                next_page = session.pop("next_page", None)

                if next_page:
                    return redirect(next_page)

                return redirect(url_for("home"))

            else:

                flash(
                    "Invalid email or password.",
                    "danger"
                )

                return render_template("login.html")

        except Exception as e:

            print(f"[LOGIN ERROR] {e}")

            return "Error during login."

        finally:

            cursor.close()
            connection.close()

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("home"))

# CUSTOMER REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        mobile_number = request.form["mobile_number"]
        password = request.form["password"]

        connection = get_db_connection()

        if connection is None:
            return "Database connection failed."

        cursor = connection.cursor()

        try:

            # Check whether email already exists
            check_sql = """ SELECT idFROM usersWHERE email = %s """
            cursor.execute( check_sql, (email,))
            existing_user = cursor.fetchone()

            if existing_user:

                flash("Email already registered.", "danger")
                return render_template("register.html")

            # Insert customer
            sql = """INSERT INTO users(name, email, mobile_number, password) VALUES (%s, %s, %s, %s)
            """

            values = (  name,  email,  mobile_number, password )

            cursor.execute(sql, values)

            connection.commit()

            flash( "Registration successful. Please login.",  "success" )

            return redirect(url_for("login"))

        except Exception as e:

            connection.rollback()

            print(f"[REGISTER ERROR] {e}")

            return "Error while registering."

        finally:

            cursor.close()
            connection.close()

    return render_template("register.html")

# AVAILABLE CARS


@app.route("/cars")
def cars():
    return render_template("AvailableCars.html")

# CAR DETAILS


@app.route("/car/<int:car_id>")
def car_details(car_id):

    return render_template(
        "car_details.html",
        car_id=car_id
    )

# BOOK NOW
@app.route("/book/<int:car_id>")
def book_car(car_id):

    # User must login before booking
    if "user_id" not in session:

        # Remember selected car
        session["next_page"] = url_for("booking_form",car_id=car_id )

        flash(  "Please login before booking a car.",  "warning" )
        return redirect(url_for("login"))

    return redirect( url_for(  "booking_form",  car_id=car_id )  )

# BOOKING
@app.route( "/booking/<int:car_id>",methods=["GET", "POST"])
def booking_form(car_id):

    # Check login
    if "user_id" not in session:
        session["next_page"] = url_for( "booking_form", car_id=car_id )

        flash( "Please login before booking a car.", "warning" )

        return redirect(url_for("login"))

    # Save booking
    if request.method == "POST":

        user_id = session["user_id"]

        connection = get_db_connection()

        if connection is None:
            return "Database connection failed."

        cursor = connection.cursor()

        try:

            sql = """ INSERT INTO bookings   (user_id, car_id)  VALUES (%s, %s) """

            cursor.execute(   sql,  (user_id, car_id) )

            connection.commit()

            flash(  "Car booked successfully!",  "success" )

            return redirect(     url_for("booking_success") )

        except Exception as e:

            connection.rollback()

            print(f"[BOOKING ERROR] {e}")

            return "Error while booking the car."

        finally:

            cursor.close()
            connection.close()

    return render_template(
        "booking.html",
        car_id=car_id
    )

# BOOKING SUCCESS
@app.route("/booking-success")
def booking_success():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "booking_success.html"
    )

# MY BOOKINGS
@app.route("/my-bookings")
def my_bookings():

    if "user_id" not in session:

        flash(
            "Please login to view your bookings.",
            "warning"
        )

        return redirect(url_for("login"))

    connection = get_db_connection()

    if connection is None:
        return "Database connection failed."

    cursor = connection.cursor(dictionary=True)

    try:

        sql = """  SELECT * FROM bookings WHERE user_id = %s  ORDER BY booking_date DESC """
        cursor.execute( sql, (session["user_id"],) )
        bookings = cursor.fetchall()
        return render_template(  "my_bookings.html",   bookings=bookings)

    except Exception as e:

        print(f"[BOOKINGS ERROR] {e}")

        return "Error while loading bookings."

    finally:

        cursor.close()
        connection.close()

# CONTACT
@app.route("/contactmore")
def contactmore():
    return render_template("register.html")

# REVIEW
@app.route("/review")
def review():
    return render_template("review.html")

# HELP
@app.route("/help")
def help_page():
    return render_template("help.html")

# MORE
@app.route("/more")
def more():
    return render_template("more.html")

# ABOUT
@app.route("/about")
def about():
    return render_template("about.html")

# CAR CATEGORIES
@app.route("/sedans")
def sedans():
    return render_template("sedans.html")


@app.route("/luxury")
def luxury():
    return render_template("luxury.html")


@app.route("/suvs")
def suvs():
    return render_template("suvv.html")


@app.route("/hatchbacks")
def hatchbacks():
    return render_template("hatchbackcars.html")

# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=True)

