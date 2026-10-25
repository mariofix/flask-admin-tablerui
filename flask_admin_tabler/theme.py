import typing as t
from dataclasses import dataclass

from flask import Blueprint, Flask
from flask_admin.theme import Theme
from markupsafe import Markup


@dataclass
class TablerTheme(Theme):
    """
    Tabler 1.7.1 theme for Flask-Admin.

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
    theme: t.Literal["light", "dark", "nav-dark", "nav-color", "auto"] = "light"
    theme_primary: t.Literal[
        "blue",
        "azure",
        "indigo",
        "purple",
        "pink",
        "red",
        "orange",
        "yellow",
        "lime",
        "green",
        "teal",
        "cyan",
    ] = "blue"
    theme_base: t.Literal["gray", "neutral", "slate", "zinc", "stone", "mist"] = "gray"
    theme_font: t.Literal["sans-serif", "serif", "monospace", "comic"] = "sans-serif"
    theme_radius: t.Literal["0", "0.5", "1", "1.5", "2"] = "1"
    theme_layout: t.Literal["fluid", "boxed"] = "fluid"
    theme_navigation: t.Literal["condensed", "sidebar", "detached", "sticky"] = "condensed"

    @property
    def is_sidebar_layout(self) -> bool:
        return self.theme_navigation == "sidebar"

    @property
    def is_fluid_layout(self) -> bool:
        return self.theme_layout == "fluid"

    @property
    def is_boxed_layout(self) -> bool:
        return self.theme_layout == "boxed"

    @property
    def is_condensed_layout(self) -> bool:
        return self.theme_navigation == "condensed"

    @property
    def is_detached_navigation(self) -> bool:
        return self.theme_navigation == "detached"

    @property
    def is_sticky_navigation(self) -> bool:
        return self.theme_navigation == "sticky"

    @property
    def body_class(self) -> str:
        classes = []
        if self.is_fluid_layout:
            classes.append("layout-fluid")
        elif self.is_boxed_layout:
            classes.append("layout-boxed")
        return " ".join(classes)

    @property
    def container_class(self) -> str:
        return "container-fluid" if self.is_fluid_layout else "container-xl"

    @property
    def html_theme(self) -> str:
        """Resolve HTML data-bs-theme value."""
        if self.theme in ("nav-dark", "nav-color"):
            return "light"
        return self.theme

    @property
    def navbar_theme(self) -> str:
        """Resolve navbar theme attribute."""
        if self.theme == "nav-dark":
            return "dark"
        if self.theme == "nav-color":
            return "primary"
        if self.theme == "dark":
            return "dark"
        return "default"

    @staticmethod
    def bool_formatter(view: t.Any, value: t.Any, name: str) -> str:
        """Format boolean values using Tabler icons instead of FontAwesome."""
        icon = "circle-check" if value else "circle-minus"
        color = "text-success" if value else "text-secondary"
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
