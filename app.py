from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from database import User, Booking, db, fill_with_example_data
from booking_management import get_availability
from datetime import datetime, timedelta
from forms import RegistrationForm, LoginForm
import click

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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        date_sel = request.form.get("date")
        start_time_str = request.form.get("start_time")
        end_time_str = request.form.get("end_time")
        if date_sel and start_time_str and end_time_str:
            start_dt = datetime.strptime(
                f"{date_sel} {start_time_str}", "%Y-%m-%d %H:%M"
            )
            end_dt = datetime.strptime(f"{date_sel} {end_time_str}", "%Y-%m-%d %H:%M")
            db.session.add(
                Booking(user_id=current_user.id, start_time=start_dt, end_time=end_dt)
            )
            db.session.commit()
        return redirect(url_for("index"))
    dates = [
        (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)
    ]
    availability = get_availability()
    return render_template(
        "index.html",
        title="Soccer Field Booking",
        dates=dates,
        availability=availability,
        START_DAY=8,
        END_DAY=22,
    )


if __name__ == "__main__":
    app.run(debug=True)
