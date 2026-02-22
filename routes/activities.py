from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import func
from extensions import db
from models import StrategicObjective, Activity, Indicator, ActivityAttendance, Project
from routes import bp_activities

def activity_reach(activity_id: int):
    row = (db.session.query(
        func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
        func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
    ).filter(ActivityAttendance.activity_id == activity_id).one())
    male = int(row.male)
    female = int(row.female)
    return {"male": male, "female": female, "total": male + female}

@bp_activities.get("/")
def list_activities():
    project_id = request.args.get("project_id", type=int)
    so_id = request.args.get("so_id", type=int)

    projects = Project.query.order_by(Project.created_at.desc()).all()
    sos = StrategicObjective.query.order_by(StrategicObjective.created_at.desc()).all()

    q = Activity.query.join(StrategicObjective, Activity.strategic_objective_id == StrategicObjective.id)
    if project_id:
        q = q.filter(StrategicObjective.project_id == project_id)
    if so_id:
        q = q.filter(Activity.strategic_objective_id == so_id)

    activities = q.order_by(Activity.activity_date.desc()).all()
    return render_template("activities/list.html",
                           activities=activities, projects=projects, sos=sos,
                           project_id=project_id, so_id=so_id)

@bp_activities.get("/create")
def create_activity_form():
    sos = StrategicObjective.query.order_by(StrategicObjective.created_at.desc()).all()
    indicators = Indicator.query.order_by(Indicator.created_at.desc()).all()
    return render_template("activities/create.html", sos=sos, indicators=indicators)

@bp_activities.post("/create")
def create_activity():
    so_id = request.form.get("strategic_objective_id", type=int)
    title = (request.form.get("title", "") or "").strip()
    if not so_id or not title:
        flash("SO and activity title are required.", "error")
        return redirect(url_for("activities.create_activity_form"))

    activity_date = datetime.strptime(request.form.get("activity_date"), "%Y-%m-%d").date()

    a = Activity(
        strategic_objective_id=so_id,
        indicator_id=request.form.get("indicator_id", type=int) or None,
        activity_code=(request.form.get("activity_code") or "").strip() or None,
        title=title,
        description=request.form.get("description") or None,
        activity_date=activity_date,
        location=request.form.get("location") or None,
        status=request.form.get("status") or "planned",
    )
    db.session.add(a)
    db.session.commit()
    flash("Activity created.", "success")
    return redirect(url_for("activities.view_activity", activity_id=a.id))

@bp_activities.get("/<int:activity_id>")
def view_activity(activity_id):
    a = Activity.query.get_or_404(activity_id)
    reach = activity_reach(a.id)
    attendance_row = ActivityAttendance.query.filter_by(activity_id=a.id).first()
    return render_template("activities/view.html", activity=a, reach=reach, attendance_row=attendance_row)

@bp_activities.get("/<int:activity_id>/edit")
def edit_activity_form(activity_id):
    a = Activity.query.get_or_404(activity_id)
    sos = StrategicObjective.query.order_by(StrategicObjective.created_at.desc()).all()
    indicators = Indicator.query.order_by(Indicator.created_at.desc()).all()
    return render_template("activities/edit.html", activity=a, sos=sos, indicators=indicators)

@bp_activities.post("/<int:activity_id>/edit")
def edit_activity(activity_id):
    a = Activity.query.get_or_404(activity_id)
    so_id = request.form.get("strategic_objective_id", type=int)
    title = (request.form.get("title", "") or "").strip()
    if not so_id or not title:
        flash("SO and activity title are required.", "error")
        return redirect(url_for("activities.edit_activity_form", activity_id=activity_id))

    a.strategic_objective_id = so_id
    a.indicator_id = request.form.get("indicator_id", type=int) or None
    a.activity_code = (request.form.get("activity_code") or "").strip() or None
    a.title = title
    a.description = request.form.get("description") or None
    a.activity_date = datetime.strptime(request.form.get("activity_date"), "%Y-%m-%d").date()
    a.location = request.form.get("location") or None
    a.status = request.form.get("status") or "planned"

    db.session.commit()
    flash("Activity updated.", "success")
    return redirect(url_for("activities.view_activity", activity_id=a.id))

@bp_activities.post("/<int:activity_id>/delete")
def delete_activity(activity_id):
    a = Activity.query.get_or_404(activity_id)
    so_id = a.strategic_objective_id
    db.session.delete(a)
    db.session.commit()
    flash("Activity deleted.", "success")
    return redirect(url_for("activities.list_activities", so_id=so_id))

@bp_activities.post("/<int:activity_id>/attendance")
def upsert_attendance(activity_id):
    a = Activity.query.get_or_404(activity_id)
    male = int(request.form.get("male_count") or 0)
    female = int(request.form.get("female_count") or 0)

    row = ActivityAttendance.query.filter_by(activity_id=a.id).first()
    if not row:
        row = ActivityAttendance(activity_id=a.id, male_count=male, female_count=female)
        db.session.add(row)
    else:
        row.male_count = male
        row.female_count = female

    db.session.commit()
    flash("Attendance saved.", "success")
    return redirect(url_for("activities.view_activity", activity_id=a.id))
