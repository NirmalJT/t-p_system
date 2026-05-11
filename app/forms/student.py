from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp


class EditProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    department = StringField("Department", validators=[DataRequired(), Length(max=80)])
    cgpa = DecimalField("CGPA", places=2, validators=[DataRequired(), NumberRange(min=0, max=10)])
    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=20),
            Regexp(r"^[0-9+\-\s]*$", message="Phone can contain numbers, spaces, + and -."),
        ],
    )
    submit = SubmitField("Update Profile")
