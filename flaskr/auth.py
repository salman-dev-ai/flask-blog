import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# Create an 'auth' Blueprint to group authentication-related routes
# All routes defined here will be prefixed with '/auth' (e.g., /auth/register)
bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Handle user registration for both GET (display form) and POST (submit data) requests."""
    if request.method == "POST":
        # Extract form inputs submitted by the user
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        error = None

        # Basic input validation
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                # Securely insert the new user into the database with a hashed password
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # Handle database constraint errors (e.g., duplicate username)
                error = f"User {username} is already registered."
            else:
                # Redirect to the login page upon successful registration
                return redirect(url_for("auth.login"))

        # Store the validation error message temporarily to show it on the template
        flash(error)

    # Render the registration HTML form for GET requests or when validation fails
    return render_template("auth/register.html")


# FIX: Added 'POST' method to the route tuple so the form submission can be processed
@bp.route("/login", methods=("GET", "POST"))
def login():
    """Handle user login session creation."""
    if request.method == "POST":
        # Extract login credentials from the submitted form
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        error = None

        # Query the database for the given username
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        # Verify credentials
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # Clear any existing session data and store the authenticated user's ID
            session.clear()
            session["user_id"] = user["id"]
            # Redirect to the main index page of the application
            return redirect(url_for("index"))

        flash(error)

    # FIX: Corrected from redirect() to render_template() to properly display the login page
    return render_template("auth/login.html")


# FIX: Changed from @bp.before_request to @bp.before_app_request
# This ensures it runs before ANY request to the application, not just within this blueprint
@bp.before_app_request
def load_logged_in_user():
    """Load the authenticated user's data from the database before processing any request."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        # Fetch full user details and attach them to the 'g' object for global request access
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/logout")
def logout():
    """Clear the user's session data and log them out of the application."""
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    """
    A custom decorator/middleware to protect routes from unauthenticated users.
    Redirects anonymous visitors to the login page.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # Block unauthorized access and redirect to the login screen
            return redirect(url_for("auth.login"))

        # Proceed to the requested view if the user is authenticated
        return view(**kwargs)

    return wrapped_view
