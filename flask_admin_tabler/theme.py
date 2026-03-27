import typing as t
from dataclasses import dataclass

from flask import Blueprint, Flask
from flask_admin.theme import Theme
from markupsafe import Markup


@dataclass
class TablerTheme(Theme):
    """
    Tabler 1.4.0 theme for Flask-Admin.

    Ships Tabler UI assets locally (CSS, JS, icon webfonts) so no CDN is
    required.  All Flask-Admin templates (base, layout, model views, file
    views, etc.) have been copied from the upstream bootstrap4 bundle and
    rewritten for Tabler / Bootstrap 5.  They live under
    ``flask_admin_tabler/templates/tabler/admin/``.

    ``Theme.folder`` is set to ``"tabler"`` so that Flask-Admin's admin
    blueprint looks inside ``templates/tabler/`` for every template it
    renders (index.html, model/list.html, …).  Registering our own package
    blueprint **before** Flask-Admin's admin blueprint further guarantees
    that our Tabler templates win when two blueprints ship the same path.

    Usage::

        from flask_admin_tabler import TablerTheme

        theme = TablerTheme()
        theme.init_app(app)  # call before Admin(app, ...)
        admin = Admin(app, name="my app", theme=theme)

    Or with a custom base template::

        theme = TablerTheme(base_template="my_base.html")
        theme.init_app(app)
        admin = Admin(app, name="my app", theme=theme)
    """

    # ``folder`` tells Flask-Admin which sub-directory of ``templates/`` to
    # use for the admin blueprint.  We ship a complete set of templates under
    # ``templates/tabler/admin/`` so Flask-Admin resolves them directly.
    folder: str = "tabler"
    base_template: str = "admin/base.html"

    # Tabler UI theme settings — map directly to data-bs-* HTML attributes.
    # Defaults match Tabler's own defaults so existing deployments are unaffected.
    theme: str = "light"  # "light" | "dark"
    theme_primary: str = "blue"  # "blue" | "lime" | "azure" | "indigo" | …
    theme_base: str = "gray"  # "gray" | "neutral" | "slate" | "zinc" | "stone"
    theme_font: str = "sans-serif"  # "sans-serif" | "serif" | "monospace" | "comic"
    theme_radius: str = "1"  # "0" | "0.5" | "1" | "1.5" | "2"

    @staticmethod
    def bool_formatter(view: t.Any, value: t.Any, name: str) -> str:
        """Format boolean values using Tabler icons instead of FontAwesome."""
        icon = "circle-check" if value else "circle-minus"
        color = "text-success" if value else "text-muted"
        label = f"{name}: {'true' if value else 'false'}"
        return Markup(f'<span class="ti ti-{icon} {color}" title="{label}"></span>')

    def init_app(self, app: Flask) -> None:
        """Register Tabler theme templates and static files with the Flask app.

        Must be called *before* creating the ``Admin`` instance.  Flask
        resolves blueprint templates in registration order, so registering
        this blueprint first guarantees our Tabler templates take priority
        over Flask-Admin's default Bootstrap ones.
        """
        bp = Blueprint(
            "flask_admin_tabler",
            __name__,
            template_folder="templates/tabler",
            static_folder="static",
            static_url_path="/static/flask_admin_tabler",
        )
        app.register_blueprint(bp)
