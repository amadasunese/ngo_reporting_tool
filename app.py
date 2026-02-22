from flask import Flask, redirect, url_for
from config import Config
from extensions import db, migrate, csrf

from routes import bp_dashboard, bp_projects, bp_sos, bp_indicators, bp_activities, bp_reports, bp_testscore

# Import route modules so handlers register on blueprints (required)
from routes import dashboard as _dashboard_routes  # noqa: F401
from routes import projects as _projects_routes  # noqa: F401
from routes import sos as _sos_routes            # noqa: F401
from routes import indicators as _ind_routes     # noqa: F401
from routes import activities as _act_routes     # noqa: F401
from routes import reports as _rep_routes        # noqa: F401
from routes import testscore as _ts_routes        # noqa: F401

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
    app.register_blueprint(bp_testscore)

    @app.get("/")
    def index():
        return redirect(url_for("dashboard.dashboard_home"))

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
