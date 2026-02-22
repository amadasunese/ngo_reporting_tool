from flask import Blueprint

bp_dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")
bp_projects   = Blueprint("projects", __name__, url_prefix="/projects")
bp_sos        = Blueprint("sos", __name__, url_prefix="/sos")
bp_indicators = Blueprint("indicators", __name__, url_prefix="/indicators")
bp_activities = Blueprint("activities", __name__, url_prefix="/activities")
bp_reports    = Blueprint("reports", __name__, url_prefix="/reports")
