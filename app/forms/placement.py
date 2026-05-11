from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import DateField, DecimalField, StringField, SubmitField, TimeField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ResumeUploadForm(FlaskForm):
    resume = FileField(
        "Select Resume (PDF)",
        validators=[FileRequired(), FileAllowed(["pdf"], "Only PDF resumes are allowed.")],
    )
    submit = SubmitField("Upload Resume")


class CompanyDriveForm(FlaskForm):
    company_name = StringField("Company Name", validators=[DataRequired(), Length(max=120)])
    role = StringField("Role", validators=[DataRequired(), Length(max=120)])
    package = StringField("Package", validators=[DataRequired(), Length(max=80)])
    min_cgpa = DecimalField("Minimum CGPA", places=2, validators=[DataRequired(), NumberRange(min=0, max=10)])
    department = StringField("Department", validators=[DataRequired(), Length(max=80)])
    drive_date = DateField("Drive Date", validators=[Optional()])
    submit = SubmitField("Save Drive")


class InterviewForm(FlaskForm):
    interview_date = DateField("Interview Date", validators=[DataRequired()])
    interview_time = TimeField("Interview Time", validators=[DataRequired()])
    venue = StringField("Venue / Meeting Link", validators=[DataRequired(), Length(max=255)])
    submit = SubmitField("Schedule Interview")
