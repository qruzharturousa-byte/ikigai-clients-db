#!/usr/bin/env python3
"""
generate_client_index.py — Genera CLIENTES_INDEX.md desde ikigai.registry.json.
Tabla Markdown con los 3+ clientes del ecosistema IKIGAI.
Solo stdlib.
"""
import json
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "ikigai.registry.json")
OUTPUT = os.path.join(ROOT, "CLIENTES_INDEX.md")

STATUS_EMOJI = {
    "activo": "✅",
    "en_desarrollo": "🔧",
    "pausado": "⏸️",
    "deprecado": "🗑️",
}

PRIORITY_EMOJI = {
    "alta": "🔴",
    "media": "🟡",
    "baja": "🟢",
}


def load_registry():
    with open(REGISTRY, encoding="utf-8") as f:
        return json.load(f)


def format_domains(domains):
    if not domains:
        return "—"
    active = [d["url"] for d in domains if d.get("status") == "activo"]
    if not active:
        return domains[0]["url"] if domains else "—"
    return active[0]


def format_stack(tech):
    parts = []
    if tech.get("frontend"):
        parts.append(tech["frontend"][0])
    if tech.get("backend"):
        parts.append(tech["backend"][0])
    if tech.get("infra"):
        parts.append(tech["infra"][0])
    return " · ".join(parts) if parts else "—"


def main():
    data = load_registry()
    clients = data.get("clients", [])
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# CLIENTES_INDEX — Ecosistema IKIGAI",
        "",
        f"> Generado automáticamente: {generated_at}  ",
        f"> Fuente: `ikigai.registry.json` · Total clientes: **{len(clients)}**",
        "",
        "## Tabla de clientes",
        "",
        "| ID | Nombre | Estado | Prioridad | Dominio principal | Páginas | Sistemas | Stack |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for c in clients:
        cid = c["id"]
        name = c["name"]
        status = c.get("status", "—")
        priority = c.get("priority", "—")
        domain = format_domains(c.get("domains", []))
        pages = c.get("pages_count", 0)
        systems = c.get("systems_count", 0)
        stack = format_stack(c.get("tech", {}))
        s_emoji = STATUS_EMOJI.get(status, "")
        p_emoji = PRIORITY_EMOJI.get(priority, "")
        lines.append(f"| `{cid}` | {name} | {s_emoji} {status} | {p_emoji} {priority} | {domain} | {pages} | {systems} | {stack} |")

    lines += [
        "",
        "## Detalle por cliente",
        "",
    ]

    for c in clients:
        cid = c["id"]
        name = c["name"]
        status = c.get("status", "—")
        s_emoji = STATUS_EMOJI.get(status, "")
        domains = c.get("domains", [])
        repos = c.get("repos", [])
        tech = c.get("tech", {})
        notes = c.get("notes", "")

        lines += [
            f"### {s_emoji} `{cid}` — {name}",
            "",
            f"- **Tipo:** {c.get('type', '—')}",
            f"- **Estado:** {status} | **Prioridad:** {c.get('priority', '—')}",
            f"- **Config:** `02_CLIENTES/{cid}/cliente.config.yaml`",
            f"- **Páginas:** {c.get('pages_count', 0)} | **Sistemas:** {c.get('systems_count', 0)} | **Bots:** {c.get('bots_count', 0)}",
        ]

        if domains:
            domain_list = " · ".join([f"`{d['url']}`" for d in domains])
            lines.append(f"- **Dominios:** {domain_list}")

        if repos:
            repo_list = " · ".join([f"`{r}`" for r in repos])
            lines.append(f"- **Repos:** {repo_list}")

        all_tech = []
        for k in ["frontend", "backend", "infra", "ai", "payments"]:
            all_tech.extend(tech.get(k, []))
        if all_tech:
            lines.append(f"- **Stack:** {' · '.join(all_tech)}")

        if notes:
            first_line = notes.strip().split("\n")[0]
            lines.append(f"- **Notas:** {first_line}")

        lines.append("")

    lines += [
        "---",
        "",
        "_Regenerar con: `python scripts/generate_client_index.py`_",
    ]

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✅ CLIENTES_INDEX.md generado — {len(clients)} clientes")
    print(f"   → {OUTPUT}")


if __name__ == "__main__":
    main()
