from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    Form,
    PasswordField,
    SelectField,
    StringField,
    validators,
)

from config import END_DAY, START_DAY, TIME_ZONE


class RegistrationForm(Form):
    first_name = StringField(
        "First Name", [validators.Length(min=2, max=100), validators.InputRequired()]
    )
    last_name = StringField(
        "Last Name", [validators.Length(min=2, max=100), validators.InputRequired()]
    )
    email = StringField(
        "Email Address",
        [
            validators.Length(min=6, max=255),
            validators.Email(),
            validators.InputRequired(),
        ],
    )
    password = PasswordField(
        "Password",
        [
            validators.Length(min=6, max=255),
            validators.InputRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")
    accept_rules = BooleanField("I accept the site rules", [validators.InputRequired()])


class LoginForm(Form):
    email = StringField(
        "Email Address",
        [
            validators.Length(min=6, max=255),
            validators.Email(),
            validators.InputRequired(),
        ],
    )
    password = PasswordField("Password", [validators.InputRequired()])
    remember_me = BooleanField("Remember Me")


class BookingForm(FlaskForm):
    date = SelectField("Date", choices=[], validators=[validators.InputRequired()])
    start_hour = SelectField(
        "Start - Hour:",
        choices=list(range(START_DAY, END_DAY)),
        validators=[validators.InputRequired()],
    )
    start_minute = SelectField(
        "Minute:",
        choices=[0, 15, 30, 45],
        validators=[validators.InputRequired()],
    )
    end_hour = SelectField(
        "End - Hour:",
        choices=list(range(START_DAY, END_DAY + 1)),
        validators=[validators.InputRequired()],
    )
    end_minute = SelectField(
        "Minute:", choices=[0, 15, 30, 45], validators=[validators.InputRequired()]
    )


def generate_booking_form() -> BookingForm:
    form = BookingForm()
    dates = [
        (datetime.now(tz=TIME_ZONE) + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(7)
    ]
    form.date.choices = [(d, d) for d in dates]
    return form
