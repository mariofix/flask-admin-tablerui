# flask-admin-tabler

A [Tabler UI](https://tabler.io/) theme for [Flask-Admin](https://github.com/pallets-eco/flask-admin).

## Installation

```shell
pip install flask-admin-tabler
```

## Usage

Call `theme.init_app(app)` **before** creating the `Admin` instance so that the
Tabler templates are registered with higher priority than Flask-Admin's default
Bootstrap ones.

```python
from flask import Flask
from flask_admin import Admin
from flask_admin_tabler import TablerTheme

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me"

theme = TablerTheme()
theme.init_app(app)          # must come before Admin(app, ...)

admin = Admin(app, name="My App", theme=theme)
```

That's it - navigating to `/admin/` will now render the Tabler UI instead of
the default Bootswatch theme.

A fully runnable example (including a SQLAlchemy model and sample data) is
available in [`examples/quickstart.py`](examples/quickstart.py):

```shell
pip install flask-admin-tabler flask-sqlalchemy
python examples/quickstart.py
# open http://127.0.0.1:5000/admin/
```

## Versioning

Releases/tags are matched to each tabler version.
