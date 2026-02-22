from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from extensions import db

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    goal = db.Column(db.Text, nullable=False)

    donor = db.Column(db.String(200))
    location = db.Column(db.String(200))

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    strategic_objectives = db.relationship(
        "StrategicObjective",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan"
    )


class StrategicObjective(db.Model):
    __tablename__ = "strategic_objectives"
    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    so_code = db.Column(db.String(20), nullable=False)   # e.g., SO1
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    indicators = db.relationship(
        "Indicator",
        backref="strategic_objective",
        lazy=True,
        cascade="all, delete-orphan"
    )

    activities = db.relationship(
        "Activity",
        backref="strategic_objective",
        lazy=True,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("project_id", "so_code", name="uq_project_so_code"),
    )


class Indicator(db.Model):
    __tablename__ = "indicators"
    id = db.Column(db.Integer, primary_key=True)

    strategic_objective_id = db.Column(
        db.Integer, db.ForeignKey("strategic_objectives.id"), nullable=False
    )

    indicator_code = db.Column(db.String(40), nullable=False)  # e.g., SO1_IND1
    statement = db.Column(db.Text, nullable=False)

    indicator_type = db.Column(db.String(20))   # Output|Outcome
    unit = db.Column(db.String(50))            # "# persons", "%", "# sessions"
    gender_disaggregation = db.Column(db.Boolean, default=True)

    baseline = db.Column(db.Float, default=0)
    target = db.Column(db.Float)  # optional at MVP

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "strategic_objective_id",
            "indicator_code",
            name="uq_so_indicator_code"
        ),
    )


class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)

    strategic_objective_id = db.Column(
        db.Integer, db.ForeignKey("strategic_objectives.id"), nullable=False
    )

    # optional: link activity to a specific indicator
    indicator_id = db.Column(db.Integer, db.ForeignKey("indicators.id"))

    activity_code = db.Column(db.String(30))  # e.g., A1.1.1
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text)

    activity_date = db.Column(db.Date, nullable=False, default=date.today)
    location = db.Column(db.String(200))

    status = db.Column(db.String(20), default="planned")  # planned|ongoing|completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    indicator = db.relationship(
        "Indicator",
        backref=db.backref("activities", lazy=True)
    )

    attendance = db.relationship(
        "ActivityAttendance",
        backref="activity",
        lazy=True,
        cascade="all, delete-orphan"
    )


class ActivityAttendance(db.Model):
    __tablename__ = "activity_attendance"
    id = db.Column(db.Integer, primary_key=True)

    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)

    male_count = db.Column(db.Integer, default=0)
    female_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def total(self):
        return (self.male_count or 0) + (self.female_count or 0)

    __table_args__ = (
        db.UniqueConstraint("activity_id", name="uq_attendance_activity"),
    )
