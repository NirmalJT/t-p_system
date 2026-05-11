from sqlalchemy import text

from app.extensions import db


def table_exists(inspector, table_name):
    return inspector.has_table(table_name)


def column_names(inspector, table_name):
    if not table_exists(inspector, table_name):
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def execute(sql):
    db.session.execute(text(sql))


def upgrade_legacy_schema():
    """Bring old college-project MySQL tables in line with the ORM models.

    SQLAlchemy's create_all creates missing tables but does not alter old tables.
    This helper is intentionally conservative: it only adds missing columns and
    copies old values into the new normalized fields.
    """
    db.create_all()
    inspector = db.inspect(db.engine)

    if table_exists(inspector, "notifications"):
        columns = column_names(inspector, "notifications")
        if "student_user_id" not in columns:
            execute("ALTER TABLE notifications ADD COLUMN student_user_id INT NULL")
            if "student_id" in columns:
                execute("UPDATE notifications SET student_user_id = student_id WHERE student_user_id IS NULL")
        if "created_at" not in columns:
            execute("ALTER TABLE notifications ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")

    if table_exists(inspector, "companies"):
        columns = column_names(inspector, "companies")
        if "name" not in columns:
            execute("ALTER TABLE companies ADD COLUMN name VARCHAR(120) NULL")
            if "company_name" in columns:
                execute("UPDATE companies SET name = company_name WHERE name IS NULL")
        if "website" not in columns:
            execute("ALTER TABLE companies ADD COLUMN website VARCHAR(255) NULL")
        if "created_at" not in columns:
            execute("ALTER TABLE companies ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")

    inspector = db.inspect(db.engine)
    if table_exists(inspector, "companies") and table_exists(inspector, "placement_drives"):
        drive_columns = column_names(inspector, "placement_drives")
        if {"company_id", "role", "package", "min_cgpa", "department"}.issubset(drive_columns):
            execute(
                """
                INSERT INTO placement_drives
                    (id, company_id, role, package, min_cgpa, department, is_open, created_at)
                SELECT
                    c.id, c.id, c.role, c.package, c.min_cgpa, c.department, 1, CURRENT_TIMESTAMP
                FROM companies c
                LEFT JOIN placement_drives d ON d.id = c.id
                WHERE d.id IS NULL
                  AND c.role IS NOT NULL
                  AND c.package IS NOT NULL
                  AND c.min_cgpa IS NOT NULL
                  AND c.department IS NOT NULL
                """
            )

    if table_exists(inspector, "applications"):
        columns = column_names(inspector, "applications")
        if "drive_id" not in columns:
            execute("ALTER TABLE applications ADD COLUMN drive_id INT NULL")
            if "company_id" in columns:
                execute("UPDATE applications SET drive_id = company_id WHERE drive_id IS NULL")
        if "applied_at" not in columns:
            execute("ALTER TABLE applications ADD COLUMN applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")

    db.session.commit()
