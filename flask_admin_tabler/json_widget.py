"""flask_admin_tabler.json_widget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reusable JSON column support for Flask-Admin ModelViews.

Usage::

    from flask_admin_tabler import JsonColumnsMixin

    class MyView(JsonColumnsMixin, SecureModelView):
        json_columns = ["config", "metadata"]

The mixin automatically:
- Shows a compact badge in the list view for JSON objects/arrays.
- Shows pretty-printed, syntax-highlighted JSON in the details view.
- Adds a "Preview JSON" button in the edit / create forms.
- Minifies JSON values before saving (strips unnecessary whitespace).
"""

import json
import typing as t

from markupsafe import Markup, escape
from wtforms.widgets import TextArea

_HLJS = "/static/flask_admin_tabler/vendor/highlightjs"

# ---------------------------------------------------------------------------
# One-time per-page initialisation block.
# window.__jsonToolsInit guards against double-execution when multiple JSON
# fields or formatters inject this snippet on the same page.
# All DOM construction uses createElement/appendChild — no innerHTML.
# ---------------------------------------------------------------------------
_ONCE_SCRIPT = Markup(
    """<script>
(function () {
  if (window.__jsonToolsInit) return;
  window.__jsonToolsInit = true;

  /* ---- helpers --------------------------------------------------------- */
  function mkIcon(cls) {
    var el = document.createElement('i');
    el.className = cls;
    return el;
  }
  function loadLink(id, href) {
    var existing = document.getElementById(id);
    if (existing) return existing;
    var link = document.createElement('link');
    link.id = id; link.rel = 'stylesheet'; link.href = href;
    document.head.appendChild(link);
    return link;
  }
  function copyText(text, btn) {
    navigator.clipboard.writeText(text).then(function () {
      btn.textContent = '';
      btn.appendChild(mkIcon('ti ti-check text-success'));
      btn.appendChild(document.createTextNode(' Copied!'));
      setTimeout(function () {
        btn.textContent = '';
        btn.appendChild(mkIcon('ti ti-copy'));
      }, 1500);
    });
  }

  /* ---- inject styles --------------------------------------------------- */
  var st = document.createElement('style');
  st.textContent = [
    '.json-viewer{border-radius:4px;overflow:auto;font-size:.82em;margin:0;padding:1rem}',
    '.json-viewer-wrapper{position:relative}',
    '.json-copy-btn{position:absolute;top:.4rem;right:.4rem;opacity:.55;transition:opacity .15s;z-index:1}',
    '.json-copy-btn:hover{opacity:1}',
    '#json-preview-modal .json-viewer{max-height:70vh}',
  ].join('');
  document.head.appendChild(st);

  /* ---- inject modal (DOM only) ----------------------------------------- */
  if (!document.getElementById('json-preview-modal')) {
    /* hidden trigger for Bootstrap's data-bs-toggle delegation */
    var trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.id = 'json-preview-trigger';
    trigger.setAttribute('data-bs-toggle', 'modal');
    trigger.setAttribute('data-bs-target', '#json-preview-modal');
    trigger.style.display = 'none';
    trigger.setAttribute('aria-hidden', 'true');
    document.body.appendChild(trigger);

    var modal    = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'json-preview-modal';
    modal.tabIndex = -1;
    modal.setAttribute('aria-hidden', 'true');

    var dialog   = document.createElement('div');
    dialog.className = 'modal-dialog modal-xl modal-dialog-scrollable';

    var content  = document.createElement('div');
    content.className = 'modal-content';

    /* header */
    var hdr  = document.createElement('div');
    hdr.className = 'modal-header';
    var ttl  = document.createElement('h5');
    ttl.className = 'modal-title';
    ttl.appendChild(mkIcon('ti ti-code me-2'));
    ttl.appendChild(document.createTextNode('JSON Preview'));
    var xBtn = document.createElement('button');
    xBtn.type = 'button';
    xBtn.className = 'btn-close';
    xBtn.setAttribute('data-bs-dismiss', 'modal');
    hdr.appendChild(ttl);
    hdr.appendChild(xBtn);

    /* body */
    var bdy  = document.createElement('div');
    bdy.className = 'modal-body p-0';
    var pre  = document.createElement('pre');
    pre.className = 'json-viewer mb-0 rounded-0';
    var code = document.createElement('code');
    code.className = 'language-json';
    code.id = 'json-preview-code';
    pre.appendChild(code);
    bdy.appendChild(pre);

    /* footer */
    var ftr   = document.createElement('div');
    ftr.className = 'modal-footer';
    var cpBtn = document.createElement('button');
    cpBtn.type = 'button';
    cpBtn.id = 'json-preview-copy-btn';
    cpBtn.className = 'btn btn-sm btn-secondary';
    cpBtn.appendChild(mkIcon('ti ti-copy me-1'));
    cpBtn.appendChild(document.createTextNode('Copy'));
    cpBtn.addEventListener('click', function () {
      copyText(document.getElementById('json-preview-code').innerText, cpBtn);
    });
    var clBtn = document.createElement('button');
    clBtn.type = 'button';
    clBtn.className = 'btn btn-sm btn-secondary';
    clBtn.setAttribute('data-bs-dismiss', 'modal');
    clBtn.textContent = 'Close';
    ftr.appendChild(cpBtn);
    ftr.appendChild(clBtn);

    content.appendChild(hdr);
    content.appendChild(bdy);
    content.appendChild(ftr);
    dialog.appendChild(content);
    modal.appendChild(dialog);
    document.body.appendChild(modal);
  }

  /* ---- CSS themes ------------------------------------------------------ */
  var lightCss = loadLink('hljs-light', '%%HLJS%%/styles/googlecode.min.css');
  var darkCss  = loadLink('hljs-dark',  '%%HLJS%%/styles/monokai.min.css');
  function applyTheme() {
    var dark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    lightCss.disabled = dark;
    darkCss.disabled   = !dark;
  }
  applyTheme();
  new MutationObserver(applyTheme).observe(document.documentElement, {
    attributes: true, attributeFilter: ['data-bs-theme']
  });

  /* ---- load highlight.js then wire everything up ----------------------- */
  var hljsEl = document.createElement('script');
  hljsEl.src = '%%HLJS%%/highlight.min.js';
  hljsEl.onload = function () {
    /* highlight existing .json-viewer blocks and add copy buttons */
    document.querySelectorAll('.json-viewer code').forEach(function (c) {
      hljs.highlightElement(c);
      var p = c.parentElement;
      var w = document.createElement('div');
      w.className = 'json-viewer-wrapper';
      p.parentNode.insertBefore(w, p);
      w.appendChild(p);
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'json-copy-btn btn btn-sm btn-ghost-secondary';
      b.title = 'Copy JSON';
      b.appendChild(mkIcon('ti ti-copy'));
      b.addEventListener('click', function () { copyText(c.innerText, b); });
      w.appendChild(b);
    });

    /* event delegation for .json-preview-btn (edit / create forms) */
    document.addEventListener('click', function (e) {
      var btn = e.target.closest('.json-preview-btn');
      if (!btn) return;
      var field = document.getElementById(btn.dataset.jsonTarget);
      if (!field) return;
      var raw = field.value.trim();
      if (!raw) { alert('The value field is empty.'); return; }
      var parsed;
      try { parsed = JSON.parse(raw); }
      catch (err) { alert('Invalid JSON:\\n' + err.message); return; }
      if (typeof parsed !== 'object' || parsed === null) {
        alert('Value is not a JSON object or array.'); return;
      }
      var codeEl = document.getElementById('json-preview-code');
      codeEl.textContent = JSON.stringify(parsed, null, 2);
      delete codeEl.dataset.highlighted;
      hljs.highlightElement(codeEl);
      document.getElementById('json-preview-trigger').click();
    });
  };
  document.head.appendChild(hljsEl);
})();
</script>""".replace("%%HLJS%%", _HLJS)
)


