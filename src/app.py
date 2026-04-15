"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Request, Response, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from starlette_csrf import CSRFMiddleware, csrf_protect, csrf_token
from itsdangerous import Signer, BadSignature
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Add CORS middleware for security (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add CSRF middleware
app.add_middleware(
    CSRFMiddleware,
    secret="super-secret-key",  # In production, use a secure random key
    cookie_name="csrf_token",
    field_name="csrf_token",
    safe_methods=["GET", "HEAD", "OPTIONS"],
)

# Session signer for secure cookies
signer = Signer("another-secret-key")

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
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}



# Helper to get or set a signed session cookie
def get_session_email(request: Request):
    session_cookie = request.cookies.get("session")
    if session_cookie:
        try:
            email = signer.unsign(session_cookie).decode()
            return email
        except BadSignature:
            return None
    return None

def set_session_email(response: Response, email: str):
    signed_email = signer.sign(email.encode()).decode()
    response.set_cookie("session", signed_email, httponly=True, samesite="Lax")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities



# CSRF-protected signup endpoint
@app.post("/activities/{activity_name}/signup")
@csrf_protect
async def signup_for_activity(
    activity_name: str,
    request: Request,
    response: Response,
    email: str = Form(...),
    csrf_token: str = Form(...),
):
    """Sign up a student for an activity (CSRF protected)"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    set_session_email(response, email)
    return {"message": f"Signed up {email} for {activity_name}"}



# CSRF-protected unregister endpoint
@app.delete("/activities/{activity_name}/unregister")
@csrf_protect
async def unregister_from_activity(
    activity_name: str,
    request: Request,
    response: Response,
    email: str = Form(...),
    csrf_token: str = Form(...),
):
    """Unregister a student from an activity (CSRF protected)"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    set_session_email(response, email)
    return {"message": f"Unregistered {email} from {activity_name}"}

# Endpoint to get CSRF token for forms
@app.get("/csrf-token")
async def get_csrf_token(request: Request):
    token = csrf_token(request)
    return {"csrf_token": token}
