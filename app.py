from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from database import User, Booking, db, fill_with_example_data, get_bookings_inbetween
from booking_management import get_availability
from datetime import datetime, timedelta
from forms import RegistrationForm, LoginForm, BookingForm, generate_booking_form
import click
from config import N_DAYS_AHEAD, MAX_TIME_SPAN

app = Flask(__name__)
app.config["SECRET_KEY"] = "REPLACE_WITH_A_SECURE_KEY"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///booking_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.cli.command("init-db")
def init_db():
    db.create_all()
    click.echo("Database initialized.")


@app.cli.command("fill-samples")
def fill_samples():
    fill_with_example_data()
    click.echo("Sample data inserted.")


@app.route("/login", methods=["GET", "POST"])
def login():
    print("loging called")
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        # In production, compare hashed passwords
        if not user:
            flash("Email not found. Please create an account.", "danger")
        elif user.password != form.password.data:
            flash("Incorrect password.", "danger")
        else:
            login_user(user, remember=form.remember_me.data)
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please log in.", "warning")
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
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


def add_booking_if_available(booking: Booking):
    if len(get_bookings_inbetween(start=booking.start_time, end=booking.end_time)):
        flash("Already occupied", "danger")
        return
    try:
        db.session.add(booking)
        db.session.commit()
        flash("Booking created successfully.", "success")
    except Exception:
        flash("Error saving booking.", "danger")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    dates = [
        (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(N_DAYS_AHEAD)
    ]
    booking_form: BookingForm = (
        generate_booking_form()
    )  # Ensure this creates a BookingForm instance

    # (Assuming generate_booking_form() sets choices appropriately)
    if request.method == "POST" and booking_form.validate():
        date_sel = booking_form.date.data
        start_dt = datetime.strptime(
            f"{date_sel} {booking_form.start_hour.data}:{booking_form.start_minute.data}",
            "%Y-%m-%d %H:%M",
        )
        end_dt = datetime.strptime(
            f"{date_sel} {booking_form.end_hour.data}:{booking_form.end_minute.data}",
            "%Y-%m-%d %H:%M",
        )

        if start_dt >= end_dt:
            flash("Start time must be before end time.", "danger")
        elif end_dt < datetime.now():
            flash("Booking is in the Past", "danger")
        elif end_dt - start_dt > MAX_TIME_SPAN:
            flash(f"Booking ecxeeds {MAX_TIME_SPAN}", "danger")
        else:
            add_booking_if_available(
                Booking(user_id=current_user.id, start_time=start_dt, end_time=end_dt)
            )
        return redirect(url_for("index"))
    availability = get_availability()
    return render_template(
        "index.html",
        title="Soccer Field Booking",
        dates=dates,
        availability=availability,
        START_DAY=8,
        END_DAY=22,
        booking_form=booking_form,
    )


if __name__ == "__main__":
    app.run(debug=True)
