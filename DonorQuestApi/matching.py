from math import radians, sin, cos, asin, sqrt
from datetime import date, timedelta

def compatible_groups(req_bg: str):
    m = {
        "A+": {"A+","A-","O+","O-"},
        "A-": {"A-","O-"},
        "B+": {"B+","B-","O+","O-"},
        "B-": {"B-","O-"},
        "AB+": {"A+","A-","B+","B-","AB+","AB-","O+","O-"},
        "AB-": {"A-","B-","AB-","O-"},
        "O+": {"O+","O-"},
        "O-": {"O-"}
    }
    return m.get(req_bg, set())

def cooldown_ok(last_date):
    if not last_date: return True
    return last_date <= (date.today() - timedelta(days=90))