# ---------------------------------------------------------------------------
# WTForms widget
# ---------------------------------------------------------------------------


class JsonTextAreaWidget:
    """WTForms widget that renders a textarea with a JSON preview button.

    Injects the one-time initialisation script on first use per page.
    """

    def __call__(self, field: t.Any, **kwargs: t.Any) -> Markup:
        textarea = TextArea()(field, **kwargs)
        btn = Markup(
            f'<button type="button"'
            f' class="btn btn-sm btn-secondary mt-1 json-preview-btn"'
            f' data-json-target="{escape(field.id)}">'
            f'<i class="ti ti-eye me-1"></i>Preview JSON</button>'
        )
        return textarea + btn + _ONCE_SCRIPT


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _parse_json_value(value: t.Any) -> dict | list | None:
    """Return a parsed JSON object/array from *value*, or None.

    Handles both:
    - ``str`` — Text columns that store JSON as a string (uses ``json.loads``).
    - ``dict`` / ``list`` — SQLAlchemy JSON columns that return Python objects directly.
    """
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str) and value:
        try:
            parsed = json.loads(value)
            if isinstance(parsed, (dict, list)):
                return parsed
        except (ValueError, TypeError):
            pass
    return None


# ---------------------------------------------------------------------------
# Column formatters
# ---------------------------------------------------------------------------


