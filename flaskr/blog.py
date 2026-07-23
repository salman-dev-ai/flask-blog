from flask import Blueprint, flash, g, redirect, render_template, request, url_for

# Used to raise clean HTTP exceptions (like 404 Not Found or 403 Forbidden) and stop execution
from werkzeug.exceptions import abort

# Import the custom authentication decorator to protect blog-writing/editing views
from flaskr.auth import login_required

# Import the database helper to fetch, create, and manage blog posts
from flaskr.db import get_db

# Create a 'blog' Blueprint to organize all blog-related routes (index, create, update, delete)
# Note: It has no url_prefix, making the blog views act as the main landing pages of the application
bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """
    Retrieve all blog posts from the database with author usernames,
    ordered from newest to oldest, and render them in the index template.
    """
    db = get_db()

    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username "
        "FROM post p JOIN user u ON p.author_id = u.id "
        "ORDER BY created DESC"
    ).fetchall()

    # Pass the database records to the HTML template
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """
    Handle creation of a new blog post.
    Accepts GET requests to show the form, and POST requests to save data.
    """
    if request.method == "POST":
        # Retrieve form input data sanitized by Flask/Werkzeug
        title = request.form["title"]
        body = request.form["body"]
        error = None

        # Validate that the title field is not empty
        if not title:
            error = "Title is required."

        # If a validation error exists, notify the user using flash flashing system
        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Execute SQL safe query with tuple binding to prevent SQL injection
            db.execute(
                "INSERT INTO post (title, body, author_id)"
                " VALUES (?, ?, ?)",  # Added the missing comma right below
                (title, body, g.user["id"]),
            )
            # Commit the transaction to save changes into SQLite database permanently
            db.commit()

            # Redirect to the main homepage upon successful post creation
            return redirect(url_for("blog.index"))

    # Render the creation form template for plain GET requests (Fixed indentation)
    return render_template("blog/create.html")


def get_post(id, check_author=True):
    """
    Helper function to safely fetch a single post by ID from the database.
    Optionally enforces authorship validation to protect update/delete actions.
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (
                id,
            ),  # Trailing comma is required to define a single-element tuple in Python
        )
        .fetchone()
    )

    # Raise a 404 error response if no matching post is found in the database
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    # Enforce access control: Raise a 403 Forbidden if user is modifying someone else's post
    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update and delete blog"""
    post = get_post(id)
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "title is required"
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?" "WHERE id = ?", (title, body, id)
            )
            db.commit()

            return redirect(url_for("blog.index"))
    

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
