from flask_wtf import FlaskForm
from wtforms import DecimalField, EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class RegistrationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    roll_number = StringField("Roll Number", validators=[DataRequired(), Length(max=50)])
    department = StringField("Department", validators=[DataRequired(), Length(max=80)])
    cgpa = DecimalField("CGPA", places=2, validators=[DataRequired(), NumberRange(min=0, max=10)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email_or_username = StringField("Email or Username", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Login")
