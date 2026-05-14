# Guía para Agentes IA — ikigai-clients-db

Este archivo describe cómo un agente IA debe interactuar con este repositorio.

## Pregunta más común: ¿qué clientes existen?

```bash
# Leer el registro global
cat ikigai.registry.json | python3 -c "import json,sys; [print(c['id'], '-', c['name'], '|', c['status']) for c in json.load(sys.stdin)['clients']]"
```

O leer directamente: `CLIENTES_INDEX.md` (tabla Markdown pre-generada)

## Pregunta: ¿qué páginas tiene el cliente X?

```bash
# Ver directorio de páginas del cliente
ls 02_CLIENTES/{cliente_id}/pages/

# Ver detalles de una página
cat 02_CLIENTES/{cliente_id}/pages/{page_id}.page.yaml
```

O leer: `PAGES_INDEX.md` (tabla global pre-generada)

## Pregunta: ¿qué versión está en producción?

```bash
cat 02_CLIENTES/{cliente_id}/deploys/production.deploy.yaml
```

## Pregunta: ¿qué falta por hacer en un cliente?

```bash
cat 02_CLIENTES/{cliente_id}/cliente.config.yaml | grep -A 20 "pendiente\|todo\|backlog"
```

## Cómo agregar un cliente nuevo

```bash
python scripts/create_client.py --id nuevo_cliente --name "Nombre" --type ecommerce
```

El script crea la estructura base. Luego editar `cliente.config.yaml` con los datos reales.

## Validar antes de hacer cambios

```bash
python scripts/validate_registry.py
```

## Reglas para agentes

1. **Nunca modificar** `ikigai.registry.json` manualmente — usar los scripts
2. **Regenerar índices** después de cualquier cambio: `python scripts/generate_client_index.py && python scripts/generate_pages_index.py`
3. **No agregar credenciales** — ver SECURITY.md
4. **Snake_case** para todos los IDs
5. **Estados válidos:** `activo`, `en_desarrollo`, `pausado`, `deprecado`
6. Los archivos `.page.yaml`, `.system.yaml`, `.bot.yaml`, `.deploy.yaml` siguen los schemas en `schemas/`

## Fuentes de verdad relacionadas

| Pregunta | Fuente |
|---|---|
| Datos de configuración/versiones | Este repo (ikigai-clients-db) |
| Gastos, transacciones | Supabase `arch-ikigai-master-raw` |
| Cache para bots | Cloudflare D1 `arch-ikigai-ops` |
| SOPs y skills | `/Users/arturo/ARCH_IKIGAI/01_CEREBRO/` |
| Evidencias y documentos | Google Drive |
