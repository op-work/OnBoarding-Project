"""
Status Badge Component
Generates HTML color-coded status badges for table views and cards.
"""

def render_status_badge(status: str) -> str:
    """Returns HTML formatted status badge string."""
    s_clean = (status or "Not Started").strip()
    s_lower = s_clean.lower()

    if "completed" in s_lower or "approved" in s_lower or "verified" in s_lower:
        bg = "#D1FAE5"
        color = "#065F46"
    elif "in progress" in s_lower or "dispatched" in s_lower or "scheduled" in s_lower:
        bg = "#DBEAFE"
        color = "#1E40AF"
    elif "pending" in s_lower or "requested" in s_lower:
        bg = "#FEF3C7"
        color = "#92400E"
    elif "rejected" in s_lower or "overdue" in s_lower:
        bg = "#FEE2E2"
        color = "#991B1B"
    else:
        bg = "#F1F5F9"
        color = "#475569"

    badge_html = f"""<span style="
        background-color: {bg};
        color: {color};
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    ">{s_clean}</span>"""
    return badge_html
