# Arquitectura — ikigai-clients-db

## Principios de diseño

1. **GitHub = verdad documental/estructural** — versiones, configuración, qué existe
2. **Supabase = verdad operativa/transaccional** — datos dinámicos, gastos, contactos, inventario
3. **Cloudflare D1 = cache de bots** — respuestas rápidas en edge, sincronizado desde Supabase
4. **Drive/Sheets = espejo humano** — visualización y evidencias

## Capas del ecosistema IKIGAI

```
┌─────────────────────────────────────────────────────────┐
│                   AGENTES IA / HUMANOS                  │
└──────────────────┬───────────────────────┬──────────────┘
                   │                       │
          ┌────────▼────────┐   ┌──────────▼─────────┐
          │ ikigai-clients  │   │  ARCH_IKIGAI/       │
          │    -db (este)   │   │  01_CEREBRO/        │
          │  Config/Versión │   │  SOPs/Skills/Memory │
          └────────┬────────┘   └──────────┬──────────┘
                   │                       │
          ┌────────▼───────────────────────▼──────────┐
          │              Supabase                      │
          │        arch-ikigai-master-raw              │
          │     (fuente de verdad operativa)           │
          └───────────────────┬───────────────────────┘
                              │ sync 4h
          ┌───────────────────▼───────────────────────┐
          │         Cloudflare D1 / R2                 │
          │      arch-ikigai-ops (cache bots)          │
          └───────────────────────────────────────────┘
```

## Convenciones de nomenclatura

- **IDs de cliente:** `snake_case`, único, inmutable (ej. `qruzh`, `torreland`)
- **IDs de página:** `snake_case` dentro del cliente (ej. `home`, `colecciones`)
- **Versiones:** `YYYY-MM-DD` o semver `vX.Y.Z`
- **Estados válidos:** `activo` | `en_desarrollo` | `pausado` | `deprecado`

## Estructura de un cliente

```
02_CLIENTES/{cliente_id}/
├── cliente.config.yaml    # Metadata y configuración principal
├── pages/                 # Una página = un archivo .page.yaml
│   └── {page_id}.page.yaml
├── systems/               # Sistemas internos (admin, CRM, etc.)
│   └── {system_id}.system.yaml
├── bots/                  # Bots/agentes (opcional)
│   └── {bot_id}.bot.yaml
└── deploys/               # Registro de deploys por ambiente
    └── {ambiente}.deploy.yaml
```

## Flujo de actualización

1. Modificar archivo YAML/JSON en rama feature
2. CI de GitHub Actions valida el schema
3. PR → merge a `main`
4. `main` = estado real del sistema
5. (futuro) webhook → Supabase actualiza metadata documental

## Reglas de seguridad

- **Nunca** incluir tokens, API keys o passwords en archivos del repo
- Credenciales van en `.env` (ignorado por git) o en `.env.example` como placeholder
- Ver [SECURITY.md](SECURITY.md) para políticas completas
