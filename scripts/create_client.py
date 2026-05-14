#!/usr/bin/env python3
"""
create_client.py — Crea la estructura de un nuevo cliente en el repo IKIGAI.
Uso: python scripts/create_client.py --id nuevo_cliente --name "Nombre" [--type otro]

Solo stdlib. No modifica ikigai.registry.json automáticamente — muestra el fragmento
a agregar manualmente para evitar conflictos de merge.
"""
import argparse
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENTS_DIR = os.path.join(ROOT, "02_CLIENTES")
TEMPLATE_DIR = os.path.join(ROOT, "templates", "cliente_template")
REGISTRY = os.path.join(ROOT, "ikigai.registry.json")

VALID_TYPES = ["ecommerce", "servicios", "perfumeria", "inmobiliaria", "restaurante", "otro"]


def validate_id(client_id):
    import re
    if not re.match(r"^[a-z][a-z0-9_]*$", client_id):
        print(f"❌ ID inválido '{client_id}'. Usar solo snake_case (letras minúsculas, números, guión bajo).")
        sys.exit(1)


def check_no_duplicate(client_id):
    if not os.path.isfile(REGISTRY):
        return
    with open(REGISTRY, encoding="utf-8") as f:
        data = json.load(f)
    existing = [c["id"] for c in data.get("clients", [])]
    if client_id in existing:
        print(f"❌ El cliente '{client_id}' ya existe en ikigai.registry.json")
        sys.exit(1)
    client_dir = os.path.join(CLIENTS_DIR, client_id)
    if os.path.exists(client_dir):
        print(f"❌ El directorio {client_dir} ya existe.")
        sys.exit(1)


def create_directories(client_id):
    dirs = [
        os.path.join(CLIENTS_DIR, client_id),
        os.path.join(CLIENTS_DIR, client_id, "pages"),
        os.path.join(CLIENTS_DIR, client_id, "systems"),
        os.path.join(CLIENTS_DIR, client_id, "deploys"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    return dirs


def copy_template(client_id, client_name, client_type):
    today = date.today().isoformat()

    config = f"""id: {client_id}
name: "{client_name}"
type: {client_type}
status: en_desarrollo
priority: media
created_at: "{today}"

contact:
  company: "{client_name}"
  location: "México"

domains:
  - url: "pendiente"
    env: staging
    status: pendiente

repos: []

tech:
  frontend: []
  backend: []
  infra: []
  ai: []
  payments: []

branding:
  colores_primarios: []
  fuentes: []
  assets_path: ""

notes: |
  Cliente creado {today}. Completar datos reales.
"""
    config_path = os.path.join(CLIENTS_DIR, client_id, "cliente.config.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config)

    home_page = f"""id: home
client_id: {client_id}
name: "Home / Inicio"
path: "/"
status: en_desarrollo
type: landing
version: "{today}"
last_updated: "{today}"

features:
  - hero_banner

seo:
  title: "{client_name}"
  description: ""
  keywords: []

analytics:
  ga4: false
  pixel_meta: false
  hotjar: false

notes: ""
"""
    page_path = os.path.join(CLIENTS_DIR, client_id, "pages", "home.page.yaml")
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(home_page)

    deploy = f"""client_id: {client_id}
env: staging
status: pending
version: "0.1"
deployed_at: "{today}"

infra:
  host: ""
  provider: "por_definir"
  container: ""
  ssl_expiry: ""
  cdn: ""

healthcheck:
  url: ""
  ok: false

notes: ""
"""
    deploy_path = os.path.join(CLIENTS_DIR, client_id, "deploys", "staging.deploy.yaml")
    with open(deploy_path, "w", encoding="utf-8") as f:
        f.write(deploy)

    return config_path, page_path, deploy_path


def print_registry_fragment(client_id, client_name, client_type):
    today = date.today().isoformat()
    fragment = {
        "id": client_id,
        "name": client_name,
        "type": client_type,
        "status": "en_desarrollo",
        "priority": "media",
        "created_at": today,
        "config_path": f"02_CLIENTES/{client_id}/cliente.config.yaml",
        "contact": {"company": client_name, "location": "México"},
        "domains": [{"url": "pendiente", "env": "staging", "status": "pendiente"}],
        "repos": [],
        "tech": {"frontend": [], "backend": [], "infra": [], "ai": [], "payments": []},
        "pages_count": 1,
        "systems_count": 0,
        "bots_count": 0,
    }
    print("\n📋 Agregar este fragmento al array 'clients' en ikigai.registry.json:")
    print(json.dumps(fragment, ensure_ascii=False, indent=4))


def main():
    parser = argparse.ArgumentParser(description="Crear nuevo cliente IKIGAI")
    parser.add_argument("--id", required=True, help="ID único snake_case del cliente")
    parser.add_argument("--name", required=True, help="Nombre comercial del cliente")
    parser.add_argument("--type", default="otro", choices=VALID_TYPES, help="Tipo de negocio")
    args = parser.parse_args()

    client_id = args.id.strip().lower()
    client_name = args.name.strip()
    client_type = args.type

    print(f"\n🚀 Creando cliente: {client_id} ({client_name})\n")

    validate_id(client_id)
    check_no_duplicate(client_id)
    dirs = create_directories(client_id)
    config_path, page_path, deploy_path = copy_template(client_id, client_name, client_type)

    print("✅ Directorios creados:")
    for d in dirs:
        print(f"   {os.path.relpath(d, ROOT)}/")

    print("\n✅ Archivos creados:")
    for p in [config_path, page_path, deploy_path]:
        print(f"   {os.path.relpath(p, ROOT)}")

    print_registry_fragment(client_id, client_name, client_type)

    print("\n📌 Próximos pasos:")
    print(f"  1. Editar 02_CLIENTES/{client_id}/cliente.config.yaml con datos reales")
    print(f"  2. Agregar el fragmento de arriba a ikigai.registry.json → 'clients'")
    print(f"  3. Regenerar índices: python scripts/generate_client_index.py && python scripts/generate_pages_index.py")
    print(f"  4. Validar: python scripts/validate_registry.py")


if __name__ == "__main__":
    main()
