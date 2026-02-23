"""
Quickstart example – flask-admin-tabler
=======================================

Run this file directly to launch a minimal Flask-Admin application that uses
the Tabler UI theme::

    pip install flask-admin-tabler flask-sqlalchemy
    python examples/quickstart.py

Then open http://127.0.0.1:5000/admin/ in your browser.
"""

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

from flask_admin_tabler import TablerTheme

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me"  # replace with a secure random value in production
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"  # in-memory database

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


# 1. Create the theme
theme = TablerTheme()

# 2. Register it with the app BEFORE creating the Admin instance
theme.init_app(app)

# 3. Pass the theme to Admin
admin = Admin(app, name="Quickstart", theme=theme)
admin.add_view(ModelView(User, db.session))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Add some sample data if the table is empty
        if not User.query.first():
            db.session.add_all(
                [
                    User(username="alice", email="alice@example.com"),
                    User(username="bob", email="bob@example.com"),
                ]
            )
            db.session.commit()
    app.run()  # add debug=True locally if you want auto-reload
