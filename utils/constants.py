"""
System Constants and Enums for Onboarding Operations
Defines stages, work modes, department lists, locations, and grades.
"""

# Work Modes
WORK_MODE_ONLINE = "Virtual"
WORK_MODE_OFFLINE = "In-person"
WORK_MODES = ["Virtual", "In-person", "Online", "Offline"]
JOB_LOCATIONS = ["Nagpur", "Pune"]
MODES_OF_JOINING = ["In-person", "Virtual"]

# Milestone Stages
STAGE_PRE_ONBOARDING = "Pre-Onboarding"
STAGE_ONBOARDING_DAY = "Onboarding Day"
STAGE_POST_ONBOARDING = "Post-Onboarding"
STAGE_FEEDBACK_PROBATION = "Feedback & Probation"
STAGES = [STAGE_PRE_ONBOARDING, STAGE_ONBOARDING_DAY, STAGE_POST_ONBOARDING]
ALL_STAGES = [STAGE_PRE_ONBOARDING, STAGE_ONBOARDING_DAY, STAGE_POST_ONBOARDING, STAGE_FEEDBACK_PROBATION]

# Backward compatibility aliases
STAGE_PRE = STAGE_PRE_ONBOARDING
STAGE_DAY = STAGE_ONBOARDING_DAY
STAGE_POST = STAGE_POST_ONBOARDING

# Stage Descriptions
STAGE_DESCRIPTIONS = {
    STAGE_PRE_ONBOARDING: "Complete pre-joining formalities, IT asset dispatch, and background verification.",
    STAGE_ONBOARDING_DAY: "Conduct Onboarding Day orientation, account provisioning, and team introductions.",
    STAGE_POST_ONBOARDING: "Manage ID card creation, HRMS doc approval, insurance & PF processing, and 1-week feedback.",
    STAGE_FEEDBACK_PROBATION: "Track 30/60/90-day milestone feedback surveys and probation completion."
}

# Overall Onboarding Statuses
STATUS_NOT_STARTED = "Not Started"
STATUS_IN_PROGRESS = "In Progress"
STATUS_COMPLETED = "Completed"

# Departments
DEPARTMENTS = ["Engineering", "Human Resources", "Data", "AI", "Finance", "Sales & Marketing", "Operations"]

# Cities
CITIES = ["Nagpur", "Pune", "Other (Customize)"]

# Locations
LOCATIONS = ["Nagpur", "Pune", "Bengaluru", "Hyderabad", "Mumbai", "Delhi NCR", "Remote"]

# Career Grades
GRADES = ["L1 - Associate", "L2 - Senior Associate", "L3 - Lead", "L4 - Manager", "L5 - Director"]
