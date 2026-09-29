# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Capacity enforcement: when an activity is full, new signups join a waitlist
- Automatic enrollment of the first waitlisted student when a participant unregisters

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity (joins the waitlist if full). Response `status` is `enrolled` or `waitlisted`; waitlisted responses include `waitlist_position` |
| DELETE | `/activities/{activity_name}/signup?email=student@mergington.edu` | Unregister from an activity or its waitlist. Response `promoted` is the email auto-enrolled from the waitlist, or `null` |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up
   - Waitlist of student emails (in order) waiting for a spot

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
