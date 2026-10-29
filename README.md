# Membership System

A simple Flask web application where:
- **Admin** (you) has a pre-created account with full access.
- **Members** can create their own accounts via self-registration.

## Default Admin Credentials
- Username: `admin`
- Password: `admin123`
- **Important:** Change the admin password after first login (or edit the code).

## Setup & Run

1. Navigate to the folder:
   ```bash
   cd membership_app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open in browser: http://localhost:5000

## Features
- Members register themselves at `/register`
- Login for both admin and members
- Admin panel at `/admin` to view all members
- Separate roles: Admin vs Member

## Security Notes
- Change `SECRET_KEY` in `app.py`
- Change default admin password
- Use a proper production server (e.g., gunicorn) for deployment
- Consider adding email verification, password reset, etc. for production use
