#!/usr/bin/env python
"""Dungeon Keeper: erzeugt die dungeon-map.md, eine Markdown-Tabelle URL -> Route-Datei -> Template(s) aus der Flask-App.

Aufruf im Projektverzeichnis:  python docs/dungeon_keeper.py > dungeon-map.md
"""
import ast
import html
import inspect
import os
import sys
import textwrap

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # docs/..
os.chdir(PROJECT_DIR)  # webapp/config.py liest config.json relativ zum cwd
sys.path.insert(0, PROJECT_DIR)
from webapp import create_app  # noqa: E402

ROOT = os.path.join(PROJECT_DIR, "webapp")
SKIP_PREFIXES = ("admin", "static")


def templates_of(func):
    """Template-Namen aus render_template("...")-Aufrufen im Funktionsquelltext."""
    func = inspect.unwrap(func)
    try:
        src = textwrap.dedent(inspect.getsource(func))
    except (OSError, TypeError):
        return []
    names = []
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "id", getattr(node.func, "attr", None)) == "render_template"
                and node.args and isinstance(node.args[0], ast.Constant)):
            names.append(node.args[0].value)
    return list(dict.fromkeys(names))


def template_path(app, endpoint, name):
    """Sucht das Template im Blueprint- bzw. App-Templateordner."""
    bp_name = endpoint.split(".")[0] if "." in endpoint else None
    folders = []
    bp = app.blueprints.get(bp_name)
    if bp and bp.template_folder:
        folders.append(os.path.join(bp.root_path, bp.template_folder))
    folders += [os.path.join(app.root_path, app.template_folder)]
    folders += [os.path.join(b.root_path, b.template_folder)
                for b in app.blueprints.values() if b.template_folder]
    for folder in folders:
        p = os.path.join(folder, name)
        if os.path.exists(p):
            return os.path.relpath(p, ROOT)
    return f"{name} (?)"


def main():
    app = create_app()
    rows = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if rule.endpoint.startswith(SKIP_PREFIXES):
            continue
        func = app.view_functions[rule.endpoint]
        src_file = inspect.getsourcefile(inspect.unwrap(func)) or "?"
        if not os.path.abspath(src_file).startswith(ROOT):
            continue  # z.B. Flask-Admin-Views aus site-packages
        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        tpls = [template_path(app, rule.endpoint, t) for t in templates_of(func)]
        # <token> & Co. escapen, sonst verschluckt der Markdown-Renderer sie als HTML-Tag
        rows.append((html.escape(rule.rule, quote=False), methods, os.path.relpath(src_file, ROOT),
                     rule.endpoint, "<br>".join(tpls) or "–"))

    print("# Map of URLs, routes, and templates\n")
    print("<!-- automatisch erzeugt mit docs/dungeon_keeper.py, nicht von Hand bearbeiten -->\n")
    print("| URL | Methoden | Flask routes.py | Endpunkt | HTML Template |")
    print("| --- | -------- | --------------- | -------- | ------------- |")
    for r in rows:
        print("| " + " | ".join(r) + " |")


if __name__ == "__main__":
    main()
