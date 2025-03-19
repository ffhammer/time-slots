from wtforms import Form, BooleanField, StringField, PasswordField, validators


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
