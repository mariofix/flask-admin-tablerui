import pytest
from flask import Flask
from flask_admin import Admin
from flask_admin_tabler import TablerTheme


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True
    return app


def test_theme_defaults():
    theme = TablerTheme()
    assert theme.folder == "tabler"
    assert theme.base_template == "admin/base.html"


def test_theme_custom_base_template():
    theme = TablerTheme(base_template="my_base.html")
    assert theme.base_template == "my_base.html"


def test_init_app_registers_blueprint(app):
    theme = TablerTheme()
    theme.init_app(app)
    assert "flask_admin_tabler" in app.blueprints


def test_init_app_static_url(app):
    theme = TablerTheme()
    theme.init_app(app)
    with app.test_request_context():
        from flask import url_for

        url = url_for(
            "flask_admin_tabler.static", filename="admin/css/tabler/admin.css"
        )
        assert "flask_admin_tabler" in url
        assert "admin.css" in url


def test_admin_index_renders_tabler(app):
    theme = TablerTheme()
    theme.init_app(app)
    Admin(app, name="Test Admin", theme=theme)

    client = app.test_client()
    response = client.get("/admin/")
    assert response.status_code == 200
    # Tabler CSS is loaded from CDN
    assert b"tabler" in response.data


def test_admin_uses_tabler_base_template(app):
    theme = TablerTheme()
    theme.init_app(app)
    Admin(app, name="Test Admin", theme=theme)

    client = app.test_client()
    response = client.get("/admin/")
    assert response.status_code == 200
    # Tabler CDN link is present
    assert b"cdn.jsdelivr.net/npm/@tabler" in response.data
    # Bootstrap CDN should NOT be present (we replaced it)
    assert b"bootstrap.min.css" not in response.data
