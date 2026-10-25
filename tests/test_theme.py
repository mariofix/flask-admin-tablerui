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
    assert theme.theme == "light"
    assert theme.theme_primary == "blue"
    assert theme.theme_base == "gray"
    assert theme.theme_font == "sans-serif"
    assert theme.theme_radius == "1"
    assert theme.theme_layout == "fluid"
    assert theme.theme_navigation == "condensed"
    assert theme.is_fluid_layout is True
    assert theme.is_condensed_layout is True
    assert theme.container_class == "container-fluid"
    assert theme.body_class == "layout-fluid"


def test_theme_custom_base_template():
    theme = TablerTheme(base_template="my_base.html")
    assert theme.base_template == "my_base.html"


def test_theme_custom_configurations():
    theme = TablerTheme(
        theme="auto",
        theme_primary="yellow",
        theme_base="mist",
        theme_layout="boxed",
        theme_navigation="sidebar",
    )
    assert theme.theme == "auto"
    assert theme.html_theme == "auto"
    assert theme.theme_primary == "yellow"
    assert theme.theme_base == "mist"
    assert theme.is_boxed_layout is True
    assert theme.is_sidebar_layout is True
    assert theme.container_class == "container-xl"
    assert theme.body_class == "layout-boxed"


def test_theme_navbar_variants():
    theme_nav_dark = TablerTheme(theme="nav-dark")
    assert theme_nav_dark.html_theme == "light"
    assert theme_nav_dark.navbar_theme == "dark"

    theme_nav_color = TablerTheme(theme="nav-color")
    assert theme_nav_color.html_theme == "light"
    assert theme_nav_color.navbar_theme == "primary"

    theme_dark = TablerTheme(theme="dark")
    assert theme_dark.html_theme == "dark"
    assert theme_dark.navbar_theme == "dark"

    theme_light = TablerTheme(theme="light")
    assert theme_light.html_theme == "light"
    assert theme_light.navbar_theme == "default"


def test_theme_layout_and_navigation():
    theme_sidebar = TablerTheme(theme_navigation="sidebar")
    assert theme_sidebar.is_sidebar_layout is True
    assert theme_sidebar.theme_navigation == "sidebar"

    theme_boxed = TablerTheme(theme_layout="boxed")
    assert theme_boxed.is_boxed_layout is True
    assert theme_boxed.theme_layout == "boxed"

    theme_condensed = TablerTheme(theme_navigation="condensed")
    assert theme_condensed.is_condensed_layout is True
    assert theme_condensed.theme_navigation == "condensed"

    theme_nav = TablerTheme(theme_navigation="detached")
    assert theme_nav.is_detached_navigation is True

    theme_sticky = TablerTheme(theme_navigation="sticky")
    assert theme_sticky.is_sticky_navigation is True


def test_bool_formatter():
    rendered_true = TablerTheme.bool_formatter(None, True, "is_active")
    assert "ti-circle-check" in str(rendered_true)
    assert "text-success" in str(rendered_true)

    rendered_false = TablerTheme.bool_formatter(None, False, "is_active")
    assert "ti-circle-minus" in str(rendered_false)
    assert "text-secondary" in str(rendered_false)


def test_init_app_registers_blueprint(app):
    theme = TablerTheme()
    theme.init_app(app)
    assert "flask_admin_tabler" in app.blueprints


def test_init_app_static_url(app):
    theme = TablerTheme()
    theme.init_app(app)
    with app.test_request_context():
        from flask import url_for

        url = url_for("flask_admin_tabler.static", filename="admin/css/tabler/admin.css")
        assert "flask_admin_tabler" in url
        assert "admin.css" in url


def test_admin_index_renders_tabler(app):
    theme = TablerTheme()
    theme.init_app(app)
    Admin(app, name="Test Admin", theme=theme)

    client = app.test_client()
    response = client.get("/admin/")
    assert response.status_code == 200
    assert b"tabler" in response.data


def test_admin_uses_tabler_base_template(app):
    theme = TablerTheme()
    theme.init_app(app)
    Admin(app, name="Test Admin", theme=theme)

    client = app.test_client()
    response = client.get("/admin/")
    assert response.status_code == 200
    # Local static files are loaded
    assert b"tabler/css/tabler.min.css" in response.data
    # Standalone Bootstrap bundle should NOT be present (Tabler bundles it)
    assert b"bootstrap.bundle.min.js" not in response.data
    assert b"bootstrap.min.css" not in response.data


def test_admin_tabler_icons_css_loaded(app):
    theme = TablerTheme()
    theme.init_app(app)
    Admin(app, name="Test Admin", theme=theme)

    client = app.test_client()
    response = client.get("/admin/")
    assert response.status_code == 200
    assert b"tabler-icons.min.css" in response.data
