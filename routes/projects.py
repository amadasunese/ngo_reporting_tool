from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from extensions import db
from models import Project
from routes import bp_projects

@bp_projects.get("/")
def list_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects/list.html", projects=projects)

@bp_projects.get("/create")
def create_project_form():
    return render_template("projects/create.html")

@bp_projects.post("/create")
def create_project():
    name = request.form.get("name", "").strip()
    goal = request.form.get("goal", "").strip()
    if not name or not goal:
        flash("Project name and goal are required.", "error")
        return redirect(url_for("projects.create_project_form"))

    def parse_date(v):
        return datetime.strptime(v, "%Y-%m-%d").date() if v else None

    p = Project(
        name=name,
        goal=goal,
        donor=request.form.get("donor") or None,
        location=request.form.get("location") or None,
        start_date=parse_date(request.form.get("start_date")),
        end_date=parse_date(request.form.get("end_date")),
    )
    db.session.add(p)
    db.session.commit()
    flash("Project created.", "success")
    return redirect(url_for("projects.view_project", project_id=p.id))

@bp_projects.get("/<int:project_id>")
def view_project(project_id):
    p = Project.query.get_or_404(project_id)
    return render_template("projects/view.html", project=p)

@bp_projects.get("/<int:project_id>/edit")
def edit_project_form(project_id):
    p = Project.query.get_or_404(project_id)
    return render_template("projects/edit.html", project=p)

@bp_projects.post("/<int:project_id>/edit")
def edit_project(project_id):
    p = Project.query.get_or_404(project_id)
    name = request.form.get("name", "").strip()
    goal = request.form.get("goal", "").strip()
    if not name or not goal:
        flash("Project name and goal are required.", "error")
        return redirect(url_for("projects.edit_project_form", project_id=project_id))

    def parse_date(v):
        return datetime.strptime(v, "%Y-%m-%d").date() if v else None

    p.name = name
    p.goal = goal
    p.donor = request.form.get("donor") or None
    p.location = request.form.get("location") or None
    p.start_date = parse_date(request.form.get("start_date"))
    p.end_date = parse_date(request.form.get("end_date"))

    db.session.commit()
    flash("Project updated.", "success")
    return redirect(url_for("projects.view_project", project_id=p.id))

@bp_projects.post("/<int:project_id>/delete")
def delete_project(project_id):
    p = Project.query.get_or_404(project_id)
    db.session.delete(p)
    db.session.commit()
    flash("Project deleted.", "success")
    return redirect(url_for("projects.list_projects"))
