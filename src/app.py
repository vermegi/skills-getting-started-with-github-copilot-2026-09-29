"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "waitlist": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "waitlist": []
    },
    "Basketball Team": {
        "description": "Practice basketball skills and compete in school games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": [],
        "waitlist": []
    },
    "Volleyball Club": {
        "description": "Develop volleyball skills and play competitively",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": [],
        "waitlist": []
    },
    "Art Club": {
        "description": "Explore drawing, painting, and other visual arts",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": [],
        "waitlist": []
    },
    "Drama Club": {
        "description": "Act, direct, and produce performances for the school community",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": [],
        "waitlist": []
    },
    "Debate Club": {
        "description": "Build public speaking and critical thinking skills through debate",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": [],
        "waitlist": []
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific discoveries",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": [],
        "waitlist": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity, or add them to the waitlist if it is full"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    waitlist = activity.setdefault("waitlist", [])

    # Check if the student is already signed up or waitlisted
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    if email in waitlist:
        raise HTTPException(status_code=400, detail="Student already on the waitlist for this activity")

    # Add student to the waitlist if the activity is full
    if len(activity["participants"]) >= activity["max_participants"]:
        waitlist.append(email)
        position = len(waitlist)
        return {
            "message": f"{activity_name} is full. Added {email} to the waitlist (position {position})",
            "status": "waitlisted",
            "waitlist_position": position,
        }

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}", "status": "enrolled"}


@app.delete("/activities/{activity_name}/signup")
def unregister_from_activity(activity_name: str, email: str):
    """Remove a student from an activity or its waitlist.

    When a participant unregisters, the first waitlisted student is auto-enrolled.
    """
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    waitlist = activity.setdefault("waitlist", [])

    if email in waitlist:
        waitlist.remove(email)
        return {
            "message": f"Removed {email} from the waitlist for {activity_name}",
            "promoted": None,
        }

    if email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Student is not signed up for this activity")

    activity["participants"].remove(email)

    promoted = None
    if waitlist and len(activity["participants"]) < activity["max_participants"]:
        promoted = waitlist.pop(0)
        activity["participants"].append(promoted)

    message = f"Unregistered {email} from {activity_name}"
    if promoted:
        message += f". {promoted} was enrolled from the waitlist"
    return {"message": message, "promoted": promoted}
