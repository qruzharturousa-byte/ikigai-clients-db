# ikigai-clients-db

Base de datos documental versionada para la arquitectura IKIGAI de Arturo Monroy.

## ¿Qué es esto?

Repositorio GitHub como **fuente de verdad documental** para todos los clientes del ecosistema IKIGAI:
qué clientes existen, qué páginas tienen, qué versión está en producción y qué falta.

**No es una base de datos transaccional** — eso lo maneja Supabase/D1. Esto es el registro
canónico de configuración, estructura y estado de cada cliente y sus activos digitales.

## Clientes activos

| ID | Nombre | Estado | Dominio principal |
|---|---|---|---|
| `qruzh` | QRUZH | ✅ Activo | qruzh.com.mx |
| `torreland` | Torre Land SA de CV | ✅ Activo | torreland.com.mx |
| `gardenia_perfumeria` | Gardenia Bloom | 🔧 En desarrollo | pendiente |

## Estructura

```
ikigai-clients-db/
├── ikigai.registry.json          # Índice global de clientes
├── schemas/                      # Schemas JSON de validación
├── templates/cliente_template/   # Plantilla base reutilizable
├── 02_CLIENTES/                  # Un directorio por cliente
│   ├── qruzh/
│   ├── torreland/
│   └── gardenia_perfumeria/
├── scripts/                      # Scripts de validación e índices
└── .github/workflows/            # CI de validación automática
```

## Uso rápido

```bash
# Validar integridad del registro
python scripts/validate_registry.py

# Generar índice de clientes
python scripts/generate_client_index.py

# Generar índice de páginas
python scripts/generate_pages_index.py

# Crear nuevo cliente
python scripts/create_client.py --id nuevo_cliente --name "Nombre Cliente"
```

## Arquitectura relacionada

- **Datos OPS dinámicos:** Supabase `arch-ikigai-master-raw`
- **Cache bots:** Cloudflare D1 `arch-ikigai-ops`
- **Cerebro IKIGAI:** `/Users/arturo/ARCH_IKIGAI/01_CEREBRO/`
- **Documentación arquitectura:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Seguridad:** [SECURITY.md](SECURITY.md)
- **Guía para agentes IA:** [AGENTS.md](AGENTS.md)
