# app.py
from datetime import datetime, timedelta

import click
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from .booking_management import get_availability
from .config import (
    END_DAY,
    MAX_TIME_SPAN,
    N_DAYS_AHEAD,
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
    START_DAY,
    TIME_ZONE,
)
from .database import Booking, User, db, fill_with_example_data, get_bookings_inbetween
from .forms import BookingForm, LoginForm, RegistrationForm, generate_booking_form
from .logging import logger

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {e}")
        return None


@app.cli.command("init-db")
def init_db():
    db.create_all()
    logger.info("Database initialized.")
    click.echo("Database initialized.")


@app.cli.command("fill-samples")
def fill_samples():
    try:
        fill_with_example_data()
        logger.info("Sample data inserted.")
        click.echo("Sample data inserted.")
    except Exception as e:
        logger.error(f"Error inserting sample data: {e}")
        click.echo("Error inserting sample data.")


@app.route("/login", methods=["GET", "POST"])
def login():
    logger.info("Login endpoint called.")
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            user = User.query.filter_by(email=form.email.data).first()
        except Exception as e:
            logger.error(f"Error querying user: {e}")
            flash("Internal error. Please try again.", "danger")
            return render_template("login.html", form=form)
        if not user:
            flash("Email not found. Please create an account.", "danger")
            logger.info("Login failed: email not found.")
        elif user.password != form.password.data:
            flash("Incorrect password.", "danger")
            logger.info("Login failed: incorrect password.")
        else:
            login_user(user, remember=form.remember_me.data)
            flash("Logged in successfully.", "success")
            logger.info(f"User {user.email} logged in.")
            return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            if User.query.filter_by(email=form.email.data).first():
                flash("Email already registered. Please log in.", "warning")
                logger.info(
                    f"Registration attempt with existing email: {form.email.data}"
                )
            else:
                new_user = User(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=form.password.data,  # Hash this in production!
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Account created successfully. Please log in.", "success")
                logger.info(f"New user registered: {form.email.data}")
                return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash("Error creating account.", "danger")
            logger.error(f"Error registering user {form.email.data}: {e}")
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    logger.info(f"User logged out: {current_user.email if current_user else 'unknown'}")
    return redirect(url_for("login"))


def add_booking_if_available(booking: Booking):
    if len(get_bookings_inbetween(start=booking.start_time, end=booking.end_time)):
        flash("Already occupied", "danger")
        logger.info(
            f"Booking conflict for user {booking.user_id}: {booking.start_time} - {booking.end_time}"
        )
        return
    try:
        db.session.add(booking)
        db.session.commit()
        flash("Booking created successfully.", "success")
        logger.info(
            f"Booking created for user {booking.user_id}: {booking.start_time} - {booking.end_time}"
        )
    except Exception as e:
        db.session.rollback()
        flash("Error saving booking.", "danger")
        logger.error(f"Error saving booking for user {booking.user_id}: {e}")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    dates = [
        (datetime.now(tz=TIME_ZONE) + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(N_DAYS_AHEAD)
    ]
    booking_form: BookingForm = generate_booking_form()
    if request.method == "POST" and booking_form.validate():
        date_sel = booking_form.date.data
        start_dt = datetime.strptime(
            f"{date_sel} {booking_form.start_hour.data}:{booking_form.start_minute.data}",
            "%Y-%m-%d %H:%M",
        ).replace(tzinfo=TIME_ZONE)
        end_dt = datetime.strptime(
            f"{date_sel} {booking_form.end_hour.data}:{booking_form.end_minute.data}",
            "%Y-%m-%d %H:%M",
        ).replace(tzinfo=TIME_ZONE)
        logger.info(
            f"Booking attempt by user {current_user.email}: {start_dt} - {end_dt}"
        )
        if start_dt >= end_dt:
            flash("Start time must be before end time.", "danger")
            logger.warning("Booking error: Start time is not before end time.")
        elif end_dt < datetime.now(tz=TIME_ZONE):
            flash("Booking is in the Past", "danger")
            logger.warning("Booking error: Booking in the past.")
        elif end_dt - start_dt > MAX_TIME_SPAN:
            flash(f"Booking exceeds {MAX_TIME_SPAN}", "danger")
            logger.warning("Booking error: Duration exceeds maximum allowed.")
        else:
            add_booking_if_available(
                Booking(user_id=current_user.id, start_time=start_dt, end_time=end_dt)
            )
        return redirect(url_for("index"))
    try:
        availability = get_availability()
    except Exception as e:
        availability = {}
        flash("Error loading availability.", "danger")
        logger.error(f"Error loading availability: {e}")
    return render_template(
        "index.html",
        title="Soccer Field Booking",
        dates=dates,
        availability=availability,
        START_DAY=START_DAY,
        END_DAY=END_DAY,
        booking_form=booking_form,
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        logger.info("Database created on app start.")
    app.run(debug=True)
