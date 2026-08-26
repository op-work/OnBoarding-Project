import datetime
from typing import Optional

def format_date(dt: Optional[datetime.date]) -> str:
    if not dt:
        return "N/A"
    if isinstance(dt, datetime.datetime):
        dt = dt.date()
    return dt.strftime("%d %b %Y")

def format_datetime(dt: Optional[datetime.datetime]) -> str:
    if not dt:
        return "N/A"
    return dt.strftime("%d %b %Y, %I:%M %p")

def calculate_feedback_due_date(doj: datetime.date, days_offset: int) -> datetime.date:
    if isinstance(doj, datetime.datetime):
        doj = doj.date()
    return doj + datetime.timedelta(days=days_offset)

def calculate_days_overdue(due_date: Optional[datetime.date], today: Optional[datetime.date] = None) -> int:
    if not due_date:
        return 0
    if isinstance(due_date, datetime.datetime):
        due_date = due_date.date()
    if today is None:
        today = datetime.date.today()
    delta = (today - due_date).days
    return max(0, delta)

def get_status_color(status: str) -> str:
    status_lower = (status or "").lower()
    if "completed" in status_lower or "approved" in status_lower:
        return "#10B981"  # Emerald Green
    elif "in progress" in status_lower or "received" in status_lower:
        return "#3B82F6"  # Royal Blue
    elif "pending" in status_lower or "requested" in status_lower:
        return "#F59E0B"  # Amber
    elif "rejected" in status_lower or "overdue" in status_lower:
        return "#E57C00"  # Konverge AI Yellowish Orange
    else:
        return "#6B7280"  # Muted Gray
