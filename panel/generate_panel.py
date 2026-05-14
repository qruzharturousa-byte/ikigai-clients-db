#!/usr/bin/env python3
"""
generate_panel.py — Genera el Panel Maestro IKIGAI desde los archivos YAML
Lee 02_CLIENTES/ y produce panel/index.html listo para Cloudflare Pages
"""
import json, os, sys, re
from datetime import datetime
from pathlib import Path

ROOT     = Path(__file__).parent.parent
CLIENTS  = ROOT / "02_CLIENTES"
OUT      = Path(__file__).parent / "index.html"
REGISTRY = ROOT / "ikigai.registry.json"

# ── Leer YAML sin dependencias externas ─────────────────────────────────────
def parse_yaml_simple(text):
    result = {}
    indent_stack = [result]
    current_indent = 0

    for line in text.splitlines():
        if not line.strip() or line.strip().startswith('#'):
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith('- '):
            val = stripped[2:].strip().strip('"').strip("'")
            target = indent_stack[-1]
            last_key = list(target.keys())[-1] if target else None
            if last_key and isinstance(target.get(last_key), list):
                target[last_key].append(val)
            continue

        if ':' in stripped:
            key, _, val = stripped.partition(':')
            key = key.strip()
            val = val.strip().strip('"').strip("'")

            while len(indent_stack) > indent // 2 + 1:
                indent_stack.pop()

            target = indent_stack[-1]

            if val == '' or val == '|':
                new_dict = {}
                target[key] = new_dict
                indent_stack.append(new_dict)
                current_indent = indent
            elif val == '[]':
                target[key] = []
                current_indent = indent
            else:
                target[key] = val
                current_indent = indent

    return result

def read_yaml(path):
    try:
        return parse_yaml_simple(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return {}

# ── Leer datos de clientes ───────────────────────────────────────────────────
def load_clients():
    clients = []
    if not CLIENTS.exists():
        return clients

    with open(REGISTRY, encoding='utf-8') as f:
        registry = json.load(f)

    order = [c['id'] for c in registry.get('clients', [])]

    for client_id in order:
        client_dir = CLIENTS / client_id
        if not client_dir.is_dir():
            continue

        config = read_yaml(client_dir / 'cliente.config.yaml')
        config['id'] = config.get('id', client_id)

        pages_dir = client_dir / 'pages'
        pages = []
        if pages_dir.exists():
            for f in sorted(pages_dir.glob('*.page.yaml')):
                p = read_yaml(f)
                p['id'] = p.get('id', f.stem.replace('.page', ''))
                pages.append(p)
        config['pages_list'] = pages
        config['pages_count'] = len(pages)

        sys_dir = client_dir / 'systems'
        systems = []
        if sys_dir.exists():
            for f in sorted(sys_dir.glob('*.system.yaml')):
                s = read_yaml(f)
                s['id'] = s.get('id', f.stem.replace('.system', ''))
                systems.append(s)
        config['systems_list'] = systems

        bots_dir = client_dir / 'bots'
        bots = []
        if bots_dir.exists():
            for f in sorted(bots_dir.glob('*.bot.yaml')):
                b = read_yaml(f)
                b['id'] = b.get('id', f.stem.replace('.bot', ''))
                bots.append(b)
        config['bots_list'] = bots

        clients.append(config)

    return clients

# ── Helpers ───────────────────────────────────────────────────────────────────
STATUS_META = {
    'activo':        ('var(--green)', 'var(--green-bg)', '● Activo'),
    'en_desarrollo': ('var(--amber)', 'var(--amber-bg)', '◐ En desarrollo'),
    'pausado':       ('var(--red)',   'var(--red-bg)',   '○ Pausado'),
    'archivado':     ('var(--muted)', 'var(--muted-bg)', '◌ Archivado'),
}

def status_pill(status):
    color, bg, label = STATUS_META.get(status, ('var(--muted)', 'var(--muted-bg)', status))
    return f'<span class="pill" style="color:{color};background:{bg}">{label}</span>'

def priority_dot(priority):
    colors = {'alta': 'var(--red)', 'media': 'var(--amber)', 'baja': 'var(--muted)'}
    labels = {'alta': 'Prioridad alta', 'media': 'Prioridad media', 'baja': 'Prioridad baja'}
    c = colors.get(priority, 'var(--muted)')
    l = labels.get(priority, priority)
    return f'<span class="priority-dot" style="background:{c}" title="{l}"></span>'

def domain_links(client):
    domains = []
    raw = client.get('domains', '')
    # Lista de dicts (formato nuevo): [{url: ..., env: ...}]
    if isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict):
                u = entry.get('url', '')
                if u and '.' in u and u != 'pendiente':
                    domains.append(u.strip())
            elif isinstance(entry, str) and '.' in entry and entry != 'pendiente':
                domains.append(entry.strip())
    elif isinstance(raw, dict):
        for k, v in raw.items():
            if isinstance(v, str) and '.' in v and v != 'pendiente':
                domains.append(v.strip())
    if not domains:
        notes = str(client.get('notes', ''))
        found = re.findall(r'[\w-]+\.[\w.-]+\.mx|[\w-]+\.[\w.-]+\.com', notes)
        domains = list(dict.fromkeys(found))[:3]
    if not domains:
        domains = [f"{client['id']}.com.mx"]

    links = []
    for d in domains[:4]:
        url = d if d.startswith('http') else f"https://{d}"
        links.append(f'<a href="{url}" target="_blank" class="domain-pill">{d} ↗</a>')
    return ' '.join(links)

