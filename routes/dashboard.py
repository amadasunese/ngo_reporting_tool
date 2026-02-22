from sqlalchemy import func
from flask import render_template
from extensions import db
from models import Project, StrategicObjective, Indicator, Activity, ActivityAttendance
from routes import bp_dashboard


def _total_reach():
    row = db.session.query(
        func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
        func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
    ).one()
    male = int(row.male or 0)
    female = int(row.female or 0)
    return male, female, male + female


def _activity_status_counts():
    rows = db.session.query(Activity.status, func.count(Activity.id)).group_by(Activity.status).all()
    data = {"planned": 0, "ongoing": 0, "completed": 0}
    for status, count in rows:
        data[status] = int(count)
    return data


def _reach_by_so(limit: int = 10):
    rows = (
        db.session.query(
            StrategicObjective.so_code,
            func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
            func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
        )
        .join(Activity, Activity.strategic_objective_id == StrategicObjective.id)
        .outerjoin(ActivityAttendance, ActivityAttendance.activity_id == Activity.id)
        .group_by(StrategicObjective.id)
        .order_by(
            (func.coalesce(func.sum(ActivityAttendance.male_count), 0)
             + func.coalesce(func.sum(ActivityAttendance.female_count), 0)).desc()
        )
        .limit(limit)
        .all()
    )

    labels, male, female = [], [], []
    for r in rows:
        labels.append(r.so_code)
        male.append(int(r.male or 0))
        female.append(int(r.female or 0))
    return labels, male, female


def _monthly_reach_last_n_months(n: int = 6):
    # SQLite-friendly grouping by YYYY-MM
    rows = (
        db.session.query(
            func.strftime("%Y-%m", Activity.activity_date).label("ym"),
            func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
            func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
        )
        .join(ActivityAttendance, ActivityAttendance.activity_id == Activity.id)
        .group_by("ym")
        .order_by("ym")
        .all()
    )

    rows = rows[-n:] if len(rows) > n else rows
    labels, totals = [], []
    for r in rows:
        labels.append(r.ym)
        totals.append(int((r.male or 0) + (r.female or 0)))
    return labels, totals


@bp_dashboard.get("/")
def dashboard_home():
    # KPIs
    total_projects = Project.query.count()
    total_sos = StrategicObjective.query.count()
    total_indicators = Indicator.query.count()
    total_activities = Activity.query.count()

    male, female, total_reach = _total_reach()

    status_counts = _activity_status_counts()
    completed = status_counts.get("completed", 0)
    completion_rate = round((completed / total_activities) * 100, 1) if total_activities else 0.0

    # Recent lists
    recent_activities = (
        Activity.query.order_by(Activity.activity_date.desc(), Activity.id.desc()).limit(10).all()
    )
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(6).all()

    # Charts
    so_labels, so_male, so_female = _reach_by_so(limit=10)
    monthly_labels, monthly_total = _monthly_reach_last_n_months(6)

    return render_template(
        "dashboard/index.html",
        stats={
            "projects": total_projects,
            "sos": total_sos,
            "indicators": total_indicators,
            "activities": total_activities,
            "male": male,
            "female": female,
            "total_reach": total_reach,
            "completion_rate": completion_rate,
            "status_counts": status_counts,
        },
        charts={
            "so_labels": so_labels,
            "so_male": so_male,
            "so_female": so_female,
            "monthly_labels": monthly_labels,
            "monthly_total": monthly_total,
        },
        recent_activities=recent_activities,
        recent_projects=recent_projects,
    )