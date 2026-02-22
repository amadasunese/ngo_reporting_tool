from flask import Flask, redirect, url_for
from config import Config
from extensions import db, migrate, csrf

from routes import bp_dashboard, bp_projects, bp_sos, bp_indicators, bp_activities, bp_reports




# Import route modules so handlers register on blueprints (required)
from routes import dashboard as _dashboard_routes         # noqa: F401
from routes import projects as _projects_routes  # noqa: F401
from routes import sos as _sos_routes            # noqa: F401
from routes import indicators as _ind_routes     # noqa: F401
from routes import activities as _act_routes     # noqa: F401
from routes import reports as _rep_routes        # noqa: F401

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_projects)
    app.register_blueprint(bp_sos)
    app.register_blueprint(bp_indicators)
    app.register_blueprint(bp_activities)
    app.register_blueprint(bp_reports)

    # @app.get("/")
    # def index():
    #     return redirect(url_for("projects.list_projects"))
    
    @app.get("/")
    def index():
        return redirect(url_for("dashboard.dashboard_home"))
    
    # app.py (replace ONLY the index() route)

    # from sqlalchemy import func
    # from models import Project, StrategicObjective, Indicator, Activity, ActivityAttendance

    # @app.get("/")
    # def index():
    #     # High-level counts
    #     total_projects = Project.query.count()
    #     total_sos = StrategicObjective.query.count()
    #     total_indicators = Indicator.query.count()
    #     total_activities = Activity.query.count()

    #     # Total reach (Male/Female/Total) across all recorded attendance
    #     reach_row = db.session.query(
    #         func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
    #         func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
    #     ).one()
    #     total_male = int(reach_row.male or 0)
    #     total_female = int(reach_row.female or 0)
    #     total_reach = total_male + total_female

    #     # Recent activities
    #     recent_activities = (
    #         Activity.query.order_by(Activity.activity_date.desc(), Activity.id.desc())
    #         .limit(10)
    #         .all()
    #     )

    #     # Latest projects
    #     recent_projects = (
    #         Project.query.order_by(Project.created_at.desc())
    #         .limit(6)
    #         .all()
    #     )

    #     return render_template(
    #         "dashboard/index.html",
    #         stats={
    #             "projects": total_projects,
    #             "sos": total_sos,
    #             "indicators": total_indicators,
    #             "activities": total_activities,
    #             "male": total_male,
    #             "female": total_female,
    #             "total_reach": total_reach,
    #         },
    #         recent_activities=recent_activities,
    #         recent_projects=recent_projects,
    #     )

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
