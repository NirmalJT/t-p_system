from app.extensions import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    website = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    drives = db.relationship("PlacementDrive", back_populates="company", cascade="all, delete-orphan")


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    package = db.Column(db.String(80), nullable=False)
    min_cgpa = db.Column(db.Numeric(4, 2), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    drive_date = db.Column(db.Date, nullable=True)
    is_open = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    company = db.relationship("Company", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive", cascade="all, delete-orphan")


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive_application"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    status = db.Column(db.String(30), default="Applied", nullable=False)
    applied_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    student = db.relationship("StudentProfile", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")
    interviews = db.relationship("Interview", back_populates="application", cascade="all, delete-orphan")


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    interview_date = db.Column(db.Date, nullable=False)
    interview_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), default="Scheduled", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    application = db.relationship("Application", back_populates="interviews")


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Unread", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    student = db.relationship("User", back_populates="notifications")