def pages_grid(pages):
    if not pages:
        return '<p class="empty-state">Sin páginas registradas</p>'
    items = ''
    for p in pages:
        status = p.get('status', 'en_desarrollo')
        color, _, _ = STATUS_META.get(status, ('var(--muted)', '', ''))
        name = p.get('name', p.get('id', ''))
        path = p.get('path', '/')
        ver  = p.get('version_actual', p.get('version', ''))
        items += f'''<div class="page-item">
          <div class="page-dot" style="background:{color}"></div>
          <div class="page-info">
            <span class="page-name">{name}</span>
            <span class="page-path">{path}</span>
          </div>
          {'<span class="version-tag">' + ver + '</span>' if ver else ''}
        </div>'''
    return f'<div class="pages-grid">{items}</div>'

def systems_row(systems):
    if not systems:
        return '<span class="tag tag-muted">Sin sistemas</span>'
    tags = ''
    for s in systems:
        status = s.get('status', 'en_desarrollo')
        color, bg, _ = STATUS_META.get(status, ('var(--muted)', 'var(--muted-bg)', ''))
        name = s.get('name', s.get('id', ''))
        tags += f'<span class="tag" style="color:{color};background:{bg}">{name}</span>'
    return tags

def bots_row(bots):
    if not bots:
        return '<span class="tag tag-muted">Sin bot</span>'
    tags = ''
    for b in bots:
        status = b.get('status', 'en_desarrollo')
        name = b.get('name', b.get('id', ''))
        version = b.get('version', '')
        if status == 'activo':
            tags += f'<span class="tag tag-bot">{name}{(" · " + version) if version else ""}</span>'
        else:
            tags += f'<span class="tag tag-muted">{name} (dev)</span>'
    return tags

