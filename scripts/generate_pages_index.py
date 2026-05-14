#!/usr/bin/env python3
"""
generate_pages_index.py — Genera PAGES_INDEX.md escaneando todos los .page.yaml.
Solo stdlib — usa el módulo re para parseo básico de YAML.
"""
import os
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENTS_DIR = os.path.join(ROOT, "02_CLIENTES")
OUTPUT = os.path.join(ROOT, "PAGES_INDEX.md")

STATUS_EMOJI = {
    "activo": "✅",
    "en_desarrollo": "🔧",
    "pausado": "⏸️",
    "deprecado": "🗑️",
}


def parse_yaml_simple(content):
    """
    Parseo mínimo de YAML plano (sin anidado, sin listas complejas).
    Suficiente para los campos de primer nivel de .page.yaml.
    """
    result = {}
    for line in content.splitlines():
        m = re.match(r'^(\w+):\s*"?([^"#\n]*)"?\s*$', line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip().strip('"')
            result[key] = val
    return result


def scan_pages():
    pages = []
    if not os.path.isdir(CLIENTS_DIR):
        return pages
    for client_id in sorted(os.listdir(CLIENTS_DIR)):
        pages_dir = os.path.join(CLIENTS_DIR, client_id, "pages")
        if not os.path.isdir(pages_dir):
            continue
        for fname in sorted(os.listdir(pages_dir)):
            if not fname.endswith(".page.yaml"):
                continue
            fpath = os.path.join(pages_dir, fname)
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
            data = parse_yaml_simple(content)
            data["client_id"] = data.get("client_id", client_id)
            data["_file"] = os.path.relpath(fpath, ROOT)
            pages.append(data)
    return pages


def main():
    pages = scan_pages()
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    clients_seen = {}
    for p in pages:
        cid = p.get("client_id", "—")
        clients_seen.setdefault(cid, []).append(p)

    lines = [
        "# PAGES_INDEX — Páginas del ecosistema IKIGAI",
        "",
        f"> Generado automáticamente: {generated_at}  ",
        f"> Total páginas: **{len(pages)}** en **{len(clients_seen)}** clientes",
        "",
        "## Tabla global de páginas",
        "",
        "| Cliente | ID página | Nombre | Path | Estado | Tipo | Versión |",
        "|---|---|---|---|---|---|---|",
    ]

    for p in pages:
        cid = p.get("client_id", "—")
        pid = p.get("id", "—")
        name = p.get("name", "—")
        path = p.get("path", "—")
        status = p.get("status", "—")
        ptype = p.get("type", "—")
        version = p.get("version", "—")
        s_emoji = STATUS_EMOJI.get(status, "")
        lines.append(f"| `{cid}` | `{pid}` | {name} | `{path}` | {s_emoji} {status} | {ptype} | {version} |")

    lines += ["", "## Por cliente", ""]

    for cid, client_pages in clients_seen.items():
        lines += [
            f"### `{cid}` ({len(client_pages)} páginas)",
            "",
        ]
        for p in client_pages:
            pid = p.get("id", "—")
            name = p.get("name", "—")
            path = p.get("path", "—")
            status = p.get("status", "—")
            s_emoji = STATUS_EMOJI.get(status, "")
            fpath = p.get("_file", "")
            lines.append(f"- {s_emoji} **`{pid}`** — {name} (`{path}`) → [`{fpath}`]({fpath})")
        lines.append("")

    lines += [
        "---",
        "",
        "_Regenerar con: `python scripts/generate_pages_index.py`_",
    ]

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✅ PAGES_INDEX.md generado — {len(pages)} páginas en {len(clients_seen)} clientes")
    print(f"   → {OUTPUT}")


if __name__ == "__main__":
    main()
