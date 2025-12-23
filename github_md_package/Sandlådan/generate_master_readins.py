import os
import json
from html import escape

EXCLUDE_DIRS = {
    ".git",
    ".obsidian",
    "node_modules",
    "__pycache__"
}

READIN_PREFIX = "📙(RI)_"
READIN_EXT = ".md"
META_NAME = "META_INDEX"

FILE_TYPES = {
    "MD": [".md"],
    "PY": [".py"],
    "JSON": [".json"],
    "IMG": [".png", ".jpg", ".jpeg", ".svg", ".webp"],
    "HTML": [".html"]
}


def classify_file(name):
    ext = os.path.splitext(name)[1].lower()
    for group, exts in FILE_TYPES.items():
        if ext in exts:
            return group
    return "OTHER"


def is_excluded_dir(name):
    return name in EXCLUDE_DIRS


def compute_level(root, path):
    rel = os.path.relpath(path, root)
    if rel == ".":
        return 0
    return rel.count(os.sep) + 1


def readin_filename(level, folder_name, ext):
    return f"{READIN_PREFIX}(L.{level:02d})_{folder_name}{ext}"


def breadcrumb(root, current):
    parts = []
    while True:
        level = compute_level(root, current)
        name = META_NAME if level == 0 else os.path.basename(current)
        file = readin_filename(level, name, READIN_EXT)
        rel = os.path.relpath(os.path.join(current, file), current)
        parts.append((name, file))
        if level == 0:
            break
        current = os.path.dirname(current)
    return list(reversed(parts))


def generate_md_and_html(root, folder, master_index):
    level = compute_level(root, folder)
    name = META_NAME if level == 0 else os.path.basename(folder)

    md_name = readin_filename(level, name, ".md")
    html_name = readin_filename(level, name, ".html")

    md_path = os.path.join(folder, md_name)
    html_path = os.path.join(folder, html_name)

    bc = breadcrumb(root, folder)

    entries = {}

    for item in sorted(os.listdir(folder)):
        full = os.path.join(folder, item)
        if os.path.isdir(full):
            if not is_excluded_dir(item):
                entries.setdefault("DIR", []).append(item)
        else:
            if not item.startswith(READIN_PREFIX):
                group = classify_file(item)
                entries.setdefault(group, []).append(item)

    master_index.append({
        "level": level,
        "path": os.path.relpath(folder, root),
        "readin_md": md_name,
        "readin_html": html_name,
        "entries": entries
    })

    # ---------- MARKDOWN ----------
    md = []
    md.append("# 📙 Readin – " + name)
    md.append("")
    md.append("**Nivå:** L.{:02d}".format(level))
    md.append("")
    md.append("## 🧭 Breadcrumb")
    md.append("")
    md.append(" › ".join(f"[{n}]({f})" for n, f in bc))
    md.append("")
    md.append("## Innehåll")
    md.append("")

    for group in sorted(entries):
        md.append(f"### {group}")
        for e in entries[group]:
            if group == "DIR":
                md.append(f"- 📁 **{e}**/")
            else:
                md.append(f"- 📄 [{e}]({e})")
        md.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # ---------- HTML ----------
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html><head><meta charset='utf-8'>")
    html.append("<title>Readin – " + escape(name) + "</title>")
    html.append("</head><body>")
    html.append("<h1>📙 Readin – " + escape(name) + "</h1>")
    html.append("<p><b>Nivå:</b> L.{:02d}</p>".format(level))
    html.append("<h3>🧭 Breadcrumb</h3>")
    html.append("<p>" + " › ".join(
        f"<a href='{escape(f)}'>{escape(n)}</a>" for n, f in bc
    ) + "</p>")

    html.append("<h2>Innehåll</h2>")

    for group in sorted(entries):
        html.append("<h3>" + escape(group) + "</h3><ul>")
        for e in entries[group]:
            if group == "DIR":
                html.append("<li>📁 <b>" + escape(e) + "</b></li>")
            else:
                html.append("<li><a href='" + escape(e) + "'>" + escape(e) + "</a></li>")
        html.append("</ul>")

    html.append("</body></html>")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))


def walk(root):
    master_index = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]
        generate_md_and_html(root, current, master_index)

    with open(os.path.join(root, "master-index.json"), "w", encoding="utf-8") as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    walk(os.getcwd())
    print("KLAR: RP9-LOCK Readin-system + HTML + master-index.json genererat.")