# ── HTML premium ──────────────────────────────────────────────────────────────
def generate_html(clients):
    now = datetime.now().strftime('%d %b %Y, %H:%M')
    total_pages = sum(c.get('pages_count', 0) for c in clients)
    active = sum(1 for c in clients if c.get('status') == 'activo')
    bots_active = sum(
        len([b for b in c.get('bots_list', []) if b.get('status') == 'activo'])
        for c in clients
    )

    # — Client cards
    cards = ''
    client_colors = [
        'linear-gradient(135deg, #5BBFC4, #3D9EA3)',   # QRUZH — teal
        'linear-gradient(135deg, #C47890, #9B5F73)',   # Torreland — rose
        'linear-gradient(135deg, #C4A882, #A08060)',   # Gardenia — gold
    ]
    for i, c in enumerate(clients):
        cid      = c.get('id', '')
        name     = c.get('name', cid)
        status   = c.get('status', 'en_desarrollo')
        priority = c.get('priority', 'media')
        tipo     = c.get('type', '')
        initials = ''.join(w[0].upper() for w in name.split()[:2])
        grad     = client_colors[i % len(client_colors)]
        active_bots = [b for b in c.get('bots_list', []) if b.get('status') == 'activo']
        bot_live = bool(active_bots)

        cards += f'''
        <div class="card" style="--card-delay:{i * 0.08}s">
          <div class="card-top">
            <div class="avatar" style="background:{grad}">{initials}</div>
            <div class="card-identity">
              <div class="card-name-row">
                <h2 class="card-name">{name}</h2>
                {priority_dot(priority)}
              </div>
              <div class="card-sub">{tipo}</div>
              {status_pill(status)}
            </div>
            {'<div class="bot-live-badge">🤖 Bot LIVE</div>' if bot_live else ''}
          </div>

          <div class="domains-row">{domain_links(c)}</div>

          <div class="metrics-row">
            <div class="metric">
              <span class="metric-val">{c.get("pages_count", 0)}</span>
              <span class="metric-lbl">Páginas</span>
            </div>
            <div class="metric">
              <span class="metric-val">{len(c.get("systems_list", []))}</span>
              <span class="metric-lbl">Sistemas</span>
            </div>
            <div class="metric">
              <span class="metric-val">{len(c.get("bots_list", []))}</span>
              <span class="metric-lbl">Bots</span>
            </div>
          </div>

          <div class="section-block">
            <div class="section-label">Sistemas</div>
            <div class="tags-row">{systems_row(c.get("systems_list", []))}</div>
          </div>

          <div class="section-block">
            <div class="section-label">Bots IA</div>
            <div class="tags-row">{bots_row(c.get("bots_list", []))}</div>
          </div>

          <div class="section-block">
            <div class="section-label">Páginas</div>
            {pages_grid(c.get("pages_list", []))}
          </div>
        </div>'''

    # — Stats numbers
    stats_html = f'''
      <div class="stat-item">
        <span class="stat-num">{len(clients)}</span>
        <span class="stat-lbl">Clientes</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-num">{active}</span>
        <span class="stat-lbl">Activos</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-num">{total_pages}</span>
        <span class="stat-lbl">Páginas</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-num">{bots_active}</span>
        <span class="stat-lbl">Bots LIVE</span>
      </div>'''

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IKIGAI — Panel Maestro</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {{
      /* ── Paleta IKIGAI oficial (extraída del logo) ── */
      --teal:       #5BBFC4;
      --teal-dark:  #3D9EA3;
      --teal-light: #A8DDE0;
      --teal-bg:    #EBF7F8;
      --rose:       #C47890;
      --rose-dark:  #9B5F73;
      --rose-light: #E8A8BB;
      --rose-bg:    #FAEEF2;
      --blush:      #F4B8C8;
      --gold:       #C4A882;
      --gold-light: #E8D8C0;
      /* ── Base ── */
      --bg:         #F7F3EF;
      --surface:    #FDFAF8;
      --surface2:   #F4EFE9;
      --border:     rgba(180,140,120,0.15);
      --shadow-sm:  0 1px 3px rgba(100,60,50,0.07), 0 1px 2px rgba(100,60,50,0.04);
      --shadow-md:  0 4px 16px rgba(100,60,50,0.10), 0 2px 4px rgba(100,60,50,0.05);
      --shadow-lg:  0 16px 48px rgba(100,60,50,0.14), 0 4px 12px rgba(100,60,50,0.07);
      --text:       #2C2018;
      --text-2:     #4A3828;
      --text-3:     #8A7060;
      --accent:     var(--teal);
      --accent2:    var(--rose);
      --green:      #1aa260;
      --green-bg:   #e8f8f0;
      --amber:      #d97706;
      --amber-bg:   #fef3c7;
      --red:        #dc2626;
      --red-bg:     #fee2e2;
      --muted:      #8A7060;
      --muted-bg:   #EDE8E2;
      --radius:     18px;
      --radius-sm:  10px;
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }}

    /* ── NAV ─────────────────────────────── */
    nav {{
      position: sticky; top: 0; z-index: 100;
      background: rgba(255,255,255,0.82);
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      border-bottom: 1px solid var(--border);
    }}
    .nav-inner {{
      max-width: 1280px; margin: 0 auto;
      padding: 0 32px;
      height: 56px;
      display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{
      display: flex; align-items: center; gap: 10px;
    }}
    .nav-logo-img {{
      height: 40px; width: 40px; border-radius: 10px;
      object-fit: cover;
    }}
    .nav-logo-text {{
      font-size: 17px; font-weight: 800; letter-spacing: 0.04em;
      background: linear-gradient(90deg, #5BBFC4 0%, #C47890 60%, #C4A882 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .nav-sep {{ width: 1px; height: 18px; background: var(--border); }}
    .nav-sub {{ font-size: 13px; color: var(--text-3); font-weight: 400; }}
    .nav-meta {{ font-size: 12px; color: var(--text-3); }}
    .nav-meta a {{ color: var(--accent); text-decoration: none; font-weight: 500; }}
    .nav-meta a:hover {{ text-decoration: underline; }}

    /* ── HERO ────────────────────────────── */
    .hero {{
      position: relative; overflow: hidden;
      background: linear-gradient(145deg, #1C1412 0%, #2A1F1A 35%, #1E2D2E 70%, #12211E 100%);
      padding: 80px 32px 72px;
      text-align: center;
    }}
    .hero::before {{
      content: '';
      position: absolute; inset: 0;
      background: radial-gradient(ellipse 70% 55% at 50% 0%, rgba(91,191,196,0.28) 0%, transparent 65%),
                  radial-gradient(ellipse 50% 40% at 85% 100%, rgba(196,120,144,0.22) 0%, transparent 60%),
                  radial-gradient(ellipse 40% 40% at 15% 75%, rgba(196,168,130,0.15) 0%, transparent 60%);
      pointer-events: none;
    }}
    .hero-orb {{
      position: absolute;
      border-radius: 50%;
      filter: blur(70px);
      opacity: 0.5;
      animation: float 9s ease-in-out infinite;
    }}
    .orb-1 {{ width: 320px; height: 320px; background: #5BBFC4; top: -100px; left: -80px; }}
    .orb-2 {{ width: 220px; height: 220px; background: #C47890; bottom: -50px; right: 4%; animation-delay: -3.5s; }}
    .orb-3 {{ width: 160px; height: 160px; background: #C4A882; top: 25%; right: 18%; animation-delay: -6s; opacity: 0.3; }}
    @keyframes float {{
      0%, 100% {{ transform: translateY(0px); }}
      50% {{ transform: translateY(-18px); }}
    }}
    .hero-content {{ position: relative; z-index: 1; }}
    .hero-logo-wrap {{
      margin-bottom: 28px;
    }}
    .hero-logo {{
      width: 130px; height: 130px;
      border-radius: 32px;
      object-fit: cover;
      box-shadow: 0 0 0 1px rgba(91,191,196,0.3),
                  0 8px 40px rgba(0,0,0,0.5),
                  0 0 80px rgba(91,191,196,0.15);
      animation: fadeIn 0.8s ease both;
    }}
    @keyframes fadeIn {{
      from {{ opacity:0; transform:scale(0.92); }}
      to   {{ opacity:1; transform:scale(1); }}
    }}
    .hero-eyebrow {{
      display: inline-block;
      font-size: 11px; font-weight: 600; letter-spacing: 0.14em;
      text-transform: uppercase;
      color: rgba(255,255,255,0.55);
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(91,191,196,0.25);
      padding: 5px 14px; border-radius: 999px;
      margin-bottom: 20px;
    }}
    .hero-title {{
      font-size: clamp(36px, 6vw, 64px);
      font-weight: 800; letter-spacing: -0.04em;
      background: linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.75) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
      line-height: 1.05;
      margin-bottom: 12px;
    }}
    .hero-gradient-word {{
      background: linear-gradient(90deg, #7DE0E4, #E8A8BB, #E8D0A8);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .hero-sub {{
      font-size: 17px; color: rgba(255,255,255,0.45);
      font-weight: 400; line-height: 1.5;
      margin-bottom: 40px;
      letter-spacing: 0.01em;
    }}

    /* ── STATS BAR ───────────────────────── */
    .stats-bar {{
      display: flex; align-items: center; justify-content: center;
      gap: 0; flex-wrap: wrap;
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(91,191,196,0.2);
      border-radius: 20px; padding: 0 8px;
      max-width: 520px; margin: 0 auto;
      backdrop-filter: blur(20px);
    }}
    .stat-item {{
      display: flex; flex-direction: column; align-items: center;
      padding: 18px 28px;
    }}
    .stat-num {{
      font-size: 32px; font-weight: 800; letter-spacing: -0.04em;
      background: linear-gradient(135deg, #ffffff, rgba(255,255,255,0.8));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
      line-height: 1;
    }}
    .stat-lbl {{
      font-size: 11px; font-weight: 500; letter-spacing: 0.06em;
      text-transform: uppercase; color: rgba(255,255,255,0.45);
      margin-top: 4px;
    }}
    .stat-divider {{
      width: 1px; height: 36px;
      background: rgba(255,255,255,0.1);
    }}

    /* ── MAIN GRID ───────────────────────── */
    .main {{
      max-width: 1280px; margin: 0 auto;
      padding: 56px 32px 80px;
    }}
    .section-title {{
      font-size: 13px; font-weight: 600; letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--text-3);
      margin-bottom: 24px;
    }}
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(min(100%, 580px), 1fr));
      gap: 24px;
    }}

    /* ── CLIENT CARD ─────────────────────── */
    .card {{
      background: var(--surface);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
      padding: 28px;
      display: flex; flex-direction: column; gap: 20px;
      transition: transform 0.25s cubic-bezier(.25,.46,.45,.94),
                  box-shadow 0.25s cubic-bezier(.25,.46,.45,.94);
      animation: slideUp 0.5s cubic-bezier(.25,.46,.45,.94) both;
      animation-delay: var(--card-delay, 0s);
    }}
    @keyframes slideUp {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .card:hover {{
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
    }}

    /* — Card top */
    .card-top {{
      display: flex; align-items: flex-start; gap: 16px;
      position: relative;
    }}
    .avatar {{
      width: 52px; height: 52px; border-radius: 14px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-size: 18px; font-weight: 800; color: white;
      letter-spacing: -0.02em;
    }}
    .card-identity {{ flex: 1; min-width: 0; }}
    .card-name-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }}
    .card-name {{
      font-size: 19px; font-weight: 700; letter-spacing: -0.02em;
      color: var(--text); line-height: 1.2;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .card-sub {{ font-size: 13px; color: var(--text-3); margin-bottom: 8px; }}
    .bot-live-badge {{
      position: absolute; top: 0; right: 0;
      font-size: 11px; font-weight: 600;
      background: linear-gradient(135deg, var(--teal), var(--teal-dark));
      color: white; padding: 4px 10px; border-radius: 999px;
      letter-spacing: 0.02em;
    }}

    /* — Pills */
    .pill {{
      display: inline-flex; align-items: center; gap: 5px;
      font-size: 12px; font-weight: 600;
      padding: 3px 10px; border-radius: 999px;
    }}
    .priority-dot {{
      width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
    }}

    /* — Domains */
    .domains-row {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .domain-pill {{
      font-size: 12px; font-weight: 500; color: var(--teal-dark);
      text-decoration: none;
      background: var(--teal-bg); padding: 4px 12px; border-radius: 999px;
      border: 1px solid var(--teal-light);
      transition: background 0.15s, color 0.15s;
    }}
    .domain-pill:hover {{
      background: var(--teal); color: white; border-color: var(--teal);
    }}

    /* — Metrics strip */
    .metrics-row {{
      display: flex; gap: 0;
      background: var(--surface2);
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      overflow: hidden;
    }}
    .metric {{
      flex: 1; padding: 14px 12px; text-align: center;
      border-right: 1px solid var(--border);
    }}
    .metric:last-child {{ border-right: none; }}
    .metric-val {{
      display: block;
      font-size: 24px; font-weight: 800; letter-spacing: -0.04em;
      color: var(--text); line-height: 1;
    }}
    .metric-lbl {{
      display: block;
      font-size: 10px; font-weight: 500; letter-spacing: 0.06em;
      text-transform: uppercase; color: var(--text-3); margin-top: 4px;
    }}

    /* — Sections */
    .section-block {{ display: flex; flex-direction: column; gap: 8px; }}
    .section-label {{
      font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--text-3);
    }}
    .tags-row {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .tag {{
      font-size: 12px; font-weight: 500;
      padding: 4px 10px; border-radius: 8px;
    }}
    .tag-bot {{
      background: linear-gradient(135deg, var(--teal-bg), #f0f9fa);
      color: var(--teal-dark);
      border: 1px solid var(--teal-light);
    }}
    .tag-muted {{ background: var(--muted-bg); color: var(--muted); }}

    /* — Pages grid */
    .pages-grid {{
      display: flex; flex-direction: column; gap: 1px;
      background: var(--border);
      border-radius: var(--radius-sm);
      overflow: hidden;
      border: 1px solid var(--border);
    }}
    .page-item {{
      display: flex; align-items: center; gap: 10px;
      padding: 9px 12px;
      background: var(--surface);
      transition: background 0.12s;
    }}
    .page-item:hover {{ background: var(--surface2); }}
    .page-dot {{ width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }}
    .page-info {{ flex: 1; min-width: 0; display: flex; align-items: baseline; gap: 8px; }}
    .page-name {{ font-size: 13px; font-weight: 500; color: var(--text-2); white-space: nowrap; }}
    .page-path {{ font-size: 12px; color: var(--text-3); font-family: 'SF Mono', Menlo, monospace; overflow: hidden; text-overflow: ellipsis; }}
    .version-tag {{
      flex-shrink: 0;
      font-size: 10px; font-weight: 600;
      background: var(--teal-bg); color: var(--teal-dark);
      border: 1px solid var(--teal-light);
      padding: 2px 7px; border-radius: 999px;
    }}
    .empty-state {{ font-size: 13px; color: var(--text-3); padding: 8px 0; }}

    /* ── FOOTER ──────────────────────────── */
    footer {{
      border-top: 1px solid var(--border);
      padding: 32px;
      text-align: center;
    }}
    .footer-text {{ font-size: 12px; color: var(--text-3); }}
    .footer-text a {{ color: var(--accent); text-decoration: none; font-weight: 500; }}
    .footer-brand {{
      display: inline-block; margin-top: 8px;
      font-size: 13px; font-weight: 700; letter-spacing: 0.06em;
      background: linear-gradient(90deg, #5BBFC4, #C47890, #C4A882);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }}

    /* ── RESPONSIVE ──────────────────────── */
    @media (max-width: 600px) {{
      .nav-inner {{ padding: 0 20px; }}
      .hero {{ padding: 60px 20px 56px; }}
      .main {{ padding: 40px 20px 60px; }}
      .cards-grid {{ gap: 16px; }}
      .card {{ padding: 20px; }}
      .stat-item {{ padding: 16px 18px; }}
    }}
  </style>
</head>
<body>

<nav>
  <div class="nav-inner">
    <div class="nav-brand">
      <img src="assets/logo-ikigai.jpeg" alt="IKIGAI" class="nav-logo-img">
      <span class="nav-logo-text">IKIGAI</span>
      <div class="nav-sep"></div>
      <span class="nav-sub">Panel Maestro</span>
    </div>
    <div class="nav-meta">
      {now} ·
      <a href="https://github.com/qruzharturousa-byte/ikigai-clients-db" target="_blank">ikigai-clients-db ↗</a>
    </div>
  </div>
</nav>

<section class="hero">
  <div class="hero-orb orb-1"></div>
  <div class="hero-orb orb-2"></div>
  <div class="hero-orb orb-3"></div>
  <div class="hero-content">
    <div class="hero-logo-wrap">
      <img src="assets/logo-ikigai.jpeg" alt="IKIGAI" class="hero-logo">
    </div>
    <div class="hero-eyebrow">Plataforma IKIGAI · v1.0</div>
    <h1 class="hero-title">
      Clientes <span class="hero-gradient-word">IKIGAI</span><br>en un solo lugar
    </h1>
    <p class="hero-sub">Base de datos versionada · Bots IA · Páginas · Sistemas</p>
    <div class="stats-bar">
      {stats_html}
    </div>
  </div>
</section>

<main class="main">
  <div class="section-title">Clientes activos y en desarrollo</div>
  <div class="cards-grid">
    {cards}
  </div>
</main>

<footer>
  <p class="footer-text">
    Generado automáticamente desde
    <a href="https://github.com/qruzharturousa-byte/ikigai-clients-db" target="_blank">ikigai-clients-db</a>
    · {now}
  </p>
  <div class="footer-brand">I K I G A I</div>
</footer>

</body>
</html>'''

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    clients = load_clients()
    if not clients:
        print("❌ No se encontraron clientes en 02_CLIENTES/")
        sys.exit(1)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(generate_html(clients), encoding='utf-8')
    total = sum(c.get('pages_count', 0) for c in clients)
    print(f"✅ Panel generado — {len(clients)} clientes · {total} páginas")
    print(f"   → {OUT}")
