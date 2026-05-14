# Seguridad — ikigai-clients-db

## Qué NUNCA va en este repositorio

- API keys, tokens de autenticación, bearer tokens
- Passwords o hashes de passwords
- Archivos de service account de Google (`*.json` con `private_key`)
- Tokens de Telegram, Shopify, Cloudflare, Supabase
- Datos personales de clientes finales (GDPR/LFPDPPP)
- Información financiera sensible

## Dónde van las credenciales reales

| Tipo | Destino |
|---|---|
| Supabase URL + anon key | `~/.secrets/supabase_arch_ikigai.env` |
| Google Service Account | `~/.secrets/google_sa_key.json` |
| Shopify Admin Token | `~/.secrets/shopify_admin_ikigai_sheets.env` |
| Cloudflare tokens | `~/.secrets/r2_torreland.env` |
| Telegram tokens | Variables de entorno del servidor / tmux session |

## Escaneo de seguridad

Antes de cada commit, verificar:

```bash
# Buscar patrones de credenciales comunes
grep -r "api_key\|token\|password\|secret\|private_key" . \
  --include="*.yaml" --include="*.json" --include="*.py" \
  --exclude-dir=".git"
```

## Política de acceso

- Este repo puede ser **público en el futuro** — diseñar con ese criterio desde ahora
- Los datos de configuración (dominios, stacks, estados) son información de negocio, no sensible
- Los archivos de deploy pueden incluir versiones pero no credenciales de deploy

## Incidentes

Si se expone una credencial accidentalmente:
1. Revocar la credencial inmediatamente en el proveedor
2. `git filter-branch` o `git-filter-repo` para limpiar el historial
3. Force push a todas las ramas
4. Rotar todas las credenciales del mismo proveedor por precaución
