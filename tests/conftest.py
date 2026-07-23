import os
import tempfile
import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

# Read the SQL seeding data file which will populate our test database
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    """
    Creates and configures a brand new application instance for each test.
    It generates a temporary database file and destroys it when done.
    """
    # Create a secure temporary file descriptor and path for the testing database
    db_fd, db_path = tempfile.mkstemp()

    # Call the application factory with testing configurations overridden
    app = create_app({
        'TESTING': True,        # Tells Flask it is in testing mode (enables better error tracking)
        'DATABASE': db_path,     # Points to the temporary database file instead of dev.sqlite
    })

    # Initialize the test database schema and seed it with dummy users and posts
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app  # The application instance is passed to the test here

    # Cleanup phase: executed after the test finishes running
    os.close(db_fd)       # Close the temporary file connection
    os.unlink(db_path)    # Permanently delete the temporary database file from disk


@pytest.fixture
def client(app):
    """
    A test client that simulates an HTTP request-response cycle without running a real server.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    A CLI runner that can invoke Click commands registered within the Flask application.
    """
    return app.test_cli_runner()


class AuthActions(object):
    """
    Helper class to simulate login and logout user interaction inside the test environment.
    """
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """
    Exposes AuthActions as a reusable fixture across multiple authentication and blog tests.
    """
    return AuthActions(client)
