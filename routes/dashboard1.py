# routes/dashboard.py

from sqlalchemy import func
from flask import render_template
from extensions import db
from models import (
    Project,
    StrategicObjective,
    Indicator,
    Activity,
    ActivityAttendance
)

from routes import bp_dashboard


@bp_dashboard.get("/")
def dashboard_home():

    # High-level counts
    total_projects = Project.query.count()
    total_sos = StrategicObjective.query.count()
    total_indicators = Indicator.query.count()
    total_activities = Activity.query.count()

    # Total reach (Male/Female)
    reach_row = db.session.query(
        func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
        func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
    ).one()

    total_male = int(reach_row.male or 0)
    total_female = int(reach_row.female or 0)
    total_reach = total_male + total_female

    # Recent activities
    recent_activities = (
        Activity.query.order_by(Activity.activity_date.desc(), Activity.id.desc())
        .limit(10)
        .all()
    )

    # Latest projects
    recent_projects = (
        Project.query.order_by(Project.created_at.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        stats={
            "projects": total_projects,
            "sos": total_sos,
            "indicators": total_indicators,
            "activities": total_activities,
            "male": total_male,
            "female": total_female,
            "total_reach": total_reach,
        },
        recent_activities=recent_activities,
        recent_projects=recent_projects,
    )