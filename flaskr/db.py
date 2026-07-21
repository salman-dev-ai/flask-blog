import sqlite3 as sql
from datetime import datetime

import click 
from flask import current_app, g

def get_db():
    """
    Connect to the application's configured database. 
    The connection is unique for each request and will be reused if called again.
    """
    if 'db' not in g:
        g.db = sql.connect(
            current_app.config['DATABASE'],
            detect_types=sql.PARSE_DECLTYPES
        )
        g.db.row_factory = sql.Row

    return g.db

def close_db(e=None):
    """
    Close the database connection at the end of the request if it exists.
    'e' captures any exception/error that occurred during the request execution.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        # تم إصلاح الخطأ الإملائي هنا من uft8 إلى utf8
        db.executescript(f.read().decode('utf8'))

# 🔥 تعديل هام جداً: تم إضافة هذا السطر السحري الذي كان ينقص كودك
@click.command('init-db')
def init_db_command():
    """clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database successfully.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

sql.register_converter('timestamp', lambda v: datetime.fromisoformat(v.decode()))
