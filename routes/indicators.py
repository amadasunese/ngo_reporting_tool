from flask import render_template, request, redirect, url_for, flash
from extensions import db
from models import StrategicObjective, Indicator, Project
from routes import bp_indicators

@bp_indicators.get("/")
def list_indicators():
    project_id = request.args.get("project_id", type=int)
    so_id = request.args.get("so_id", type=int)

    projects = Project.query.order_by(Project.created_at.desc()).all()
    sos = StrategicObjective.query.order_by(StrategicObjective.created_at.desc()).all()

    q = Indicator.query.join(StrategicObjective, Indicator.strategic_objective_id == StrategicObjective.id)
    if project_id:
        q = q.filter(StrategicObjective.project_id == project_id)
    if so_id:
        q = q.filter(Indicator.strategic_objective_id == so_id)

    indicators = q.order_by(Indicator.created_at.desc()).all()
    return render_template("indicators/list.html",
                          indicators=indicators, projects=projects, sos=sos,
                          project_id=project_id, so_id=so_id)

@bp_indicators.get("/create")
def create_indicator_form():
    sos = StrategicObjective.query.order_by(StrategicObjective.created_at.desc()).all()
    return render_template("indicators/create.html", sos=sos)

@bp_indicators.post("/create")
def create_indicator():
    so_id = request.form.get("strategic_objective_id", type=int)
    code = (request.form.get("indicator_code", "") or "").strip().upper()
    statement = (request.form.get("statement", "") or "").strip()
    if not so_id or not code or not statement:
        flash("SO, Indicator code and statement are required.", "error")
        return redirect(url_for("indicators.create_indicator_form"))

    ind = Indicator(
        strategic_objective_id=so_id,
        indicator_code=code,
        statement=statement,
        indicator_type=request.form.get("indicator_type") or None,
        unit=request.form.get("unit") or None,
        gender_disaggregation=True if request.form.get("gender_disaggregation") == "on" else False,
        baseline=float(request.form.get("baseline") or 0),
        target=float(request.form.get("target") or 0) if (request.form.get("target") or "").strip() else None,
    )
    db.session.add(ind)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Indicator code must be unique within the SO.", "error")
        return redirect(url_for("indicators.create_indicator_form"))

    flash("Indicator created.", "success")
    return redirect(url_for("indicators.view_indicator", indicator_id=ind.id))

@bp_indicators.get("/<int:indicator_id>")
def view_indicator(indicator_id):
    ind = Indicator.query.get_or_404(indicator_id)
    return render_template("indicators/view.html", indicator=ind)

@bp_indicators.get("/<int:indicator_id>/edit")
def edit_indicator_form(indicator_id):
    ind = Indicator.query.get_or_404(indicator_id)
    sos = StrategicObjective.query.order_by(StrategicObjective.created_at.desc()).all()
    return render_template("indicators/edit.html", indicator=ind, sos=sos)

@bp_indicators.post("/<int:indicator_id>/edit")
def edit_indicator(indicator_id):
    ind = Indicator.query.get_or_404(indicator_id)
    so_id = request.form.get("strategic_objective_id", type=int)
    code = (request.form.get("indicator_code", "") or "").strip().upper()
    statement = (request.form.get("statement", "") or "").strip()
    if not so_id or not code or not statement:
        flash("SO, Indicator code and statement are required.", "error")
        return redirect(url_for("indicators.edit_indicator_form", indicator_id=indicator_id))

    ind.strategic_objective_id = so_id
    ind.indicator_code = code
    ind.statement = statement
    ind.indicator_type = request.form.get("indicator_type") or None
    ind.unit = request.form.get("unit") or None
    ind.gender_disaggregation = True if request.form.get("gender_disaggregation") == "on" else False
    ind.baseline = float(request.form.get("baseline") or 0)
    ind.target = float(request.form.get("target") or 0) if (request.form.get("target") or "").strip() else None

    db.session.commit()
    flash("Indicator updated.", "success")
    return redirect(url_for("indicators.view_indicator", indicator_id=ind.id))

@bp_indicators.post("/<int:indicator_id>/delete")
def delete_indicator(indicator_id):
    ind = Indicator.query.get_or_404(indicator_id)
    so_id = ind.strategic_objective_id
    db.session.delete(ind)
    db.session.commit()
    flash("Indicator deleted.", "success")
    return redirect(url_for("indicators.list_indicators", so_id=so_id))
