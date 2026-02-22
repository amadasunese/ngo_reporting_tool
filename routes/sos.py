from flask import render_template, request, redirect, url_for, flash
from extensions import db
from models import Project, StrategicObjective
from routes import bp_sos

@bp_sos.get("/")
def list_sos():
    project_id = request.args.get("project_id", type=int)
    projects = Project.query.order_by(Project.created_at.desc()).all()

    q = StrategicObjective.query
    if project_id:
        q = q.filter_by(project_id=project_id)

    sos = q.order_by(StrategicObjective.created_at.desc()).all()
    return render_template("sos/list.html", sos=sos, projects=projects, project_id=project_id)

@bp_sos.get("/create")
def create_so_form():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("sos/create.html", projects=projects)

@bp_sos.post("/create")
def create_so():
    project_id = request.form.get("project_id", type=int)
    so_code = (request.form.get("so_code", "") or "").strip().upper()
    title = (request.form.get("title", "") or "").strip()
    if not project_id or not so_code or not title:
        flash("Project, SO code and title are required.", "error")
        return redirect(url_for("sos.create_so_form"))

    so = StrategicObjective(
        project_id=project_id,
        so_code=so_code,
        title=title,
        description=request.form.get("description") or None,
    )
    db.session.add(so)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("SO code must be unique within the project.", "error")
        return redirect(url_for("sos.create_so_form"))

    flash("Strategic Objective created.", "success")
    return redirect(url_for("sos.view_so", so_id=so.id))

@bp_sos.get("/<int:so_id>")
def view_so(so_id):
    so = StrategicObjective.query.get_or_404(so_id)
    return render_template("sos/view.html", so=so)

@bp_sos.get("/<int:so_id>/edit")
def edit_so_form(so_id):
    so = StrategicObjective.query.get_or_404(so_id)
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("sos/edit.html", so=so, projects=projects)

@bp_sos.post("/<int:so_id>/edit")
def edit_so(so_id):
    so = StrategicObjective.query.get_or_404(so_id)
    project_id = request.form.get("project_id", type=int)
    so_code = (request.form.get("so_code", "") or "").strip().upper()
    title = (request.form.get("title", "") or "").strip()
    if not project_id or not so_code or not title:
        flash("Project, SO code and title are required.", "error")
        return redirect(url_for("sos.edit_so_form", so_id=so_id))

    so.project_id = project_id
    so.so_code = so_code
    so.title = title
    so.description = request.form.get("description") or None

    db.session.commit()
    flash("Strategic Objective updated.", "success")
    return redirect(url_for("sos.view_so", so_id=so.id))

@bp_sos.post("/<int:so_id>/delete")
def delete_so(so_id):
    so = StrategicObjective.query.get_or_404(so_id)
    project_id = so.project_id
    db.session.delete(so)
    db.session.commit()
    flash("Strategic Objective deleted.", "success")
    return redirect(url_for("sos.list_sos", project_id=project_id))
