import sqlite3
import os
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db(app):
    from flask import current_app
    
    @app.teardown_appcontext
    def close_db_at_end_of_request(e=None):
        close_db(e)
    
    with app.app_context():
        db = get_db()
        
        # Create tables
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
