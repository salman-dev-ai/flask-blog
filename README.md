<p align="center">
  <a href="README_AR.md">🌐 العربية</a>
</p>

<h1 align="center">
  📘 FaceBlog — Facebook-Inspired Social Blogging Application
</h1>

<p align="center">
  <strong>A production-grade social blogging platform built with Python 3, Flask, and SQLite.</strong>
  <br />
  Designed as a comprehensive learning resource for mastering full-stack web development
  with the Flask microframework, featuring a custom Facebook-inspired UI/UX theme.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask 3.0" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Pytest-100%25_Code_Coverage-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest 100% Coverage" />
  <img src="https://img.shields.io/badge/Waitress-Production_WSGI-4B0082?style=for-the-badge&logo=python&logoColor=white" alt="Waitress WSGI" />
  <img src="https://img.shields.io/badge/Flit-Modern_Packaging-FFD43B?style=for-the-badge&logo=python&logoColor=black" alt="Flit Packaging" />
</p>

<hr />

## 📑 Table of Contents

- [🚀 Core Features](#-core-features)
- [🧠 Complete Learning Roadmap](#-complete-learning-roadmap)
- [⚙️ Real-World Debugging & Engineering Challenges Solved](#️-real-world-debugging--engineering-challenges-solved)
- [📸 Visual Showcase](#-visual-showcase)
- [⚡ Quick Installation & Launch Guide](#-quick-installation--launch-guide)
- [📂 Project Structure Map](#-project-structure-map)
- [👨‍💻 Author & License](#-author--license)

<hr />

## 🚀 Core Features

FaceBlog delivers **six fundamental pillars** of modern web application engineering:

### 1. 🏭 Application Factory Pattern & Blueprint Architecture

The application is constructed using Flask's **Application Factory** pattern (`create_app()` in `flaskr/__init__.py`), which dynamically configures and returns a fully-initialized Flask instance. This pattern enables:

- **Environment-aware configuration** — Switching between development, testing, and production contexts by passing different configuration mappings.
- **Instance-folder isolation** — Sensitive configuration (like `SECRET_KEY`) lives in `instance/config.py`, excluded from version control.
- **Modular Blueprint structure** — Two distinct Blueprints organize the codebase:
  - `auth` Blueprint (prefix `/auth`) — Handles registration, login, logout, and session management.
  - `blog` Blueprint (no prefix) — Serves as the main application landing page with post creation, editing, and deletion.

```python
# flaskr/__init__.py — Application Factory Core
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)  # Load production secrets
    else:
        app.config.from_mapping(test_config)               # Load test overrides

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    app.register_blueprint(auth.bp)   # Register auth routes
    app.register_blueprint(blog.bp)   # Register blog routes
    app.add_url_rule("/", endpoint="index")  # Map root URL to 'index' endpoint

    return app
```

### 2. 🔐 Secure Authentication System

Authentication is implemented using **industry-standard security practices**:

- **Password hashing** via Werkzeug's `generate_password_hash()` and `check_password_hash()` — using the default (PBKDF2-SHA256) algorithm.
- **Session-based auth** — User ID stored in Flask's signed session cookie after successful login.
- **`@login_required` decorator** — A custom middleware that intercepts unauthenticated requests and redirects them to the login page.
- **`@bp.before_app_request`** — Automatically loads the authenticated user's data into Flask's `g` object before *every* request, making `g.user` globally accessible across all Blueprints.

```python
# flaskr/auth.py — Login session creation
@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()

        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)
    return render_template("auth/login.html")
```

### 3. ✍️ CRUD Blog Functionality

Full **Create, Read, Update, Delete** capabilities for blog posts:

- **Index page** — Displays all posts with author usernames, ordered by creation date (newest first), using a SQL JOIN query.
- **Create** — Protected by `@login_required`, validates title, uses parameterized INSERT queries.
- **Update** — Uses the `get_post()` helper to fetch the post, validate ownership, and render the edit form.
- **Delete** — A POST-only route that verifies ownership, then permanently removes the post.

```python
# flaskr/blog.py — Retrieve all posts with author information
@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username "
        "FROM post p JOIN user u ON p.author_id = u.id "
        "ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)
```

### 4. 🛡️ Author-Ownership Protection

A critical security feature ensuring **strict author-access control**:

- The `get_post(id, check_author=True)` function is used for both update and delete operations.
- It accepts a `check_author` parameter (defaults to `True`). When enabled, it checks if `post["author_id"] == g.user["id"]`.
- If a user attempts to modify or delete another author's post: **HTTP 403 Forbidden** is raised.
- If the post ID does not exist: **HTTP 404 Not Found** is raised.

```python
# flaskr/blog.py — Ownership verification
def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)  # Forbidden — not your post

    return post
```

### 5. 🎨 Facebook-Inspired UI/UX Theme

The frontend is fully styled with a **custom, modern Facebook aesthetic**:

- **CSS Custom Properties (Variables)** — Colors like `--fb-blue: #1877F2`, fonts, and spacing are globally defined for consistent theming.
- **Sticky Navigation Bar** — The top navigation stays fixed as users scroll, using `position: sticky; top: 0; z-index: 100`.
- **Feed Card Design** — Posts are rendered as individual white cards with subtle box-shadows, rounded corners, and proper spacing — mirroring Facebook's news feed layout.
- **Interactive States** — Hover effects on buttons, focus rings on form inputs, and smooth transitions for all interactive elements.
- **Responsive Layout** — Max-width container (960px for nav, 680px for feed) ensures the application renders beautifully on desktop while remaining mobile-friendly.

### 6. ✅ 100% Automated Test Coverage

The test suite achieves **100% code coverage** across the entire application:

- **`test_factory.py`** — Verifies the Application Factory creates instances correctly (testing mode toggle, hello page).
- **`test_db.py`** — Validates database initialization, connection reuse, and query execution.
- **`test_auth.py`** — Tests registration (successful + duplicate + validation), login (correct + incorrect credentials), and logout (session clearing).
- **`test_blog.py`** — Comprehensive coverage of index rendering, login-required protection, author-ownership enforcement, non-existent post handling, create/update/delete operations, and input validation.

```python
# tests/conftest.py — Test fixture with temporary database
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    yield app
    os.close(db_fd)
    os.unlink(db_path)
```

<hr />

## 🧠 Complete Learning Roadmap

This project serves as a **comprehensive educational resource** for junior-to-mid-level Python web developers. Here is exactly what you will learn:

### 📐 Web MVC Architecture Mapped to Flask

| Concept | Flask Implementation |
|---------|---------------------|
| **Model** | SQLite database layer (`db.py`) with `get_db()` managing connections |
| **View** | Jinja2 templates (`templates/`) rendering HTML with dynamic data |
| **Controller** | Flask route functions in `auth.py` and `blog.py` handling HTTP requests |
| **Router** | Blueprint registration and `app.add_url_rule()` for URL-to-endpoint mapping |
| **Middleware** | `@login_required` decorator and `before_app_request` hook |
| **Provider** | Application Factory providing configuration, database, and template context |

### 🗄️ Database Engineering with SQLite

- **Schema Design** — Two tables (`user` and `post`) with a foreign key relationship (`author_id` references `user.id`).
- **Safe Parameterized Queries** — All SQL uses `?` placeholders with tuple binding to prevent SQL injection attacks.
- **Lifecycle Management** — Connections are created per-request, stored in Flask's `g` object, and automatically closed via `app.teardown_appcontext(close_db)`.
- **Schema Initialization** — The `init-db` CLI command reads `schema.sql`, drops existing tables, recreates them, and seeds the database — all through a single Click command.
- **Timestamp Handling** — Custom converter registered: `sql.register_converter('timestamp', lambda v: datetime.fromisoformat(v.decode()))`.

```sql
-- flaskr/schema.sql — Database schema
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
```

### 🎨 Jinja2 Template Inheritance

- **`base.html`** — The skeleton template defining the HTML structure, navigation bar, flash message system, and **block placeholders** (`{% block title %}`, `{% block header %}`, `{% block content %}`).
- **Child Templates** — Each page (login, register, index, create, update) extends `base.html` and overrides specific blocks.
- **Conditional Rendering** — Navigation dynamically shows "Log In" / "Register" for anonymous users, and "Log Out" with the username for authenticated users: `{% if g.user %} ... {% else %} ... {% endif %}`.
- **Scoped Loop Context** — The `for` loop in Jinja2 maintains its own scope, preventing variable leakage between iterations — a common source of bugs for beginners.

```html
<!-- flaskr/templates/base.html — Parent layout template -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}{% endblock %}- FaceBlog</title>
    <link rel="stylesheet" href="{{url_for('static',filename='style.css')}}" />
    <link rel="icon" type="image/x-icon" sizes="any" href="{{ url_for('static', filename='favicon.ico') }}">
  </head>
  <body>
    <nav>
      <h1>FaceBlog</h1>
      <ul>
        {% if g.user %}
        <li><span>{{ g.user['username'] }}</span></li>
        <li><a href="{{ url_for('auth.logout') }}">Log Out</a></li>
        {% else %}
        <li><a href="{{ url_for('auth.register') }}">Register</a></li>
        <li><a href="{{ url_for('auth.login') }}">Log In</a></li>
        {% endif %}
      </ul>
    </nav>
    <section class="content">
      <header>{% block header %}{% endblock %}</header>
      {% for message in get_flashed_messages() %}
      <div class="flash">{{ message }}</div>
      {% endfor %}
      {% block content %}{% endblock %}
    </section>
  </body>
</html>
```

### 📦 Modern Python Packaging with Flit

- **`pyproject.toml`** — The modern Python packaging standard, replacing the legacy `setup.py` approach.
- **Flit as Build Backend** — A lightweight, fast packaging tool that works seamlessly with Flask applications.
- **Module Name Mapping** — The `[tool.flit.module]` section explicitly maps the internal `flaskr` folder to the public `faceblog` package name — a critical link that beginners often miss.

```toml
# pyproject.toml — Modern Python packaging configuration
[project]
name = "faceblog"                   # Public package name on PyPI
version = "1.0.0"
description = "A Facebook-inspired social blogging application built with Python and Flask."
dependencies = [
    "flask",                         # Core web framework
    "waitress",                      # Production WSGI server
]

[build-system]
requires = ["flit_core<4"]
build-backend = "flit_core.buildapi"

[tool.flit.module]
name = "flaskr"  # ⚡ Maps the internal `flaskr` folder to the `faceblog` package

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["flaskr"]
```

<hr />

## ⚙️ Real-World Debugging & Engineering Challenges Solved

This section documents **four real bugs** encountered during development, each representing a classic pitfall in Python/Flask development. Understanding these will save you hours of debugging.

### 🔥 Bug #1: Missing Spaces in Multi-line SQL Strings

**Symptom:** SQLite raises `OperationalError: near "WHERE" syntax error` when executing an UPDATE query.

**Root Cause:** Python's implicit string concatenation (`"string1" "string2"`) does **not** insert a space between the concatenated parts. The original code:

```python
# ❌ BUG: Missing space before 'WHERE'
db.execute(
    "UPDATE post SET title = ?, body = ?" "WHERE id = ?", 
    (title, body, id)
)
```

This compiles to: `UPDATE post SET title = ?, body = ?WHERE id = ?` — producing invalid SQL.

**✅ The Fix:** Add a leading space before `WHERE`:

```python
# ✅ FIX: Space before 'WHERE'
db.execute(
    "UPDATE post SET title = ?, body = ?" " WHERE id = ?",  # Note the space!
    (title, body, id)
)
```

**📚 Lesson:** Python concatenates adjacent string literals without any separator. Always verify SQL string composition when using multi-line formatting.

---

### 🔥 Bug #2: Endpoint Route Conflict (KeyError: 'index')

**Symptom:** After registering both `auth` and `blog` Blueprints, calling `url_for("index")` raises `KeyError: 'index'`.

**Root Cause:** The `auth` Blueprint's `login()` and `logout()` functions internally call `url_for("index")`, expecting it to point to the root URL `/`. However, the `blog` Blueprint's index route (`@bp.route("/")`) creates an endpoint named `blog.index`, not `index`. Without an explicit alias, Flask has no endpoint registered under the plain name `index`.

```python
# ❌ BUG: url_for("index") fails because no route is named 'index'
app.register_blueprint(auth.bp)
app.register_blueprint(blog.bp)  # Creates 'blog.index' endpoint, not 'index'
```

**✅ The Fix:** Register the root URL with an explicit `endpoint` parameter:

```python
# ✅ FIX: Map root URL to the 'index' endpoint name
app.add_url_rule("/", endpoint="index")
```

**📚 Lesson:** The ordering of `register_blueprint()` and `add_url_rule()` matters. When you register a Blueprint, its routes are namespaced (`blog.index`). To create a non-namespaced alias, use `app.add_url_rule()` *after* all Blueprints are registered.

---

### 🔥 Bug #3: Flit Packaging ValueError — No file/folder found for module

**Symptom:** Running `flit install` or `pip install -e .` fails with `ValueError: No file/folder found for module 'faceblog'`.

**Root Cause:** By default, Flit looks for a top-level directory or file that matches the `[project].name` (`faceblog`). However, the actual source code lives inside the `flaskr/` directory, not `faceblog/`. Flit cannot automatically resolve the mapping.

```toml
# ❌ BUG: Flit looks for 'faceblog/' folder which doesn't exist
[project]
name = "faceblog"    # Flit searches for ./faceblog/ — missing!
```

**✅ The Fix:** Explicitly tell Flit which module directory to package:

```toml
# ✅ FIX: Declare the module name mapping explicitly
[tool.flit.module]
name = "flaskr"  # Tells Flit: "package 'flaskr/', publish as 'faceblog'"
```

**📚 Lesson:** The `[tool.flit.module]` section acts as an **architectural link** between your internal folder structure and your public package name. Always configure this when your source directory name differs from your package name.

---

### 🔥 Bug #4: Favicon/SVG Aggressive Browser Caching

**Symptom:** After replacing the favicon file, the browser stubbornly displays the old icon despite multiple refreshes. The new favicon appears only after clearing the entire browser cache.

**Root Cause:** Browsers aggressively cache favicon files, often ignoring standard cache-control headers. Additionally, SVG favicons require specific `<link>` attributes to render correctly across different browsers.

```html
<!-- ❌ BUG: Browsers cache the old favicon stubbornly -->
<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
```

**✅ The Fix:** Add the `sizes="any"` attribute, which tells browsers to treat the favicon as a fallback for all sizes, effectively bypassing cache locks:

```html
<!-- ✅ FIX: sizes="any" forces browsers to re-read the favicon -->
<link rel="icon" type="image/x-icon" sizes="any" href="{{ url_for('static', filename='favicon.ico') }}">
```

**Hard Refresh Strategies:**
- **Chrome/Edge:** `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- **Firefox:** `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
- **Developer Tools:** Right-click the refresh button → "Empty Cache and Hard Reload"

**📚 Lesson:** Favicon caching is one of the most aggressive caching mechanisms in modern browsers. The `sizes="any"` attribute acts as a cache-busting signal. For SVG favicons specifically, always include `type="image/svg+xml"` and `sizes="any"` to ensure cross-browser compatibility.

<hr />

## 📸 Visual Showcase

> **Note:** Screenshots are auto-captured and stored in the `flaskr/static/img/` directory.
> Replace the placeholder filenames below with your actual screenshots.

### 📰 Main Post Feed
The Facebook-inspired card-based feed layout displaying all blog posts with author information and timestamps.

<p align="center">
  <img src="flaskr/static/img/img (1).png" alt="FaceBlog Main Feed — Card-based post layout" width="80%" />
</p>

### 🔑 Login / Register View
The authentication interface with a clean, centered form design consistent with the Facebook theme.

<p align="center">
  <img src="flaskr/static/img/img (2).png" alt="FaceBlog Login Page — Facebook-themed authentication form" width="80%" />
</p>

### ✏️ Create & Edit Post Interfaces
The content creation and editing forms, featuring Facebook-styled input fields and action buttons.

<p align="center">
  <img src="flaskr/static/img/img (3).png" alt="FaceBlog Create/Edit Post — Content management forms" width="80%" />
</p>

### 🧪 Pytest 100% Coverage Report
Automated test suite achieving complete code coverage across the entire application.

<p align="center">
  <img src="flaskr/static/img/img (4).png" alt="Pytest Coverage Report — 100% code coverage verification" width="80%" />
</p>

<hr />

## ⚡ Quick Installation & Launch Guide

Follow these steps to set up and run FaceBlog on your local machine.

### Prerequisites

- **Python 3.9+** installed on your system
- **Git** (optional, for cloning the repository)
- **pip** (Python package installer)

### Step 1: Clone the Repository

```bash
# Clone from GitHub (or copy the project folder manually)
git clone https://github.com/salman-dev-ai/flask-blog.git
cd flask-blog
```

### Step 2: Create a Virtual Environment

```bash
# Create an isolated Python environment for this project
# Windows:
python -m venv venv

# macOS / Linux:
python3 -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### Step 3: Install the Package (Editable Mode)

```bash
# Install the project and its dependencies in editable/development mode.
# The '-e .' flag tells pip to use the current directory's pyproject.toml.
# Editable mode means code changes take effect immediately without reinstalling.
pip install -e .
```

### Step 4: Create the Secret Key Configuration

```bash
# Create the instance directory and configuration file for production secrets
# The SECRET_KEY is used by Flask to cryptographically sign session cookies.

# For Windows (Command Prompt):
mkdir instance
echo SECRET_KEY='your-production-secret-key-here' > instance\config.py

# For macOS / Linux:
mkdir -p instance
echo "SECRET_KEY='your-production-secret-key-here'" > instance/config.py

# 🔐 IMPORTANT: Generate a strong key using Python:
# python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: Initialize the Database

```bash
# Create the SQLite database and apply the schema defined in flaskr/schema.sql.
# This command registers the 'init-db' CLI command via Click, as defined in db.py.
flask --app flaskr init-db
```

### Step 6: Run the Automated Test Suite

```bash
# Execute all tests with code coverage analysis
# The '--branch' flag measures branch coverage (if/else paths).
# The 'source = ["flaskr"]' config in pyproject.toml limits coverage to application code.

# Run pytest with coverage:
coverage run -m pytest

# View the coverage report in the terminal:
coverage report

# Generate an HTML coverage report (opens in browser):
coverage html
# Then open: htmlcov/index.html

# For a quick test run without coverage:
pytest -v
```

### Step 7: Start the Production WSGI Server

```bash
# Launch the application using Waitress, a production-grade WSGI server.
# The '--call' flag tells Waitress to invoke flaskr:create_app() as a factory function.
# This is significantly more robust than Flask's built-in development server.

waitress-serve --call "flaskr:create_app"
```

### Step 8: Access the Application

```
Open your web browser and navigate to:

    👉 http://localhost:8080

You should see the FaceBlog homepage with the Facebook-themed interface!
```

### 🐍 Quick Start (One-Liner for Development)

```bash
# For development purposes only (not for production):
flask --app flaskr --debug run
```

<hr />

## 📂 Project Structure Map

```
faceblog/                              # Project root (published as 'faceblog')
│
├── pyproject.toml                     # Modern Python packaging config (Flit)
├── MANIFEST.in                        # Inclusion rules for source distribution
├── hello.py                           # Quick hello-world test script
├── info                               # Project notes / metadata
├── .gitignore                         # Git exclusion rules
├── .coverage                          # Coverage data file (generated by pytest-cov)
│
├── flaskr/                            # Main application package (internal name)
│   ├── __init__.py                    # Application Factory: create_app()
│   ├── auth.py                        # Authentication Blueprint (register/login/logout)
│   ├── blog.py                        # Blog Blueprint (index/create/update/delete)
│   ├── db.py                          # Database layer (get_db, init_db, close_db, CLI)
│   ├── schema.sql                     # SQL schema (user + post tables)
│   │
│   ├── templates/                     # Jinja2 HTML templates
│   │   ├── base.html                  # Base layout with nav, blocks, flash messages
│   │   ├── auth/
│   │   │   ├── register.html          # User registration form
│   │   │   └── login.html             # User login form
│   │   └── blog/
│   │       ├── index.html             # Main feed — lists all posts
│   │       ├── create.html            # New post creation form
│   │       └── update.html            # Post editing form
│   │
│   ├── static/                        # Static assets (CSS, images, favicon)
│   │   ├── style.css                  # Facebook-inspired theme (custom FB properties)
│   │   ├── favicon.ico                # Browser tab icon
│   │   └── img/                       # Application screenshots directory
│   │       ├── img (1).png            # Feed preview screenshot
│   │       ├── img (2).png            # Auth preview screenshot
│   │       ├── img (3).png            # CRUD preview screenshot
│   │       └── img (4).png            # Test coverage screenshot
│
├── instance/                          # Instance folder (excluded from version control)
│   └── config.py                      # Production SECRET_KEY (auto-loaded by factory)
│
└── tests/                             # Automated test suite (Pytest)
    ├── conftest.py                    # Fixtures: app, client, runner, auth
    ├── data.sql                       # Test seed data (dummy users + posts)
    ├── test_factory.py                # Factory creation and hello page tests
    ├── test_db.py                     # Database initialization and query tests
    ├── test_auth.py                   # Auth flow tests (register, login, logout, validation)
    └── test_blog.py                   # Blog CRUD tests (permissions, validation, operations)
```

<hr />

## 👨‍💻 Author & License

**FaceBlog** was engineered and documented by **Salman Soft** (مهندس سلمان سوفت) — a passionate software engineer and mentor dedicated to crafting production-grade educational resources for the Python and Flask community.

| Detail | Information |
|--------|-------------|
| **Author** | Eng-Salman Soft   |
| **Role** |  Full-Stack |
| **License** | MIT License — Free for personal and commercial use |
| **Repository** | [github.com/salman-dev-ai/flask-blog](https://github.com/salman-dev-ai/flask-blog) |
| **Built With** | ❤️ Python 3, Flask 3.0, SQLite, Waitress, Pytest, Flit |

---

<p align="center">
  <strong>⭐ If you found this project educational, please give it a star on GitHub!</strong>
  <br />
  <em>"The best way to learn is to build. The best way to teach is to show the struggle."</em>
  <br />
  — Salman Soft
</p>