def json_list_formatter(view: t.Any, context: t.Any, model: t.Any, name: str) -> Markup:
    """List-view formatter: compact badge for JSON objects/arrays."""
    value = getattr(model, name, None)
    if value is None:
        return Markup("")
    parsed = _parse_json_value(value)
    if parsed is not None:
        tip = escape(json.dumps(parsed, separators=(",", ":"), ensure_ascii=False))
        if isinstance(parsed, dict):
            label = f"{{ {len(parsed)} keys }}"
            return Markup(f'<span class="badge bg-green-lt" title="{tip}">{escape(label)}</span>')
        label = f"[ {len(parsed)} items ]"
        return Markup(f'<span class="badge bg-blue-lt" title="{tip}">{escape(label)}</span>')
    # Plain string fallback
    text = str(value)
    if len(text) > 80:
        return Markup(f'<span title="{escape(text)}">{escape(text[:77])}…</span>')
    return Markup(escape(text))


def json_detail_formatter(view: t.Any, context: t.Any, model: t.Any, name: str) -> Markup:
    """Details-view formatter: pretty-printed, syntax-highlighted JSON."""
    value = getattr(model, name, None)
    if value is None:
        return Markup("")
    parsed = _parse_json_value(value)
    if parsed is not None:
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        return (
            Markup(f'<pre class="json-viewer"><code class="language-json">{escape(formatted)}</code></pre>')
            + _ONCE_SCRIPT
        )
    return Markup(escape(str(value)))


# ---------------------------------------------------------------------------
# ModelView mixin
# ---------------------------------------------------------------------------


class JsonColumnsMixin:
    """Mixin for Flask-Admin ModelView that adds JSON column support.

    Set ``json_columns`` to the names of columns that hold JSON values::

        class MyView(JsonColumnsMixin, ModelView):
            json_columns = ["config", "metadata"]

    The mixin merges formatters and widget args at instantiation time so it
    never mutates shared class-level dicts.  Any formatters or widget args
    already defined on the subclass take precedence (``setdefault`` semantics).
    """

    json_columns: t.ClassVar[list[str]] = []

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        if self.json_columns:
            # Copy existing dicts — never mutate shared class-level objects.
            cf = dict(getattr(self, "column_formatters", {}) or {})
            cfd = dict(getattr(self, "column_formatters_detail", {}) or {})
            fwa = dict(getattr(self, "form_widget_args", {}) or {})

            for col in self.json_columns:
                cf.setdefault(col, json_list_formatter)
                cfd.setdefault(col, json_detail_formatter)
                fwa.setdefault(col, {"widget": JsonTextAreaWidget()})

            # Set as instance attributes so Flask-Admin's __init__ picks them up.
            self.column_formatters = cf
            self.column_formatters_detail = cfd
            self.form_widget_args = fwa

        super().__init__(*args, **kwargs)

    def on_model_change(self, form: t.Any, model: t.Any, is_created: bool) -> None:
        """Minify JSON string values before persisting to the database.

        Only applies to Text columns that store JSON as a string.  Native
        dict/list values (SQLAlchemy JSON columns) are left untouched —
        SQLAlchemy serialises those itself.
        """
        for col in self.json_columns:
            value = getattr(model, col, None)
            if isinstance(value, str) and value:
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, (dict, list)):
                        setattr(
                            model,
                            col,
                            json.dumps(
                                parsed,
                                separators=(",", ":"),
                                ensure_ascii=False,
                            ),
                        )
                except (ValueError, TypeError):
                    pass
        super().on_model_change(form, model, is_created)
