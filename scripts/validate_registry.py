#!/usr/bin/env python3
"""
validate_registry.py — Valida integridad del registro IKIGAI de clientes.
Verifica: JSON válido, IDs únicos, config_path existente, counts de páginas.
Solo stdlib.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "ikigai.registry.json")
CLIENTS_DIR = os.path.join(ROOT, "02_CLIENTES")


def load_registry():
    with open(REGISTRY, encoding="utf-8") as f:
        return json.load(f)


def check_unique_ids(clients):
    ids = [c["id"] for c in clients]
    seen = set()
    duplicates = []
    for cid in ids:
        if cid in seen:
            duplicates.append(cid)
        seen.add(cid)
    return duplicates


def check_client_dirs(clients):
    missing = []
    for c in clients:
        client_dir = os.path.join(CLIENTS_DIR, c["id"])
        if not os.path.isdir(client_dir):
            missing.append(c["id"])
    return missing


def check_config_paths(clients):
    missing = []
    for c in clients:
        config_path = os.path.join(ROOT, c.get("config_path", ""))
        if not os.path.isfile(config_path):
            missing.append((c["id"], c.get("config_path", "")))
    return missing


def check_pages_counts(clients):
    mismatches = []
    for c in clients:
        pages_dir = os.path.join(CLIENTS_DIR, c["id"], "pages")
        declared = c.get("pages_count", 0)
        if os.path.isdir(pages_dir):
            actual = len([f for f in os.listdir(pages_dir) if f.endswith(".page.yaml")])
        else:
            actual = 0
        if declared != actual:
            mismatches.append((c["id"], declared, actual))
    return mismatches


def check_no_credentials(clients):
    """Alerta si algún campo contiene patrones de credenciales."""
    import re
    pattern = re.compile(r"(api_key|token|password|secret|private_key)", re.IGNORECASE)
    raw = json.dumps(clients)
    matches = pattern.findall(raw)
    return list(set(matches))


def main():
    errors = []
    warnings = []

    print("🔍 Validando ikigai.registry.json...\n")

    if not os.path.isfile(REGISTRY):
        print(f"❌ FATAL: no se encontró {REGISTRY}")
        sys.exit(1)

    try:
        data = load_registry()
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        sys.exit(1)

    clients = data.get("clients", [])
    print(f"  Clientes en registro: {len(clients)}")

    duplicates = check_unique_ids(clients)
    if duplicates:
        errors.append(f"IDs duplicados: {duplicates}")

    missing_dirs = check_client_dirs(clients)
    if missing_dirs:
        errors.append(f"Directorios faltantes en 02_CLIENTES/: {missing_dirs}")

    missing_configs = check_config_paths(clients)
    if missing_configs:
        for cid, path in missing_configs:
            errors.append(f"config_path no existe para '{cid}': {path}")

    count_mismatches = check_pages_counts(clients)
    if count_mismatches:
        for cid, declared, actual in count_mismatches:
            warnings.append(f"pages_count incorrecto para '{cid}': declarado={declared}, real={actual}")

    cred_hits = check_no_credentials(clients)
    if cred_hits:
        warnings.append(f"Posibles credenciales en registry (revisar): {cred_hits}")

    if errors:
        print("\n❌ ERRORES:")
        for e in errors:
            print(f"  • {e}")
    if warnings:
        print("\n⚠️  ADVERTENCIAS:")
        for w in warnings:
            print(f"  • {w}")

    if not errors and not warnings:
        print("\n✅ Registro válido — todo OK")
    elif not errors:
        print(f"\n✅ Registro válido ({len(warnings)} advertencia(s))")
    else:
        print(f"\n❌ Validación fallida ({len(errors)} error(es))")
        sys.exit(1)


if __name__ == "__main__":
    main()
