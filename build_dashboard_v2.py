import json, datetime, os
import urllib.request

def get_bna_tc_historical():
    """Obtiene tipos de cambio BNA vendedor oficial históricos (diarios) desde Bluelytics"""
    try:
        url = 'https://api.bluelytics.com.ar/v2/evolution.json?days=2000'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            tc_dict = {}
            for entry in data:
                # Filtrar solo los datos del BNA oficial (source = "Oficial")
                if entry.get('source') == 'Oficial':
                    date_str = entry.get('date')  # formato: YYYY-MM-DD
                    if date_str:
                        try:
                            sell_rate = entry.get('value_sell')  # TC vendedor
                            if sell_rate:
                                # Usar YYYY-M-D como clave (día específico)
                                tc_dict[date_str] = round(float(sell_rate))
                        except (ValueError, KeyError, TypeError):
                            continue

            if tc_dict:
                print(f"OK: Obtenidos {len(tc_dict)} tipos de cambio BNA diarios desde Bluelytics")
                return tc_dict
            return None

    except Exception as e:
        print(f"Advertencia: No se pudo obtener TC del BNA ({e}). Usando valores por defecto.")
        return None

# Intentar obtener TC del BNA, usar default si falla
tc_bna = get_bna_tc_historical()

with open('C:/Users/usuario/OneDrive/Escritorio/CLAUDE/ventas_data_v5.json', 'r', encoding='utf-8') as f:
    compact = json.load(f)
data_js = json.dumps(compact, ensure_ascii=False, separators=(',',':'))
today = datetime.date.today()
fecha_es = today.strftime('%d de %B de %Y').replace('January','enero').replace('February','febrero').replace('March','marzo').replace('April','abril').replace('May','mayo').replace('June','junio').replace('July','julio').replace('August','agosto').replace('September','septiembre').replace('October','octubre').replace('November','noviembre').replace('December','diciembre')

# Find max month with data
max_year = max(r['a'] for r in compact)
max_month_in_max_year = max(r['m'] for r in compact if r['a']==max_year)
MESES_ES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
partial_label = f"{max_year} = enero–{MESES_ES[max_month_in_max_year-1]}"

html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Ventas Luctron</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --c-dark:#000000;--c-midnight:#0F0F0F;--c-deep-blue:#0C2136;--c-misty-blue:#3E688F;
  --c-white:#FFFFFF;--c-light-gray:#E8E8E8;--c-medium-gray:#B0B0B0;
  --bg:#F2F2F2;--surface:#FFFFFF;--surface-2:#FAFAFA;--surface-hover:#F6F6F6;
  --feature-bg:#0C2136;
  --border:#E4E4E4;--border-soft:#EDEDED;--border-strong:#D8D8D8;
  --text:#0F0F0F;--text-2:#2A2A2A;--muted:#6B6B6B;--muted-2:#9A9A9A;
  --on-dark:#FFFFFF;--on-dark-muted:#B7C3D1;
  --accent:#0C2136;--accent-2:#3E688F;--accent-soft:#ECF1F7;
  --verde:#2E7A4F;--verde-bg:#E8F4ED;--verde-border:#B8DCC4;
  --amarillo:#B07410;--amarillo-bg:#FCF3DE;--amarillo-border:#ECD79B;
  --rojo:#B33B3A;--rojo-bg:#FDECEC;--rojo-border:#F5C9C8;
  --azul-st:#3E688F;--azul-st-bg:#E8EEF5;--azul-st-border:#BACBDF;
  --font:"Inter","Segoe UI",-apple-system,Arial,sans-serif;
  --radius:14px;--radius-sm:10px;--radius-xs:6px;--pill:999px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:var(--bg);color:var(--text);font-size:13.5px;line-height:1.5;-webkit-font-smoothing:antialiased;letter-spacing:-0.005em}

/* Top toolbar */
.toolbar{background:var(--surface);padding:10px 22px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);font-size:13px}
.toolbar .left{display:flex;align-items:center;gap:14px;color:var(--text-2)}
.toolbar .left .title{font-weight:600;color:var(--text)}
.toolbar .right{display:flex;align-items:center;gap:18px;color:var(--muted);font-size:13px}
.toolbar .right .version b{color:var(--text);font-weight:600}

/* Header */
header{background:var(--feature-bg);color:var(--on-dark);padding:22px 32px}
header h1{font-size:20px;font-weight:700;letter-spacing:-0.4px;display:flex;align-items:center;gap:10px}
header .icon{color:#fbbf24;font-size:20px}
header .sub{font-size:12px;color:var(--on-dark-muted);margin-top:5px}

/* Tabs */
.tabs{background:var(--surface);padding:0 32px;border-bottom:1px solid var(--border);display:flex;gap:0;position:sticky;top:0;z-index:100}
.tab{padding:14px 20px;font-size:13px;color:var(--muted);cursor:pointer;border-bottom:3px solid transparent;font-weight:500;transition:color .12s;background:none;border-top:none;border-left:none;border-right:none;font-family:inherit;display:flex;align-items:center;gap:6px}
.tab:hover{color:var(--text)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent);font-weight:600}

/* Filters */
.filters{position:sticky;top:50px;z-index:99;background:var(--surface);padding:14px 32px 12px;border-bottom:1px solid var(--border-soft);display:flex;align-items:center;flex-wrap:wrap;gap:14px}
.filters-left{display:flex;align-items:center;gap:10px;flex-wrap:wrap;flex:1}
.filters-label{font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.7px;text-transform:uppercase}
.year-pill{padding:5px 15px;border-radius:var(--pill);border:1px solid var(--border);background:var(--surface);cursor:pointer;font-size:12.5px;color:var(--text-2);transition:border-color .12s;font-family:inherit;font-weight:500}
.year-pill:hover{border-color:var(--border-strong)}
.year-pill.active{background:var(--c-midnight);border-color:var(--c-midnight);color:var(--c-white);font-weight:600}
.filters-right{display:flex;align-items:center;gap:14px;font-size:13px}
.filters-right a{color:var(--accent-2);cursor:pointer;text-decoration:none;font-weight:500}
.filters-right a:hover{color:var(--accent)}
.filters-right span{color:var(--border)}
.filter-note{padding:0 32px 10px;background:var(--surface);font-size:12px;color:var(--muted);display:flex;align-items:center;gap:10px;border-bottom:1px solid var(--border)}
.filter-badge{background:var(--accent-soft);color:var(--accent);padding:2px 10px;border-radius:var(--pill);font-weight:600;font-size:11px}

/* Main */
.main{padding:24px 32px;display:grid;gap:20px}

/* KPIs */
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}
.kpi{background:var(--surface);border-radius:var(--radius-sm);padding:16px 20px;border:1px solid var(--border)}
.kpi-label{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.7px;margin-bottom:8px}
.kpi-value{font-size:26px;font-weight:700;color:var(--accent);line-height:1.1;margin-bottom:4px;font-variant-numeric:tabular-nums;letter-spacing:-0.4px}
.kpi-sub{font-size:12px;color:var(--muted-2);margin-top:4px}
.kpi-strong{font-size:13px;color:var(--text);font-weight:600;margin-top:6px}

/* Section */
.section{background:var(--surface);border-radius:var(--radius);padding:20px 22px;border:1px solid var(--border)}
.section-title{font-size:14px;font-weight:600;color:var(--text);margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;letter-spacing:-0.1px}
.section-title .sub{font-size:12px;color:var(--muted);font-weight:400}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}

/* Charts */
svg{display:block;width:100%}
svg text{font-family:var(--font)}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin-top:10px;font-size:12px;color:var(--muted)}
.legend-item{display:flex;align-items:center;gap:5px}
.legend-dot{width:10px;height:10px;border-radius:2px}

/* Tables */
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{background:var(--surface);padding:8px 12px;text-align:right;font-weight:600;color:var(--muted);border-bottom:1px solid var(--border-soft);font-size:10px;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
th:first-child{text-align:left}
td{padding:8px 12px;text-align:right;border-bottom:1px solid var(--border-soft);color:var(--text-2);font-variant-numeric:tabular-nums}
td:first-child{text-align:left;font-weight:500;color:var(--text)}
tr:hover td{background:var(--surface-hover)}
tr.total td{background:var(--surface-2);font-weight:700;border-top:1px solid var(--border)}

/* Panels */
.panel{display:none}
.panel.active{display:grid;gap:20px}

/* Status pills */
.status{display:inline-block;padding:2px 9px;border-radius:var(--pill);font-size:11px;font-weight:700}
.status-good{background:var(--verde-bg);color:var(--verde)}
.status-warn{background:var(--amarillo-bg);color:var(--amarillo)}
.status-bad{background:var(--rojo-bg);color:var(--rojo)}

/* Origen toggle */
.origen-toggle{display:inline-flex;background:var(--bg);border-radius:var(--radius-xs);padding:3px;gap:0;border:1px solid var(--border)}
.orig-btn{padding:6px 14px;border:0;background:transparent;cursor:pointer;font-size:12.5px;font-weight:600;color:var(--muted);border-radius:3px;font-family:inherit;transition:all .12s}
.orig-btn:hover{color:var(--text)}
.orig-btn.active[data-or="ambos"]{background:var(--c-midnight);color:var(--c-white)}
.orig-btn.active[data-or="nacional"]{background:var(--verde);color:#fff}
.orig-btn.active[data-or="importado"]{background:var(--amarillo);color:#fff}

/* Origen period selector */
.origen-period{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:12px;padding-top:12px;border-top:1px solid var(--border-soft)}
.orig-period-btn{padding:4px 12px;border:1px solid var(--border);background:var(--surface);cursor:pointer;font-size:11.5px;font-weight:500;color:var(--text-2);border-radius:var(--pill);font-family:inherit;transition:all .12s}
.orig-period-btn:hover{border-color:var(--border-strong)}
.orig-period-btn.active{background:var(--c-midnight);border-color:var(--c-midnight);color:var(--c-white);font-weight:600}

/* Currency toggle */
.currency-toggle{display:inline-flex;background:var(--bg);border-radius:var(--radius-xs);padding:2px;gap:0;border:1px solid var(--border)}
.curr-btn{padding:4px 11px;border:0;background:transparent;cursor:pointer;font-size:12px;font-weight:600;color:var(--muted);border-radius:3px;font-family:inherit;transition:all .12s}
.curr-btn.active{background:var(--c-midnight);color:var(--c-white)}

/* Month filters */
.filters.filters-months{padding-top:0;border-top:0;background:var(--surface-2);border-bottom:1px solid var(--border)}
.month-pill{padding:3px 9px;border-radius:var(--radius-xs);border:1px solid var(--border);background:var(--surface);cursor:pointer;font-size:11px;color:var(--text-2);font-weight:500;font-family:inherit;transition:all .12s}
.month-pill:hover{border-color:var(--border-strong)}
.month-pill.active{background:var(--accent-2);color:#fff;border-color:var(--accent-2);font-weight:600}

/* Quick buttons */
.quick-btn{padding:5px 13px;border-radius:var(--pill);border:1px solid var(--border);background:var(--surface);cursor:pointer;font-size:12px;color:var(--text-2);font-weight:500;font-family:inherit;transition:all .12s}
.quick-btn:hover{border-color:var(--border-strong)}
.quick-btn.active{background:var(--c-midnight);color:var(--c-white);border-color:var(--c-midnight)}
.vend-pill{padding:4px 11px;border-radius:var(--pill);border:1px solid var(--border);background:var(--surface);cursor:pointer;font-size:12px;color:var(--text-2);font-weight:500;font-family:inherit;display:inline-flex;align-items:center;gap:6px;transition:all .12s}
.vend-pill .dot{width:7px;height:7px;border-radius:var(--pill)}
.vend-pill.active{border-color:var(--border-strong);color:var(--text);font-weight:600}

/* Story cards (Vendedores tab) */
.story-card{background:var(--surface);border-radius:var(--radius);padding:18px 20px;border:1px solid var(--border);border-top:3px solid var(--accent);position:relative}
.story-card .tag{position:absolute;top:-9px;left:16px;background:var(--accent);color:#fff;font-size:10px;font-weight:700;padding:3px 9px;border-radius:var(--radius-xs);letter-spacing:.6px;text-transform:uppercase}
.story-card.green{border-top-color:var(--verde)} .story-card.green .tag{background:var(--verde)}
.story-card.purple{border-top-color:#6d4aad} .story-card.purple .tag{background:#6d4aad}
.story-card.amber{border-top-color:var(--amarillo)} .story-card.amber .tag{background:var(--amarillo)}
.story-card .name{font-size:17px;font-weight:700;color:var(--text);margin-top:6px;line-height:1.2;letter-spacing:-0.2px}
.story-card .figure{font-size:13.5px;color:var(--text-2);margin-top:8px;font-weight:600}
.story-card .note{font-size:12px;color:var(--muted);margin-top:4px}
.story-card .delta{font-size:12px;font-weight:600;margin-top:8px;display:inline-flex;align-items:center;gap:4px}
.story-card .delta.up{color:var(--verde)} .story-card .delta.down{color:var(--rojo)} .story-card .delta.new{color:#6d4aad}

/* Trend cells */
.trend-up{color:var(--verde);font-weight:600}
.trend-down{color:var(--rojo);font-weight:600}
.trend-new{color:#6d4aad;font-weight:600}

/* Strategy cards */
.strat-card{background:var(--surface);border-radius:var(--radius);padding:20px;border:1px solid var(--border);border-left:3px solid var(--accent)}
.strat-card.warn{border-left-color:var(--amarillo)}
.strat-card.good{border-left-color:var(--verde)}
.strat-card h4{font-size:13.5px;color:var(--text);margin-bottom:8px;font-weight:600}
.strat-card p{font-size:12.5px;color:var(--text-2);line-height:1.6}
.strat-card .big{font-size:26px;font-weight:700;color:var(--accent);margin:6px 0;font-variant-numeric:tabular-nums;letter-spacing:-0.4px}
.strat-card.warn .big{color:var(--amarillo)}
.strat-card.good .big{color:var(--verde)}

@media(max-width:1100px){.kpis{grid-template-columns:repeat(3,1fr)}.grid-3{grid-template-columns:1fr}}
@media(max-width:760px){.kpis{grid-template-columns:1fr 1fr}.grid-2{grid-template-columns:1fr}.main{padding:14px}.tabs{padding:0 14px;overflow-x:auto}.filters{padding:14px}}
</style>
</head>
<body>

<div class="toolbar">
  <div class="left">
    <span class="title">Dashboard Ventas Luctron</span>
  </div>
  <div class="right">
    <span class="version">Versi&oacute;n <b>Actual</b></span>
  </div>
</div>

<header style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
  <div>
    <h1><span class="icon">&#9889;</span> Luctron Led Lighting &mdash; Dashboard de Ventas</h1>
    <div class="sub">Datos desde enero 2020 &middot; Valores en USD &middot; Actualizado al """ + fecha_es + """</div>
  </div>
  <button id="btn-refresh-dash" onclick="actualizarDashboard()" style="padding:9px 18px;border-radius:8px;border:0;cursor:pointer;font-size:13px;font-weight:600;font-family:inherit;background:#fff;color:#1e3a5f;display:inline-flex;align-items:center;gap:8px;box-shadow:0 1px 3px rgba(0,0,0,.15)">&#128260; Actualizar datos</button>
</header>

<div class="tabs">
  <button class="tab active" data-tab="resumen">Resumen General</button>
  <button class="tab" data-tab="mensual">Evoluci&oacute;n Mensual</button>
  <button class="tab" data-tab="vend">Vendedores</button>
  <button class="tab" data-tab="cli">Clientes &amp; Productos</button>
  <button class="tab" data-tab="origen">&#127760; Origen</button>
  <button class="tab" data-tab="diario">&#128197; Diario</button>
  <button class="tab" data-tab="estr">&#127919; Estrategia</button>
</div>

<div class="filters">
  <div class="filters-left">
    <span class="filters-label">A&Ntilde;OS:</span>
    <div id="year-pills" style="display:flex;gap:8px;flex-wrap:wrap"></div>
  </div>
  <div class="filters-right" style="gap:14px">
    <div class="currency-toggle">
      <button class="curr-btn active" id="curr-usd">USD</button>
      <button class="curr-btn" id="curr-ars">ARS</button>
    </div>
    <a id="sel-todos">Todos</a>
    <span>|</span>
    <a id="sel-ultimos3">&Uacute;ltimos 3</a>
    <span>|</span>
    <label style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--muted);font-weight:500;cursor:default">
      Target
      <input type="number" id="target-input" min="0" step="5000"
             style="width:96px;font-size:12.5px;padding:3px 8px;border:1px solid var(--border);border-radius:6px;
                    text-align:right;font-family:inherit;font-variant-numeric:tabular-nums;
                    background:var(--surface);color:var(--text);font-weight:600">
      <span id="target-currency-label" style="font-size:11px;color:var(--muted-2)">USD/mes</span>
    </label>
  </div>
</div>

<div class="filters filters-months">
  <div class="filters-left">
    <span class="filters-label">MESES:</span>
    <div id="month-pills" style="display:flex;gap:5px;flex-wrap:wrap"></div>
  </div>
  <div class="filters-right">
    <a id="sel-months-actual" style="font-weight:700;color:#2563eb">Mes actual</a>
    <span>|</span>
    <a id="sel-months-todos">Todos</a>
    <span>|</span>
    <a id="sel-months-q1">Q1</a>
    <span>|</span>
    <a id="sel-months-q2">Q2</a>
    <span>|</span>
    <a id="sel-months-q3">Q3</a>
    <span>|</span>
    <a id="sel-months-q4">Q4</a>
    <span>|</span>
    <a id="sel-months-ytd">YTD</a>
  </div>
</div>

<div class="filter-note">
  <span>* """ + partial_label + """ &middot; </span>
  <span>Mostrando:</span>
  <span class="filter-badge" id="filter-badge">""" + str(max_year) + """</span>
  <span class="filter-badge" id="filter-badge-months" style="background:#fef3c7;color:#92400e;margin-left:6px">12 meses</span>
  <span class="filter-badge" id="filter-badge-curr" style="background:#dcfce7;color:#166534;margin-left:6px">USD</span>
</div>
<div style="padding:8px 32px;background:#f9fafb;border-bottom:1px solid #e5e7eb;font-size:11px;color:#6b7280" id="note-tc-text">
  <b>Vista en USD:</b> ventas en ARS convertidas con TC BNA oficial hist&oacute;rico mensual. Las facturas en USD se toman directamente.
</div>

<div class="main">
  <!-- Resumen General -->
  <div class="panel active" id="panel-resumen">
    <div class="section">
      <div class="section-title">Evoluci&oacute;n mensual total <span class="sub" id="evol-resumen-sub">USD facturado mes a mes</span></div>
      <div id="chart-evol-resumen"></div>
    </div>
    <div class="kpis" id="kpis"></div>
    <div class="grid-2">
      <div class="section">
        <div class="section-title">Evoluci&oacute;n anual <span class="sub">USD facturado</span></div>
        <div id="chart-annual"></div>
      </div>
      <div class="section">
        <div class="section-title">Top 5 vendedores <span class="sub" id="top-vend-sub"></span></div>
        <div id="chart-top-vend"></div>
      </div>
    </div>
    <div class="section">
      <div class="section-title">Resumen por a&ntilde;o <span class="sub">Comparativa hist&oacute;rica</span></div>
      <div id="table-annual" style="overflow-x:auto"></div>
    </div>
  </div>

  <!-- Evolucion Mensual -->
  <div class="panel" id="panel-mensual">
    <div class="section">
      <div class="section-title">Facturaci&oacute;n mensual <span class="sub" id="monthly-sub"></span></div>
      <div id="chart-monthly"></div>
      <div class="legend" id="monthly-legend"></div>
    </div>
    <div class="section">
      <div class="section-title">Detalle mensual <span class="sub">USD por mes vs target</span></div>
      <div id="table-monthly" style="overflow-x:auto"></div>
    </div>
  </div>

  <!-- Vendedores -->
  <div class="panel" id="panel-vend">
    <div id="vend-story-cards" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px"></div>
    <div class="section">
      <div class="section-title">Evoluci&oacute;n mensual por vendedor <span class="sub" id="evol-vend-sub">Una l&iacute;nea por vendedor seleccionado</span></div>
      <div id="chart-evol-vend"></div>
    </div>

    <div class="section">
      <div class="section-title">Ventas por vendedor por a&ntilde;o (USD)
        <span class="sub" id="vend-story-sub"></span>
      </div>
      <div class="vend-toggle-bar" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:14px">
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;flex:1">
          <span class="filters-label">VER:</span>
          <div id="vend-pills" style="display:flex;gap:6px;flex-wrap:wrap"></div>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          <button class="quick-btn" id="sel-vend-todos">Todos</button>
          <button class="quick-btn active" id="sel-vend-activo">Solo equipo activo</button>
        </div>
      </div>
      <div style="font-size:11px;color:#9ca3af;margin-bottom:10px">Hac&eacute; clic en cada vendedor para mostrar u ocultar</div>
      <div id="chart-vend-byyear"></div>
      <div style="font-size:11px;color:#6b7280;margin-top:14px;padding:10px 14px;background:#f9fafb;border-radius:6px;border-left:3px solid #d1d5db">
        * INX2 = cartera de Nacho. Oscar incluido en Lucas/Federico desde 2025.
      </div>
    </div>

    <div class="section">
      <div class="section-title">Detalle por vendedor <span class="sub" id="vend-table-sub">Todos</span></div>
      <div id="table-vend" style="overflow-x:auto"></div>
    </div>
  </div>

  <!-- Clientes & Productos -->
  <div class="panel" id="panel-cli">
    <div class="section">
      <div class="section-title">Evoluci&oacute;n mensual por familia de producto <span class="sub" id="evol-prod-sub">Top 6 familias</span></div>
      <div id="chart-evol-prod"></div>
    </div>
    <div class="grid-2">
      <div class="section">
        <div class="section-title">Top 15 clientes <span class="sub" id="cli-sub"></span></div>
        <div id="chart-top-cli"></div>
      </div>
      <div class="section">
        <div class="section-title">Concentraci&oacute;n de cartera <span class="sub">Principio de Pareto</span></div>
        <div id="chart-pareto"></div>
        <div id="pareto-text" style="margin-top:14px;padding:12px;background:#f9fafb;border-radius:8px;font-size:13px;color:#374151"></div>
      </div>
    </div>

    <div class="grid-2">
      <div class="section">
        <div class="section-title">Familias de producto <span class="sub" id="prod-sub"></span></div>
        <div id="chart-products"></div>
      </div>
      <div class="section">
        <div class="section-title">Evoluci&oacute;n por familia <span class="sub">Top 6 por año</span></div>
        <div id="chart-prod-evol"></div>
      </div>
    </div>
    <div class="section">
      <div class="section-title">Detalle clientes (top 30) <span class="sub" id="cli-table-sub"></span></div>
      <div id="table-cli" style="overflow-x:auto"></div>
    </div>
    <div class="section">
      <div class="section-title">Detalle por familia de producto <span class="sub" id="prod-table-sub"></span></div>
      <div id="table-products" style="overflow-x:auto"></div>
    </div>

    <!-- Alertas comerciales -->
    <div class="grid-3">
      <div class="section" style="padding:16px 18px">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px;gap:8px;flex-wrap:wrap">
          <div>
            <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px">Clientes nuevos</div>
            <div style="font-size:11px;color:var(--muted)">Primera compra registrada</div>
          </div>
          <select id="alerta-nuevos-sel" style="font-size:11.5px;padding:4px 8px;border:1px solid var(--border);border-radius:6px;background:var(--surface);color:var(--text);font-family:inherit;cursor:pointer"></select>
        </div>
        <div id="alerta-nuevos-body"></div>
      </div>
      <div class="section" style="padding:16px 18px">
        <div style="margin-bottom:12px">
          <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px">Candidatos a reactivaci&oacute;n</div>
          <div style="font-size:11px;color:var(--muted);display:flex;align-items:center;gap:4px">Sin compras en los &uacute;ltimos <input type="number" id="alerta-reactiv-n" value="24" min="6" max="60" step="6" style="width:44px;font-size:11.5px;padding:2px 5px;border:1px solid var(--border);border-radius:5px;text-align:center;font-family:inherit"> meses &middot; <span id="alerta-reactiv-count" style="color:var(--muted-2)"></span></div>
        </div>
        <div id="alerta-reactiv-body"></div>
      </div>
      <div class="section" style="padding:16px 18px">
        <div style="margin-bottom:12px">
          <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px" id="alerta-activos-title">Sin comprar en el a&ntilde;o en curso</div>
          <div style="font-size:11px;color:var(--muted);display:flex;align-items:center;gap:4px">Que compraron en los &uacute;ltimos <input type="number" id="alerta-activos-n" value="3" min="1" max="5" style="width:38px;font-size:11.5px;padding:2px 5px;border:1px solid var(--border);border-radius:5px;text-align:center;font-family:inherit"> a&ntilde;os &middot; <span id="alerta-activos-count" style="color:var(--muted-2)"></span></div>
        </div>
        <div id="alerta-activos-body"></div>
      </div>
    </div>
  </div>

  <!-- Origen (Nacional vs Importado) -->
  <div class="panel" id="panel-origen">
    <div class="section" style="padding-bottom:14px">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px">
        <div>
          <div class="section-title" style="margin-bottom:6px">Origen del producto <span class="sub">Filtr&aacute; entre nacional, importado o ambos</span></div>
          <div style="font-size:12px;color:#6b7280">Productos nacionales = producci&oacute;n local de Luctron. Importados: ANKA, HOLT, LENA, VIKS, BODO, LIER. Servicios y "NO APLICA" quedan fuera.</div>
        </div>
        <div class="origen-toggle">
          <button class="orig-btn active" data-or="ambos">Ambos</button>
          <button class="orig-btn" data-or="nacional">Nacional</button>
          <button class="orig-btn" data-or="importado">Importado</button>
        </div>
      </div>
      <div class="origen-period">
        <span style="font-size:11px;font-weight:700;color:#6b7280;letter-spacing:.7px">PER&Iacute;ODO:</span>
        <button class="orig-period-btn" data-months="all">Todo el a&ntilde;o</button>
        <button class="orig-period-btn" data-months="1,2,3">Q1 ene&ndash;mar</button>
        <button class="orig-period-btn" data-months="4,5,6">Q2 abr&ndash;jun</button>
        <button class="orig-period-btn" data-months="7,8,9">Q3 jul&ndash;sep</button>
        <button class="orig-period-btn" data-months="10,11,12">Q4 oct&ndash;dic</button>
        <button class="orig-period-btn" data-months="1,2,3,4,5,6">1er semestre</button>
        <button class="orig-period-btn" data-months="7,8,9,10,11,12">2do semestre</button>
        <span id="origen-period-label" style="font-size:12px;color:#2563eb;font-weight:600;margin-left:4px"></span>
      </div>
    </div>

    <div id="origen-kpis" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px"></div>

    <div class="section">
      <div class="section-title">Evoluci&oacute;n mensual <span class="sub" id="evol-origen-sub"></span></div>
      <div id="chart-evol-origen"></div>
    </div>

    <div class="grid-2">
      <div class="section">
        <div class="section-title">Participaci&oacute;n nacional / importado <span class="sub">Apilado por a&ntilde;o</span></div>
        <div id="chart-orig-stack"></div>
      </div>
      <div class="section">
        <div class="section-title">% Importado por a&ntilde;o <span class="sub">Tendencia hist&oacute;rica</span></div>
        <div id="chart-orig-pct"></div>
      </div>
    </div>

    <div class="grid-2">
      <div class="section">
        <div class="section-title">Familias de producto <span class="sub" id="origen-fam-sub"></span></div>
        <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:16px;align-items:start">
          <div id="chart-origen-fam"></div>
          <div id="chart-origen-pie"></div>
        </div>
      </div>
      <div class="section">
        <div class="section-title">Top clientes <span class="sub" id="origen-cli-sub"></span></div>
        <div id="chart-origen-cli"></div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Detalle por familia <span class="sub" id="origen-tbl-sub"></span></div>
      <div id="origen-fam-table" style="overflow-x:auto"></div>
    </div>

    <div class="section">
      <div class="section-title">Resumen nacional vs importado por a&ntilde;o</div>
      <div id="orig-table" style="overflow-x:auto"></div>
    </div>
  </div>

  <!-- Diario -->
  <div class="panel" id="panel-diario">
    <div class="section" style="padding-bottom:14px">
      <div class="section-title" style="margin-bottom:6px">Facturaci&oacute;n d&iacute;a por d&iacute;a <span class="sub" id="diario-sub"></span></div>
      <div style="font-size:12px;color:#6b7280">Us&aacute; los filtros globales de a&ntilde;o y mes para definir el per&iacute;odo. Cada barra representa el total facturado en ese d&iacute;a (con las NC restadas).</div>
    </div>
    <div id="diario-kpis" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px"></div>
    <div class="section">
      <div class="section-title">Facturaci&oacute;n diaria <span class="sub" id="diario-chart-sub"></span></div>
      <div id="chart-diario"></div>
    </div>
    <div class="section">
      <div class="section-title">Detalle por d&iacute;a <span class="sub" id="diario-tbl-sub"></span></div>
      <div id="table-diario" style="overflow-x:auto;max-height:600px;overflow-y:auto"></div>
    </div>
  </div>

  <!-- Estrategia -->
  <div class="panel" id="panel-estr">
    <div class="grid-3" id="strat-cards"></div>
    <div class="section">
      <div class="section-title">Evoluci&oacute;n mensual vs target <span class="sub" id="evol-estr-sub">Cada mes vs target</span></div>
      <div id="chart-evol-estr"></div>
    </div>
    <div class="section">
      <div class="section-title"><span id="gap-title">An&aacute;lisis de brecha vs objetivo</span></div>
      <div id="chart-gap"></div>
    </div>
    <div class="section">
      <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:14px;gap:10px;flex-wrap:wrap">
        <div class="section-title" style="margin-bottom:0">Targets mensuales <span class="sub">Click en una celda para editar &middot; valores en USD &middot; se guardan en el browser</span></div>
        <span style="font-size:11px;color:var(--muted-2)" id="target-table-currency"></span>
      </div>
      <div id="target-table" style="overflow-x:auto"></div>
    </div>
    <div class="grid-2">
      <div class="section">
        <div class="section-title">Estacionalidad <span class="sub">Promedio por mes hist&oacute;rico</span></div>
        <div id="chart-season"></div>
      </div>
      <div class="section">
        <div class="section-title">Recomendaciones</div>
        <div id="recommendations"></div>
      </div>
    </div>
  </div>
</div>

<script>
const VENTAS = """ + data_js + """;

// Tipos de cambio BNA vendedor oficial (actualizado desde Bluelytics)
const TC = """ + json.dumps(tc_bna if tc_bna else {}) + """;
// Si TC está vacío, usar defaults históricos
if(!Object.keys(TC).length){
  Object.assign(TC, {
    '2020-1':63,'2020-2':64,'2020-3':66,'2020-4':67,'2020-5':68,'2020-6':70,
    '2020-7':73,'2020-8':74,'2020-9':76,'2020-10':79,'2020-11':81,'2020-12':84,
    '2021-1':85,'2021-2':88,'2021-3':91,'2021-4':93,'2021-5':96,'2021-6':98,
    '2021-7':100,'2021-8':102,'2021-9':99,'2021-10':100,'2021-11':102,'2021-12':104,
    '2022-1':107,'2022-2':108,'2022-3':111,'2022-4':114,'2022-5':121,'2022-6':126,
    '2022-7':131,'2022-8':137,'2022-9':145,'2022-10':155,'2022-11':163,'2022-12':176,
    '2023-1':188,'2023-2':196,'2023-3':205,'2023-4':214,'2023-5':239,'2023-6':263,
    '2023-7':268,'2023-8':350,'2023-9':350,'2023-10':354,'2023-11':368,'2023-12':800,
    '2024-1':810,'2024-2':843,'2024-3':868,'2024-4':874,'2024-5':906,'2024-6':935,
    '2024-7':974,'2024-8':995,'2024-9':1007,'2024-10':1022,'2024-11':1048,'2024-12':1005,
    '2025-1':1060,'2025-2':1072,'2025-3':1080,'2025-4':1150,'2025-5':1200,'2025-6':1250,
    '2025-7':1290,'2025-8':1320,'2025-9':1350,'2025-10':1380,'2025-11':1395,'2025-12':1400,
    '2026-1':1410,'2026-2':1430,'2026-3':1450,'2026-4':1470,'2026-5':1490
  });
}

const DEFAULT_TARGET_USD = 215000; // fallback si no hay target para ese mes
let currency = 'USD'; // 'USD' or 'ARS'
const CURR_SYM = {USD:'$', ARS:'AR$'};
function currentTC(){
  // Latest TC available (busca por día, luego fallback a mes)
  const keys = Object.keys(TC).sort().reverse();
  if(keys.length) return TC[keys[0]];
  return 1000; // fallback
}

// ---- Per-month targets ----
// Stored as { "2026-1": 215000, "2026-6": 250000, ... } — values always in USD
const MONTHLY_TARGETS_KEY = 'luctron_monthly_targets_v2';
let monthlyTargets = JSON.parse(localStorage.getItem(MONTHLY_TARGETS_KEY) || '{}');

function getTargetUSD(y, m){
  // Find the most recent entry in monthlyTargets at or before (y, m)
  const cursor = y * 100 + m;
  let best = null, bestKey = -1;
  Object.entries(monthlyTargets).forEach(([k, v]) => {
    const [ky, km] = k.split('-').map(Number);
    const kc = ky * 100 + km;
    if(kc <= cursor && kc > bestKey){ bestKey = kc; best = v; }
  });
  return best !== null ? best : DEFAULT_TARGET_USD;
}
function getTargetDisplay(y, m){
  return currency==='USD' ? getTargetUSD(y,m) : Math.round(getTargetUSD(y,m)*currentTC());
}
function setMonthTarget(y, m, displayVal){
  const usd = currency==='USD' ? Math.round(displayVal) : Math.round(displayVal/currentTC());
  monthlyTargets[y+'-'+m] = usd;
  localStorage.setItem(MONTHLY_TARGETS_KEY, JSON.stringify(monthlyTargets));
}

// TARGET / TARGET_ANUAL — initialized after TODAY_YEAR/TODAY_MONTH are defined (see below)
let TARGET = DEFAULT_TARGET_USD;
let TARGET_ANUAL = DEFAULT_TARGET_USD * 12;
function updateTargets(){
  TARGET = getTargetDisplay(TODAY_YEAR, TODAY_MONTH);
  TARGET_ANUAL = getTargetUSD(TODAY_YEAR, TODAY_MONTH) * 12;
}
const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
const MONTHS_FULL = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

const YEAR_COLORS = {2020:'#9ca3af',2021:'#60a5fa',2022:'#34d399',2023:'#fbbf24',2024:'#f87171',2025:'#2563eb',2026:'#8b5cf6'};

const PROD_LABELS = {
  'OSLO-EX':'OSLO APE',
  'AURE-EX':'AURE APE'
};
const IMPORTED_FAMS = new Set(['ANKA','HOLT','LENA','VIKS','BODO','LIER']);
const NON_PRODUCT = new Set(['SERVICIOS','NO APLICA']);
function origenOf(fam){
  if(NON_PRODUCT.has(fam)) return 'otros';
  return IMPORTED_FAMS.has(fam)?'importado':'nacional';
}
const VEND_LABELS = {
  'INX2 ILUMINACION SA':'INX2 / Nacho',
  'ANIBAL CASOY':'Anibal Casoy',
  'FACUNDO OROZA':'Facundo Oroza',
  'FEDERICO CAFFARELLI':'Federico Caffarelli',
  'LUCAS LUNA':'Lucas Luna',
  'ARIEL FLORES':'Ariel Flores',
  'SUELEM':'Suelem',
  'MARCOS GOMEZ':'Marcos Gomez',
  'OSCAR NOGUERA':'Oscar Noguera',
  'PABLO DRAGHI':'Pablo Draghi',
  'GRISEL FERNANDEZ':'Grisel Fernandez'
};

const ALL_YEARS = [...new Set(VENTAS.map(r=>r.a))].sort();
const CURRENT_YEAR = Math.max(...ALL_YEARS);
const TODAY = new Date();
const TODAY_YEAR = TODAY.getFullYear();
const TODAY_MONTH = TODAY.getMonth() + 1; // 1-indexed
updateTargets(); // initialize TARGET/TARGET_ANUAL now that TODAY_YEAR/MONTH are known
// Returns true when a month is the current (still-incomplete) month
function isPartialMonth(year, mi){ // mi is 0-based month index
  return year === TODAY_YEAR && (mi + 1) === TODAY_MONTH;
}
const PARTIAL_YEARS = (function(){
  // year is partial if not all 12 months present
  const set = new Set();
  ALL_YEARS.forEach(y=>{
    const months = new Set(VENTAS.filter(r=>r.a===y).map(r=>r.m));
    if(months.size<12) set.add(y);
  });
  return set;
})();

let selYears = new Set([CURRENT_YEAR]); // default año en curso (2026)
if(!ALL_YEARS.includes(CURRENT_YEAR)) selYears = new Set([CURRENT_YEAR-1]);
let selMonths = new Set([1,2,3,4,5,6,7,8,9,10,11,12]); // default all months

// r.t = TOTAL neto en PESOS (ya incluye signo: negativo para NC)
function toUSD(r){
  // Busca TC diario (YYYY-M-D), luego fallback a mes si no existe
  const dayKey = r.a+'-'+String(r.m).padStart(2,'0')+'-'+String(r.d).padStart(2,'0');
  const monthKey = r.a+'-'+r.m;
  const tc = TC[dayKey] || TC[monthKey] || 1000;
  return r.t/tc;
}
function toARS(r){ return r.t; }
function toAmount(r){ return currency==='USD' ? toUSD(r) : toARS(r); }
function inMonth(r){ return selMonths.has(r.m); }

// Per-client metadata (first/last purchase, all years with data) — used by alert panels
const CLIENT_META = (function(){
  const m={};
  VENTAS.forEach(r=>{
    if(!r.c) return;
    if(!m[r.c]) m[r.c]={first:{a:r.a,mo:r.m},last:{a:r.a,mo:r.m},years:new Set([r.a])};
    const cm=m[r.c];
    if(r.a<cm.first.a||(r.a===cm.first.a&&r.m<cm.first.mo)) cm.first={a:r.a,mo:r.m};
    if(r.a>cm.last.a ||(r.a===cm.last.a &&r.m>cm.last.mo))  cm.last ={a:r.a,mo:r.m};
    cm.years.add(r.a);
  });
  return m;
})();

// All year-month combos that exist in data, sorted chronologically
const ALL_YEAR_MONTHS = [...new Set(VENTAS.map(r=>r.a*100+r.m))].sort()
  .map(ym=>({a:Math.floor(ym/100), m:ym%100}));

// Months elapsed from (a,m) to today
function monthsSince(a, m){ return (TODAY_YEAR-a)*12+(TODAY_MONTH-m); }

// Alert state
let alertNuevosYM = ALL_YEAR_MONTHS[ALL_YEAR_MONTHS.length-1]; // most recent month
let alertReactivN = 24;  // months without buying
let alertActivosN = 3;   // last N years
function fmtK(v){
  const sym=CURR_SYM[currency];
  const a=Math.abs(v);
  if(a>=1e9) return sym+(v/1e9).toFixed(2)+'B';
  if(a>=1e6) return sym+(v/1e6).toFixed(2)+'M';
  if(a>=1e3) return sym+(v/1e3).toFixed(0)+'K';
  return sym+Math.round(v);
}
function fmtFull(v){ return CURR_SYM[currency]+Math.round(v).toLocaleString('es-AR'); }
function pct(v,t){ return t>0?Math.round(v/t*100):0; }

// ---- Aggregations ----
function filteredRows(){
  return VENTAS.filter(r=>selYears.has(r.a) && inMonth(r));
}
function totalForYear(y){
  let t=0;
  VENTAS.filter(r=>r.a===y && inMonth(r)).forEach(r=>t+=toAmount(r));
  return t;
}
function monthlyForYear(y){
  const arr=new Array(12).fill(0);
  VENTAS.filter(r=>r.a===y && inMonth(r)).forEach(r=>arr[r.m-1]+=toAmount(r));
  return arr;
}
function vendorTotals(years){
  const res={};
  VENTAS.filter(r=>years.has(r.a) && inMonth(r)).forEach(r=>{
    const v=r.v||'(sin asignar)';
    res[v]=(res[v]||0)+toAmount(r);
  });
  return res;
}
function clientTotals(years){
  const res={};
  VENTAS.filter(r=>years.has(r.a) && inMonth(r)).forEach(r=>{
    const c=r.c||'(sin cliente)';
    res[c]=(res[c]||0)+toAmount(r);
  });
  return res;
}
function productTotals(years){
  const res={};
  VENTAS.filter(r=>years.has(r.a) && inMonth(r)).forEach(r=>{
    const p=r.p||'(sin familia)';
    res[p]=(res[p]||0)+toAmount(r);
  });
  return res;
}
function productByYearTotals(){
  // Returns {familia: {year: total}} — respects month filter
  const res={};
  VENTAS.filter(r=>inMonth(r)).forEach(r=>{
    const p=r.p||'(sin familia)';
    if(!res[p]) res[p]={};
    res[p][r.a]=(res[p][r.a]||0)+toAmount(r);
  });
  return res;
}

// ---- SVG helpers ----
function svg(w,h){ return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet">`; }

// ---- Generic monthly timeline chart (chronological line chart) ----
// series = [{name, color, byKey: {'y-m': value}}], target = optional horizontal line value
function buildMonthlyTimeline(){
  const yrs=[...selYears].sort();
  const timeline=[];
  yrs.forEach(y=>{
    for(let m=1;m<=12;m++){
      if(selMonths.has(m)) timeline.push({y,m,k:y+'-'+m});
    }
  });
  return timeline;
}
function chartMonthlyTimeline(series, opts={}){
  const timeline=buildMonthlyTimeline();
  if(!timeline.length||!series.length) return '<p style="color:#9ca3af;padding:24px">Sin datos para el filtro</p>';
  const showAreaForFirst=opts.area||false;
  const W=920, H=320, PL=68, PR=opts.rightPad||30, PT=20, PB=50;
  const CW=W-PL-PR, CH=H-PT-PB;
  let maxVal=0;
  series.forEach(s=>timeline.forEach(t=>{ const v=s.byKey[t.k]||0; if(v>maxVal) maxVal=v; }));
  // include per-month targets in scale
  timeline.forEach(t=>{ const tv=getTargetDisplay(t.y,t.m); if(tv>maxVal) maxVal=tv; });
  maxVal=maxVal*1.12||1;
  const n=timeline.length;
  const dx = n>1 ? CW/(n-1) : 0;
  let s=svg(W,H);
  // Grid Y
  for(let i=0;i<=5;i++){
    const y=PT+CH*(1-i/5), v=maxVal*i/5;
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${fmtK(v)}</text>`;
  }
  // Year separators (vertical lines at year boundaries)
  let prevY=null;
  timeline.forEach((t,i)=>{
    if(prevY!==null && t.y!==prevY){
      const x=PL+i*dx-dx/2;
      s+=`<line x1="${x.toFixed(1)}" y1="${PT}" x2="${x.toFixed(1)}" y2="${PT+CH}" stroke="#e5e7eb" stroke-dasharray="3,3" stroke-width="1"/>`;
    }
    prevY=t.y;
  });
  // Series lines
  series.forEach((sr,si)=>{
    const pts = timeline.map((t,i)=>{
      const v=sr.byKey[t.k]||0;
      return [PL+i*dx, PT+CH*(1-v/maxVal), v, t];
    });
    if(showAreaForFirst && si===0){
      let area=`M ${pts[0][0].toFixed(1)} ${(PT+CH).toFixed(1)}`;
      pts.forEach(p=>{ area+=` L ${p[0].toFixed(1)} ${p[1].toFixed(1)}`; });
      area+=` L ${pts[pts.length-1][0].toFixed(1)} ${(PT+CH).toFixed(1)} Z`;
      s+=`<path d="${area}" fill="${sr.color}" opacity=".10"/>`;
    }
    let path='';
    pts.forEach((p,i)=>{ path+=(i?' L ':'M ')+p[0].toFixed(1)+' '+p[1].toFixed(1); });
    // Wide transparent hit-area so hovering anywhere on the line shows the series name
    s+=`<path d="${path}" fill="none" stroke="transparent" stroke-width="12"><title>${sr.name}</title></path>`;
    s+=`<path d="${path}" fill="none" stroke="${sr.color}" stroke-width="2.2" stroke-linejoin="round" pointer-events="none"/>`;
    pts.forEach(p=>{
      if(p[2]>0) s+=`<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="3" fill="${sr.color}"><title>${sr.name} · ${MONTH_LABELS[p[3].m-1]}/${String(p[3].y).slice(2)}: ${fmtFull(p[2])}</title></circle>`;
    });
  });
  // Per-month target line (staircase — holds each value until it changes)
  if(timeline.length){
    let tPath='', prevTy=null;
    timeline.forEach((t,i)=>{
      const tv=getTargetDisplay(t.y,t.m);
      const ty=PT+CH*(1-tv/maxVal);
      const tx=PL+i*dx;
      if(i===0){
        tPath='M '+tx.toFixed(1)+' '+ty.toFixed(1);
      } else {
        // step: horizontal at old level, then vertical to new level
        tPath+=' L '+tx.toFixed(1)+' '+prevTy.toFixed(1);
        tPath+=' L '+tx.toFixed(1)+' '+ty.toFixed(1);
      }
      prevTy=ty;
    });
    // extend last value to right edge
    tPath+=' L '+(W-PR)+' '+prevTy.toFixed(1);
    s+=`<path d="${tPath}" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="6,3" pointer-events="none"/>`;
    // label at right edge
    s+=`<text x="${W-PR+4}" y="${(prevTy+4).toFixed(1)}" font-size="10" fill="#ef4444" font-weight="600">Target</text>`;
  }
  // X labels — sparser if too many ticks
  const tickEvery = n<=12 ? 1 : n<=24 ? 2 : n<=36 ? 3 : Math.ceil(n/12);
  timeline.forEach((t,i)=>{
    if(i%tickEvery===0 || i===n-1){
      const x=PL+i*dx;
      s+=`<text x="${x.toFixed(1)}" y="${H-26}" text-anchor="middle" font-size="10" fill="#6b7280">${MONTH_LABELS[t.m-1]}</text>`;
      s+=`<text x="${x.toFixed(1)}" y="${H-12}" text-anchor="middle" font-size="10" fill="#9ca3af">'${String(t.y).slice(2)}</text>`;
    }
  });
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#cbd5e1"/>`;
  // Legend
  if(series.length>1){
    let lx=PL;
    series.forEach(sr=>{
      s+=`<rect x="${lx}" y="2" width="10" height="3" fill="${sr.color}" rx="1"/>`;
      s+=`<text x="${lx+14}" y="7" font-size="11" fill="#374151">${sr.name}</text>`;
      lx+=Math.min(sr.name.length*7+24, 140);
    });
  }
  s+='</svg>';
  return s;
}

// Build "byKey" map from a row filter function
function byKeyMap(rowFilter){
  const m={};
  VENTAS.filter(rowFilter).forEach(r=>{
    if(!selYears.has(r.a)||!inMonth(r)) return;
    const k=r.a+'-'+r.m;
    m[k]=(m[k]||0)+toAmount(r);
  });
  return m;
}

// ---- Seasonality chart: one line per year, X = Ene-Dic ----
// Useful when 2+ years are selected to spot seasonality patterns.
function chartSeasonalityByYear(rowFilter, opts={}){
  const target = opts.target || null;
  const years = [...selYears].sort();
  const months = [...selMonths].sort((a,b)=>a-b);
  if(!years.length || !months.length) return '<p style="color:#9ca3af;padding:24px">Sin datos para el filtro</p>';

  // Aggregate per year per month
  const yearData = {};
  years.forEach(y => { yearData[y] = new Array(12).fill(0); });
  VENTAS.filter(rowFilter).forEach(r => {
    if(!selYears.has(r.a) || !inMonth(r)) return;
    yearData[r.a][r.m-1] += toAmount(r);
  });

  const W=920, H=320, PL=68, PR=70, PT=20, PB=48;
  const CW=W-PL-PR, CH=H-PT-PB;

  let maxVal = 0;
  years.forEach(y => months.forEach(m => {
    const v = yearData[y][m-1]; if(v>maxVal) maxVal = v;
  }));
  if(target && target>maxVal) maxVal = target;
  maxVal = maxVal*1.12 || 1;

  const n = months.length;
  const dx = n>1 ? CW/(n-1) : 0;

  let s = svg(W, H);
  // Grid + Y labels
  for(let i=0; i<=5; i++){
    const y = PT+CH*(1-i/5), v = maxVal*i/5;
    s += `<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s += `<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${fmtK(v)}</text>`;
  }

  // One line per year
  years.forEach((yr, yi) => {
    const col = YEAR_COLORS[yr] || '#6b7280';
    const isCurrent = yr === Math.max(...years);
    const pts = months.map((m, i) => {
      const v = yearData[yr][m-1];
      return [PL+i*dx, PT+CH*(1-v/maxVal), v, m];
    });
    let path = '';
    pts.forEach((p, i) => { path += (i?' L ':'M ') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); });
    const sw = isCurrent ? 2.6 : 2;
    // Wide transparent hit-area so hovering anywhere on the line shows the year
    s += `<path d="${path}" fill="none" stroke="transparent" stroke-width="12"><title>${yr}</title></path>`;
    s += `<path d="${path}" fill="none" stroke="${col}" stroke-width="${sw}" stroke-linejoin="round" opacity="${isCurrent?1:.85}" pointer-events="none"/>`;
    pts.forEach(p => {
      if(p[2] > 0) s += `<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="${isCurrent?3.5:2.8}" fill="${col}"><title>${yr} · ${MONTH_LABELS[p[3]-1]}: ${fmtFull(p[2])}</title></circle>`;
    });
    // Year label at the right end (only the last point with data)
    let lastIdx = -1;
    for(let i=pts.length-1; i>=0; i--){ if(pts[i][2]>0){lastIdx=i;break;} }
    if(lastIdx>=0){
      const lp = pts[lastIdx];
      s += `<text x="${(lp[0]+8).toFixed(1)}" y="${(lp[1]+4).toFixed(1)}" font-size="11" fill="${col}" font-weight="700">${yr}${PARTIAL_YEARS.has(yr)?'*':''}</text>`;
    }
  });

  // Target line
  if(target){
    const ty = PT+CH*(1-target/maxVal);
    s += `<line x1="${PL}" y1="${ty.toFixed(1)}" x2="${W-PR}" y2="${ty.toFixed(1)}" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="6,3"/>`;
    s += `<text x="${PL+4}" y="${(ty-4).toFixed(1)}" font-size="10" fill="#dc2626" font-weight="600">Target ${fmtK(target)}</text>`;
  }

  // X labels (months)
  months.forEach((m, i) => {
    const x = PL + i*dx;
    s += `<text x="${x.toFixed(1)}" y="${H-22}" text-anchor="middle" font-size="11" fill="#374151" font-weight="500">${MONTH_LABELS[m-1]}</text>`;
  });
  s += `<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#cbd5e1"/>`;

  // Legend (years with their colors)
  let lx = PL;
  years.forEach(yr => {
    const col = YEAR_COLORS[yr] || '#6b7280';
    s += `<rect x="${lx}" y="${H-12}" width="10" height="3" fill="${col}" rx="1"/>`;
    s += `<text x="${lx+14}" y="${H-7}" font-size="11" fill="#4b5563">${yr}${PARTIAL_YEARS.has(yr)?'*':''}</text>`;
    lx += 60;
  });

  s += '</svg>';
  return s;
}

function chartGroupedBars(monthly, opts={}){
  const W=820,H=300,PL=70,PR=30,PT=20,PB=42;
  const CW=W-PL-PR, CH=H-PT-PB;
  const years=Object.keys(monthly).map(Number).sort();
  const allVals=years.flatMap(y=>monthly[y]||[]);
  const latestY=years[years.length-1];
  const maxVal=Math.max(...allVals, ...Array.from({length:12},(_,i)=>getTargetDisplay(latestY,i+1)))*1.1||1;
  const nY=years.length;
  const groupW=CW/12;
  const barW=Math.min(groupW*0.78/nY, 30);
  const barGap=(groupW-barW*nY)*0.5;
  let s=svg(W,H);
  for(let i=0;i<=5;i++){
    const y=PT+CH*(1-i/5), v=maxVal*i/5;
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3" stroke-width="1"/>`;
    s+=`<text x="${PL-8}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="11" fill="#9ca3af">${fmtK(v)}</text>`;
  }
  years.forEach((yr,yi)=>{
    const vals=monthly[yr]||new Array(12).fill(0);
    vals.forEach((v,mi)=>{
      if(!v) return;
      const bh=(v/maxVal)*CH;
      const x=PL+mi*groupW+barGap+yi*barW;
      const y=PT+CH-bh;
      s+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${bh.toFixed(1)}" fill="${YEAR_COLORS[yr]||'#2563eb'}" rx="3"><title>${yr} ${MONTHS_FULL[mi]}: ${fmtFull(v)}</title></rect>`;
    });
  });
  // Per-month staircase target line
  let tPath2='', prevTy2=null;
  for(let mi=0;mi<12;mi++){
    const tgt=getTargetDisplay(latestY,mi+1);
    const ty=PT+CH*(1-tgt/maxVal);
    const cx=PL+mi*groupW+groupW/2;
    if(mi===0){ tPath2='M '+PL.toFixed(1)+' '+ty.toFixed(1); }
    else { tPath2+=' L '+cx.toFixed(1)+' '+prevTy2.toFixed(1)+' L '+cx.toFixed(1)+' '+ty.toFixed(1); }
    prevTy2=ty;
  }
  if(prevTy2!==null){
    tPath2+=' L '+(W-PR).toFixed(1)+' '+prevTy2.toFixed(1);
    s+=`<path d="${tPath2}" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="6,3" pointer-events="none"/>`;
    s+=`<text x="${W-PR+4}" y="${(prevTy2+4).toFixed(1)}" font-size="11" fill="#ef4444" font-weight="600">Target</text>`;
  }
  MONTHS.forEach((m,i)=>{
    const x=PL+i*groupW+groupW/2;
    s+=`<text x="${x.toFixed(1)}" y="${H-6}" text-anchor="middle" font-size="11" fill="#6b7280">${m}</text>`;
  });
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

function chartAnnualBars(data){
  const W=520,H=270,PL=60,PR=20,PT=20,PB=35;
  const CW=W-PL-PR, CH=H-PT-PB;
  const years=ALL_YEARS;
  const vals=years.map(y=>data[y]||0);
  const maxVal=Math.max(...vals)*1.1||1;
  const barStep=CW/years.length;
  const barW=barStep*0.62;
  let s=svg(W,H);
  for(let i=0;i<=4;i++){
    const y=PT+CH*(1-i/4);
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${fmtK(maxVal*i/4)}</text>`;
  }
  years.forEach((yr,i)=>{
    const v=data[yr]||0;
    const bh=(v/maxVal)*CH;
    const x=PL+i*barStep+(barStep-barW)/2;
    const y=PT+CH-bh;
    const col=YEAR_COLORS[yr]||'#2563eb';
    s+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${bh.toFixed(1)}" fill="${col}" rx="4"><title>${yr}: ${fmtFull(v)}</title></rect>`;
    s+=`<text x="${(x+barW/2).toFixed(1)}" y="${H-8}" text-anchor="middle" font-size="11" fill="#4b5563" font-weight="500">${yr}${PARTIAL_YEARS.has(yr)?'*':''}</text>`;
    if(v>0) s+=`<text x="${(x+barW/2).toFixed(1)}" y="${Math.max(y-5,PT+12)}" text-anchor="middle" font-size="11" fill="#111827" font-weight="600">${fmtK(v)}</text>`;
  });
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

function chartHBars(entries, opts={}){
  const max=opts.max||10;
  const data=entries.slice(0,max);
  if(!data.length) return '<p style="color:#9ca3af;padding:20px">Sin datos</p>';
  const maxVal=data[0][1]||1;
  const ROW=34, W=560, PL=(opts.labelW||160), PR=80, PT=8;
  const H=PT+data.length*ROW+10;
  let s=svg(W,H);
  data.forEach(([label,val],i)=>{
    const y=PT+i*ROW;
    const bw=Math.max(3,(val/maxVal)*(W-PL-PR));
    const col=opts.color||'#2563eb';
    const dispLabel=(opts.labels&&opts.labels[label])||label;
    const short=dispLabel.length>22?dispLabel.substring(0,21)+'…':dispLabel;
    s+=`<text x="${PL-8}" y="${y+ROW/2+4}" text-anchor="end" font-size="12" fill="#374151">${short}</text>`;
    s+=`<rect x="${PL}" y="${y+5}" width="${bw.toFixed(1)}" height="${ROW-10}" fill="${col}" rx="4"><title>${dispLabel}: ${fmtFull(val)}</title></rect>`;
    s+=`<text x="${PL+bw+6}" y="${y+ROW/2+4}" font-size="12" fill="#1f2937" font-weight="600">${fmtK(val)}</text>`;
  });
  s+='</svg>';
  return s;
}

function chartParetoLine(entries){
  // Cumulative line chart
  const W=520, H=260, PL=50, PR=20, PT=20, PB=30;
  const CW=W-PL-PR, CH=H-PT-PB;
  const total=entries.reduce((a,b)=>a+b[1],0);
  const cum=[];
  let acc=0;
  entries.forEach(([k,v])=>{ acc+=v; cum.push(acc/total*100); });
  let s=svg(W,H);
  for(let i=0;i<=4;i++){
    const y=PT+CH*(1-i/4);
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${(i*25)}%</text>`;
  }
  // 80% reference line
  const ref80=PT+CH*(1-0.8);
  s+=`<line x1="${PL}" y1="${ref80.toFixed(1)}" x2="${W-PR}" y2="${ref80.toFixed(1)}" stroke="#ef4444" stroke-width="1" stroke-dasharray="4,3"/>`;
  s+=`<text x="${W-PR+2}" y="${(ref80+4).toFixed(1)}" font-size="10" fill="#ef4444">80%</text>`;
  // Line
  const pts=cum.map((p,i)=>{
    const x=PL+(i/(cum.length-1||1))*CW;
    const y=PT+CH*(1-p/100);
    return [x,y];
  });
  let path='';
  pts.forEach((p,i)=>{ path+=(i?' L ':'M ')+p[0].toFixed(1)+' '+p[1].toFixed(1); });
  s+=`<path d="${path}" fill="none" stroke="#2563eb" stroke-width="2.5"/>`;
  // Find 80% point
  const idx80=cum.findIndex(p=>p>=80);
  if(idx80>=0){
    const p=pts[idx80];
    s+=`<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="5" fill="#ef4444"/>`;
    s+=`<text x="${(p[0]+8).toFixed(1)}" y="${(p[1]-6).toFixed(1)}" font-size="11" fill="#1f2937" font-weight="600">${idx80+1} clientes = 80%</text>`;
  }
  // X label
  s+=`<text x="${PL+CW/2}" y="${H-6}" text-anchor="middle" font-size="11" fill="#6b7280">N° de clientes (ordenados por facturación)</text>`;
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

function chartGap(){
  // Show last 6 months vs target
  const W=820, H=280, PL=70, PR=30, PT=20, PB=40;
  const CW=W-PL-PR, CH=H-PT-PB;
  // Get last 12 months of data
  const allMonths=[];
  ALL_YEARS.forEach(y=>{
    const ms=monthlyForYear(y);
    ms.forEach((v,i)=>{ if(v>0||(y<CURRENT_YEAR)) allMonths.push({y,m:i+1,v}); });
  });
  // Trim to last 18 months
  const last=allMonths.slice(-18);
  const maxVal=Math.max(...last.map(x=>x.v), ...last.map(x=>getTargetDisplay(x.y,x.m)))*1.15;
  const barStep=CW/last.length;
  const barW=barStep*0.7;
  let s=svg(W,H);
  for(let i=0;i<=5;i++){
    const y=PT+CH*(1-i/5);
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${fmtK(maxVal*i/5)}</text>`;
  }
  last.forEach((d,i)=>{
    const tgt=getTargetDisplay(d.y,d.m);
    const bh=(d.v/maxVal)*CH;
    const x=PL+i*barStep+(barStep-barW)/2;
    const y=PT+CH-bh;
    const col=d.v>=tgt?'#10b981':'#f59e0b';
    s+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${bh.toFixed(1)}" fill="${col}" rx="3" opacity=".85"><title>${MONTHS_FULL[d.m-1]} ${d.y}: ${fmtFull(d.v)} · target ${fmtFull(tgt)}</title></rect>`;
    if(i%2===0||last.length<=12){
      s+=`<text x="${(x+barW/2).toFixed(1)}" y="${H-8}" text-anchor="middle" font-size="10" fill="#6b7280">${MONTHS[d.m-1]}'${String(d.y).slice(2)}</text>`;
    }
  });
  // Staircase target line per month
  let tPath='', prevTy=null;
  last.forEach((d,i)=>{
    const tgt=getTargetDisplay(d.y,d.m);
    const ty=PT+CH*(1-tgt/maxVal);
    const cx=PL+i*barStep+barStep/2;
    if(i===0){ tPath='M '+(PL).toFixed(1)+' '+ty.toFixed(1); }
    else { tPath+=' L '+cx.toFixed(1)+' '+prevTy.toFixed(1)+' L '+cx.toFixed(1)+' '+ty.toFixed(1); }
    prevTy=ty;
  });
  if(prevTy!==null){
    tPath+=' L '+(W-PR).toFixed(1)+' '+prevTy.toFixed(1);
    s+=`<path d="${tPath}" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="6,3" pointer-events="none"/>`;
    const lastTgt=getTargetDisplay(last[last.length-1].y,last[last.length-1].m);
    s+=`<text x="${W-PR+4}" y="${(prevTy+4).toFixed(1)}" font-size="11" fill="#ef4444" font-weight="600">${fmtK(lastTgt)}</text>`;
  }
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

function chartSeasonality(){
  // Average per month across all complete years
  const W=520, H=260, PL=50, PR=20, PT=20, PB=35;
  const CW=W-PL-PR, CH=H-PT-PB;
  const seas=new Array(12).fill(0);
  const cnt=new Array(12).fill(0);
  ALL_YEARS.filter(y=>!PARTIAL_YEARS.has(y)).forEach(y=>{
    const ms=monthlyForYear(y);
    ms.forEach((v,i)=>{ if(v>0){seas[i]+=v;cnt[i]++;} });
  });
  const avg=seas.map((v,i)=>cnt[i]?v/cnt[i]:0);
  const maxVal=Math.max(...avg, TARGET)*1.1;
  const barStep=CW/12;
  const barW=barStep*0.7;
  let s=svg(W,H);
  for(let i=0;i<=4;i++){
    const y=PT+CH*(1-i/4);
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${fmtK(maxVal*i/4)}</text>`;
  }
  avg.forEach((v,i)=>{
    const bh=(v/maxVal)*CH;
    const x=PL+i*barStep+(barStep-barW)/2;
    const y=PT+CH-bh;
    s+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${bh.toFixed(1)}" fill="#60a5fa" rx="3"><title>${MONTHS_FULL[i]}: prom ${fmtFull(v)}</title></rect>`;
    s+=`<text x="${(x+barW/2).toFixed(1)}" y="${H-8}" text-anchor="middle" font-size="10" fill="#6b7280">${MONTHS[i]}</text>`;
  });
  const ty=PT+CH*(1-TARGET/maxVal);
  s+=`<line x1="${PL}" y1="${ty.toFixed(1)}" x2="${W-PR}" y2="${ty.toFixed(1)}" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="5,3"/>`;
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

// ---- KPI rendering (Resumen) ----
function renderKPIs(){
  const years=[...selYears].sort();
  let total=0, monthCount=0, bestMVal=0, bestMLab='', bestY=0, bestYVal=0;
  years.forEach(y=>{
    const ms=monthlyForYear(y);
    const yTot=ms.reduce((a,b)=>a+b,0);
    if(yTot>bestYVal){bestYVal=yTot;bestY=y;}
    ms.forEach((v,i)=>{
      if(v>0 && !isPartialMonth(y,i)){total+=v;monthCount++;}
      if(v>bestMVal){bestMVal=v;bestMLab=MONTHS[i]+' '+y;}
    });
  });
  const avg=monthCount>0?total/monthCount:0;
  const yrLabel=years.length===1?years[0]+(PARTIAL_YEARS.has(years[0])?'*':''):(years[0]+'–'+years[years.length-1]);

  // Detect whether the current partial month was excluded from the avg
  let partialExcluded = false;
  years.forEach(y=>{
    const ms=monthlyForYear(y);
    ms.forEach((v,i)=>{ if(v>0 && isPartialMonth(y,i)) partialExcluded=true; });
  });
  const avgStrong = monthCount+(monthCount===1?' mes':' meses')+(partialExcluded?' · excl. '+MONTHS[TODAY_MONTH-1]:'');

  const kpis=[
    {lbl:'TOTAL PERÍODO', val:fmtK(total), sub:yrLabel, strong:monthCount+' meses con datos'},
    {lbl:'MEJOR AÑO', val:String(bestY||'–'), sub:'', strong:fmtK(bestYVal)+' '+currency},
    {lbl:'MEJOR MES', val:bestMLab||'–', sub:'', strong:fmtK(bestMVal)+' '+currency},
    {lbl:'PROM. MENSUAL', val:fmtK(avg), sub:currency+'/mes en el período', strong:avgStrong},
    {lbl:'OBJETIVO '+MONTHS[TODAY_MONTH-1]+' '+TODAY_YEAR, val:fmtK(getTargetDisplay(TODAY_YEAR,TODAY_MONTH)), sub:'Target del mes en curso', strong:fmtK(getTargetUSD(TODAY_YEAR,TODAY_MONTH)*12)+' USD anual (×12)'},
  ];

  document.getElementById('kpis').innerHTML = kpis.map(k=>`
    <div class="kpi">
      <div class="kpi-label">${k.lbl}</div>
      <div class="kpi-value">${k.val}</div>
      ${k.sub?`<div class="kpi-sub">${k.sub}</div>`:''}
      ${k.strong?`<div class="kpi-strong">${k.strong}</div>`:''}
    </div>`).join('');
}

function renderAnnualChart(){
  const data={};
  ALL_YEARS.forEach(y=>{ data[y]=totalForYear(y); });
  document.getElementById('chart-annual').innerHTML = chartAnnualBars(data);
}

function renderTopVendResumen(){
  const yrs=selYears;
  const vt=vendorTotals(yrs);
  const entries=Object.entries(vt).sort((a,b)=>b[1]-a[1]).slice(0,5);
  document.getElementById('top-vend-sub').textContent=[...yrs].sort().join(', ');
  document.getElementById('chart-top-vend').innerHTML = chartHBars(entries, {max:5, labelW:150, labels:VEND_LABELS, color:'#10b981'});
}

function renderAnnualTable(){
  let html='<table><thead><tr><th>Año</th><th>Total USD</th><th>Prom/mes</th><th>Mejor mes</th><th>vs Target</th><th>YoY</th></tr></thead><tbody>';
  let prev=null;
  ALL_YEARS.forEach(y=>{
    const ms=monthlyForYear(y);
    const tot=ms.reduce((a,b)=>a+b,0);
    let filteredTot=0, monthsWith=0;
    ms.forEach((v,mi)=>{ if(v>0 && !isPartialMonth(y,mi)){filteredTot+=v; monthsWith++;} });
    const avg=monthsWith?filteredTot/monthsWith:0;
    const best=Math.max(...ms);
    const bestIdx=ms.indexOf(best);
    const vsT=pct(avg,TARGET);
    let yoy='–';
    if(prev!==null && prev>0){
      const ch=(tot/prev-1)*100;
      const cls=ch>=0?'status-good':'status-bad';
      yoy=`<span class="status ${cls}">${ch>=0?'+':''}${ch.toFixed(0)}%</span>`;
    }
    const stCls=vsT>=100?'status-good':vsT>=70?'status-warn':'status-bad';
    html+=`<tr><td>${y}${PARTIAL_YEARS.has(y)?'*':''}</td><td>${fmtFull(tot)}</td><td>${fmtK(avg)}</td><td>${best>0?MONTHS[bestIdx]+' ('+fmtK(best)+')':'–'}</td><td><span class="status ${stCls}">${vsT}%</span></td><td>${yoy}</td></tr>`;
    prev=tot;
  });
  html+='</tbody></table>';
  document.getElementById('table-annual').innerHTML=html;
}

// ---- Mensual ----
function renderMonthly(){
  const yrs=[...selYears].sort();
  document.getElementById('monthly-sub').textContent=yrs.join(' vs ');
  const m={};
  yrs.forEach(y=>{ m[y]=monthlyForYear(y); });
  document.getElementById('chart-monthly').innerHTML=chartGroupedBars(m);
  const lastY=yrs[yrs.length-1];
  document.getElementById('monthly-legend').innerHTML=
    yrs.map(y=>`<div class="legend-item"><div class="legend-dot" style="background:${YEAR_COLORS[y]||'#2563eb'}"></div>${y}${PARTIAL_YEARS.has(y)?'*':''}</div>`).join('')+
    `<div class="legend-item"><svg width="22" height="3"><line x1="0" y1="1.5" x2="22" y2="1.5" stroke="#ef4444" stroke-width="2" stroke-dasharray="5,3"/></svg>&nbsp;Target por mes</div>`;

  let html='<table><thead><tr><th>Mes</th>'+yrs.map(y=>`<th>${y}${PARTIAL_YEARS.has(y)?'*':''}</th>`).join('')+'<th>Target</th><th>vs Target</th></tr></thead><tbody>';
  const totals=yrs.map(()=>0); let tgtSum=0;
  MONTHS.forEach((mn,i)=>{
    const tgt=getTargetDisplay(lastY,i+1);
    const vals=yrs.map((y,yi)=>{const v=m[y][i]||0;totals[yi]+=v;return v;});
    const last=vals[vals.length-1];
    const p=pct(last,tgt);
    const cls=p>=100?'status-good':p>=70?'status-warn':'status-bad';
    tgtSum+=tgt;
    html+=`<tr><td>${MONTHS_FULL[i]}</td>${vals.map(v=>`<td>${v>0?fmtK(v):'–'}</td>`).join('')}<td style="color:var(--muted)">${fmtK(tgt)}</td><td>${last>0?'<span class="status '+cls+'">'+p+'%</span>':'–'}</td></tr>`;
  });
  const lastTotal=totals[totals.length-1];
  html+=`<tr class="total"><td>TOTAL</td>${totals.map(t=>`<td>${fmtFull(t)}</td>`).join('')}<td style="color:var(--muted)">${fmtFull(tgtSum)}</td><td>${pct(lastTotal/12,tgtSum/12)}% prom</td></tr>`;
  html+='</tbody></table>';
  document.getElementById('table-monthly').innerHTML=html;
}

// ---- Vendedores ----
const ACTIVE_VENDORS = ['FACUNDO OROZA','FEDERICO CAFFARELLI','LUCAS LUNA','INX2 ILUMINACION SA'];
const VEND_PALETTE = {
  'FACUNDO OROZA':'#2563eb',
  'FEDERICO CAFFARELLI':'#10b981',
  'LUCAS LUNA':'#f59e0b',
  'INX2 ILUMINACION SA':'#8b5cf6',
  'ANIBAL CASOY':'#6b7280',
  'ARIEL FLORES':'#ec4899',
  'MARCOS GOMEZ':'#0891b2',
  'OSCAR NOGUERA':'#7c2d12',
  'SUELEM':'#9333ea',
  'PABLO DRAGHI':'#a16207',
  'GRISEL FERNANDEZ':'#1e40af'
};
const ALL_VENDORS_RANKED = (function(){
  const t={};
  VENTAS.forEach(r=>{ t[r.v]=(t[r.v]||0)+toUSD(r); });
  return Object.entries(t).sort((a,b)=>b[1]-a[1]).map(e=>e[0]);
})();

let selVendors = new Set(ACTIVE_VENDORS.filter(v=>ALL_VENDORS_RANKED.includes(v)));
let vendQuickFilter = 'activo'; // 'todos' or 'activo'

function totalForVendorYear(v,y){
  let t=0;
  VENTAS.filter(r=>r.a===y && r.v===v && inMonth(r)).forEach(r=>t+=toAmount(r));
  return t;
}

function renderVendStoryCards(){
  // Choose the latest fully-complete year (or current if no complete) as reference
  const refYear = ALL_YEARS.filter(y=>!PARTIAL_YEARS.has(y)).slice(-1)[0] || CURRENT_YEAR;
  const prevYear = refYear-1;
  const ytdYear = ALL_YEARS.slice(-1)[0]; // current year (partial)

  // 1) Top vendedor refYear
  const refTotals={};
  ALL_VENDORS_RANKED.forEach(v=>{ refTotals[v]=totalForVendorYear(v,refYear); });
  const topEntries = Object.entries(refTotals).sort((a,b)=>b[1]-a[1]);
  const [topVend, topVal] = topEntries[0] || ['',0];
  const topPrev = totalForVendorYear(topVend, prevYear);
  const topDelta = topPrev>0?((topVal/topPrev-1)*100):null;

  // 2) Mejor debut refYear: vendedor con mas ventas en refYear y sin ventas en años anteriores
  let bestDebut=null, bestDebutVal=0;
  ALL_VENDORS_RANKED.forEach(v=>{
    const prevTotal = ALL_YEARS.filter(y=>y<refYear).reduce((a,y)=>a+totalForVendorYear(v,y),0);
    if(prevTotal===0 && refTotals[v]>bestDebutVal){
      bestDebutVal=refTotals[v]; bestDebut=v;
    }
  });

  // 3) Vendedor en progresion: mejor % crecimiento YoY (ref vs prev) entre quienes ya tenian historia
  let progVend=null, progDelta=-Infinity, progVal=0, progPrev=0;
  ALL_VENDORS_RANKED.forEach(v=>{
    if(v===topVend||v===bestDebut) return;
    const cur=refTotals[v];
    const prev=totalForVendorYear(v,prevYear);
    if(prev>5000 && cur>5000){
      const d=(cur/prev-1)*100;
      if(d>progDelta){ progDelta=d; progVend=v; progVal=cur; progPrev=prev; }
    }
  });

  // 4) Cartera INX2 - always show
  const inxRef = totalForVendorYear('INX2 ILUMINACION SA', refYear);
  const inxYtd = totalForVendorYear('INX2 ILUMINACION SA', ytdYear);

  const cards = [];
  if(topVend){
    cards.push({
      cls:'',
      tag:'Top vendedor '+refYear,
      name: VEND_LABELS[topVend]||topVend,
      figure: fmtK(topVal)+' USD en '+refYear,
      note:'',
      delta: topDelta!==null ? {dir:topDelta>=0?'up':'down', text:(topDelta>=0?'↑ +':'↓ ')+Math.abs(topDelta).toFixed(0)+'% vs '+prevYear} : null
    });
  }
  if(bestDebut){
    cards.push({
      cls:'green',
      tag:'Mejor debut '+refYear,
      name: VEND_LABELS[bestDebut]||bestDebut,
      figure: fmtK(bestDebutVal)+' USD — primer año',
      note:'',
      delta: {dir:'new', text:'★ Debut en '+refYear}
    });
  }
  if(progVend){
    const ytd = totalForVendorYear(progVend, ytdYear);
    cards.push({
      cls:'amber',
      tag:VEND_LABELS[progVend]||progVend,
      name: fmtK(progVal)+(ytd>0?(' → '+fmtK(ytd)):''),
      figure: refYear+(ytd>0?(' → '+ytdYear+' YTD'):''),
      note:'Crecimiento sostenido',
      delta: {dir:progDelta>=0?'up':'down', text:(progDelta>=0?'↑ +':'↓ ')+Math.abs(progDelta).toFixed(0)+'% vs '+prevYear}
    });
  }
  cards.push({
    cls:'purple',
    tag:'Cartera Nacho (INX2)',
    name: fmtK(inxRef),
    figure: refYear+' · Ventas directas',
    note:'',
    delta: inxYtd>0 ? {dir:'up', text:fmtK(inxYtd)+' en lo que va de '+ytdYear} : null
  });

  document.getElementById('vend-story-cards').innerHTML = cards.map(c=>`
    <div class="story-card ${c.cls}">
      <span class="tag">${c.tag}</span>
      <div class="name">${c.name}</div>
      <div class="figure">${c.figure}</div>
      ${c.note?`<div class="note">${c.note}</div>`:''}
      ${c.delta?`<div class="delta ${c.delta.dir}">${c.delta.text}</div>`:''}
    </div>`).join('');

  document.getElementById('vend-story-sub').textContent = 'Datos hist&oacute;ricos · referencia '+refYear;
}

function renderVendPills(){
  const c=document.getElementById('vend-pills');
  c.innerHTML='';
  ALL_VENDORS_RANKED.forEach(v=>{
    const col=VEND_PALETTE[v]||'#6b7280';
    const b=document.createElement('button');
    b.className='vend-pill'+(selVendors.has(v)?' active':'');
    const lbl=VEND_LABELS[v]||v;
    const isCasoy=v==='ANIBAL CASOY';
    b.innerHTML=`<span class="dot" style="background:${selVendors.has(v)?col:'#cbd5e1'}"></span>${lbl}${isCasoy?' †':''}`;
    if(selVendors.has(v)){ b.style.borderColor=col; b.style.color=col; }
    b.onclick=()=>{
      if(selVendors.has(v)) selVendors.delete(v); else selVendors.add(v);
      renderVendChart();
      renderEvolVend();
      renderVendPills();
    };
    c.appendChild(b);
  });
}

function chartVendByYear(){
  const vendors = ALL_VENDORS_RANKED.filter(v=>selVendors.has(v));
  if(!vendors.length) return '<p style="color:#9ca3af;padding:24px">Seleccion&aacute; al menos un vendedor</p>';
  const W=900, H=340, PL=70, PR=30, PT=20, PB=42;
  const CW=W-PL-PR, CH=H-PT-PB;
  const years = ALL_YEARS;
  let maxVal=0;
  vendors.forEach(v=>{ years.forEach(y=>{ const t=totalForVendorYear(v,y); if(t>maxVal) maxVal=t; }); });
  maxVal=maxVal*1.12||1;
  const nV=vendors.length;
  const groupW=CW/years.length;
  const barW=Math.min(groupW*0.85/nV, 36);
  const barGap=(groupW-barW*nV)*0.5;
  let s=svg(W,H);
  for(let i=0;i<=5;i++){
    const y=PT+CH*(1-i/5), v=maxVal*i/5;
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-8}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="11" fill="#9ca3af">${fmtK(v)}</text>`;
  }
  vendors.forEach((vd,vi)=>{
    const col=VEND_PALETTE[vd]||'#6b7280';
    years.forEach((yr,yi)=>{
      const v=totalForVendorYear(vd,yr);
      if(!v) return;
      const bh=(v/maxVal)*CH;
      const x=PL+yi*groupW+barGap+vi*barW;
      const y=PT+CH-bh;
      s+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${bh.toFixed(1)}" fill="${col}" rx="3"><title>${VEND_LABELS[vd]||vd} ${yr}: ${fmtFull(v)}</title></rect>`;
    });
  });
  years.forEach((y,i)=>{
    const x=PL+i*groupW+groupW/2;
    s+=`<text x="${x.toFixed(1)}" y="${H-6}" text-anchor="middle" font-size="12" fill="#374151" font-weight="500">${y}${PARTIAL_YEARS.has(y)?'*':''}</text>`;
  });
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

function renderVendChart(){
  document.getElementById('chart-vend-byyear').innerHTML=chartVendByYear();
}

function trendCell(cur, prev, hadAnyBefore){
  if(!hadAnyBefore && cur>0) return '<span class="trend-new">Nuevo</span>';
  if(prev>0 && cur>0){
    const d=(cur/prev-1)*100;
    const cls=d>=0?'trend-up':'trend-down';
    return `<span class="${cls}">${d>=0?'↑':'↓'}${Math.abs(d).toFixed(0)}%</span>`;
  }
  if(prev>0 && !cur) return '<span class="trend-down">↓100%</span>';
  return '—';
}

function renderVendTable(){
  const refYear = ALL_YEARS.filter(y=>!PARTIAL_YEARS.has(y)).slice(-1)[0] || CURRENT_YEAR;
  const prevYear = refYear-1;
  // Show all but order by ref year total desc
  const totals={};
  ALL_VENDORS_RANKED.forEach(v=>{ totals[v]=totalForVendorYear(v,refYear); });
  const order = ALL_VENDORS_RANKED.slice().sort((a,b)=>(totals[b]||0)-(totals[a]||0));
  // Pick years to show: from 2022 onward to keep table compact
  const yearsShow = ALL_YEARS.filter(y=>y>=2022);
  let html='<table><thead><tr><th>Vendedor</th>'+yearsShow.map(y=>`<th>${y}${PARTIAL_YEARS.has(y)?'*':''}</th>`).join('')+`<th>Tend. ${String(prevYear).slice(2)}→${String(refYear).slice(2)}</th></tr></thead><tbody>`;
  order.forEach(v=>{
    const row=yearsShow.map(y=>totalForVendorYear(v,y));
    const sumBefore=ALL_YEARS.filter(y=>y<refYear).reduce((a,y)=>a+totalForVendorYear(v,y),0);
    const cur=totalForVendorYear(v,refYear);
    const prev=totalForVendorYear(v,prevYear);
    const hadBefore=ALL_YEARS.filter(y=>y<refYear).some(y=>totalForVendorYear(v,y)>0);
    const trend=trendCell(cur,prev,hadBefore);
    const lbl=(VEND_LABELS[v]||v)+(v==='ANIBAL CASOY'?' †':'');
    html+=`<tr><td>${lbl}</td>${row.map(t=>`<td>${t>0?fmtK(t):'—'}</td>`).join('')}<td>${trend}</td></tr>`;
  });
  html+='</tbody></table>';
  document.getElementById('table-vend').innerHTML=html;
}

function renderVendores(){
  renderVendStoryCards();
  renderVendPills();
  renderVendChart();
  renderVendTable();
}

// ---- Clientes & Productos ----
function renderClientes(){
  const yrs=selYears;
  const yrLabel=[...yrs].sort().join(', ');
  const ct=clientTotals(yrs);
  const entries=Object.entries(ct).sort((a,b)=>b[1]-a[1]);
  document.getElementById('cli-sub').textContent=yrLabel;
  document.getElementById('cli-table-sub').textContent=yrLabel;
  document.getElementById('prod-sub').textContent=yrLabel;
  document.getElementById('prod-table-sub').textContent=yrLabel;
  document.getElementById('chart-top-cli').innerHTML=chartHBars(entries, {max:15, labelW:180, color:'#8b5cf6'});

  // Pareto
  document.getElementById('chart-pareto').innerHTML=chartParetoLine(entries);
  const total=entries.reduce((a,b)=>a+b[1],0);
  let acc=0;
  let n80=entries.findIndex(([k,v])=>{ acc+=v; return acc/total>=0.8; })+1;
  document.getElementById('pareto-text').innerHTML=`
    <b>${n80} de ${entries.length}</b> clientes (${pct(n80,entries.length)}%) generan el <b>80% de la facturacion</b> del periodo.
    ${n80<entries.length*0.2?'Cartera muy concentrada - vale la pena diversificar.':''}
  `;

  // Top clients table
  let html='<table><thead><tr><th>#</th><th>Cliente</th><th>USD facturado</th><th>% del total</th><th>Acumulado</th></tr></thead><tbody>';
  let cum=0;
  entries.slice(0,30).forEach(([c,v],i)=>{
    cum+=v;
    html+=`<tr><td>${i+1}</td><td>${c}</td><td>${fmtFull(v)}</td><td>${(v/total*100).toFixed(1)}%</td><td>${(cum/total*100).toFixed(1)}%</td></tr>`;
  });
  html+='</tbody></table>';
  document.getElementById('table-cli').innerHTML=html;

  // Nacional vs Importado deep dive vive ahora en la pestaña "Origen".

  // Products
  const pt=productTotals(yrs);
  const pEntries=Object.entries(pt).sort((a,b)=>b[1]-a[1]);
  document.getElementById('chart-products').innerHTML=chartHBars(pEntries, {max:10, labelW:110, color:'#0ea5e9', labels:PROD_LABELS});

  // Product evolution chart - top 6 families
  const pBY=productByYearTotals();
  const topFams=pEntries.slice(0,6).map(e=>e[0]);
  document.getElementById('chart-prod-evol').innerHTML=chartProductEvolution(topFams, pBY);

  // Product table
  const totalProd=pEntries.reduce((a,b)=>a+b[1],0);
  let phtml='<table><thead><tr><th>Familia</th>'+ALL_YEARS.map(y=>`<th>${y}${PARTIAL_YEARS.has(y)?'*':''}</th>`).join('')+'<th>Total periodo</th><th>%</th></tr></thead><tbody>';
  pEntries.forEach(([fam,tot])=>{
    const row=ALL_YEARS.map(y=>(pBY[fam]&&pBY[fam][y])||0);
    const lbl=PROD_LABELS[fam]||fam;
    phtml+=`<tr><td><b>${lbl}</b></td>${row.map(t=>`<td>${t>0?fmtK(t):'-'}</td>`).join('')}<td><b>${fmtFull(tot)}</b></td><td>${(tot/totalProd*100).toFixed(1)}%</td></tr>`;
  });
  phtml+='</tbody></table>';
  document.getElementById('table-products').innerHTML=phtml;
}

// ---- Alertas comerciales ----
function renderAlertasComerciales(){
  renderAlertaNuevos();
  renderAlertaReactivacion();
  renderAlertaAusentes();
}

function renderAlertaNuevos(){
  const sel=document.getElementById('alerta-nuevos-sel');
  if(sel && !sel._init){
    sel._init=true;
    [...ALL_YEAR_MONTHS].reverse().forEach(({a,m})=>{
      const opt=document.createElement('option');
      opt.value=a*100+m;
      opt.textContent=MONTHS_FULL[m-1]+' '+a;
      sel.appendChild(opt);
    });
    sel.value=alertNuevosYM.a*100+alertNuevosYM.m;
    sel.addEventListener('change',()=>{
      const v=parseInt(sel.value);
      alertNuevosYM={a:Math.floor(v/100),m:v%100};
      renderAlertaNuevos();
    });
  }
  const {a,m}=alertNuevosYM;
  const newClients=Object.keys(CLIENT_META).filter(c=>CLIENT_META[c].first.a===a&&CLIENT_META[c].first.mo===m);
  const body=document.getElementById('alerta-nuevos-body');
  if(!newClients.length){
    body.innerHTML='<p style="color:var(--muted-2);font-size:12px;padding:6px 0">Sin clientes nuevos en este mes.</p>';
    return;
  }
  const newSet=new Set(newClients);
  const monthTotals={};
  VENTAS.filter(r=>r.a===a&&r.m===m&&newSet.has(r.c)).forEach(r=>{
    monthTotals[r.c]=(monthTotals[r.c]||0)+toAmount(r);
  });
  const rows=newClients.map(c=>[c,monthTotals[c]||0]).sort((a,b)=>b[1]-a[1]);
  let html='<table><thead><tr><th>#</th><th>Cliente</th><th>1.ª compra</th></tr></thead><tbody>';
  rows.forEach(([c,v],i)=>{
    html+=`<tr><td>${i+1}</td><td>${c}</td><td>${fmtFull(v)}</td></tr>`;
  });
  html+='</tbody></table>';
  body.innerHTML=html;
}

function renderAlertaReactivacion(){
  const input=document.getElementById('alerta-reactiv-n');
  if(input&&!input._init){
    input._init=true;
    input.addEventListener('change',()=>{
      alertReactivN=Math.max(6,parseInt(input.value)||24);
      input.value=alertReactivN;
      renderAlertaReactivacion();
    });
  }
  const threshold=alertReactivN;
  // Totals all-time per client
  const allTotals={};
  VENTAS.forEach(r=>{ allTotals[r.c]=(allTotals[r.c]||0)+toAmount(r); });
  const candidates=Object.entries(CLIENT_META)
    .filter(([c,cm])=>monthsSince(cm.last.a,cm.last.mo)>=threshold)
    .map(([c,cm])=>({c,lastA:cm.last.a,lastM:cm.last.mo,meses:monthsSince(cm.last.a,cm.last.mo),hist:allTotals[c]||0}))
    .sort((a,b)=>b.hist-a.hist)
    .slice(0,20);
  const countEl=document.getElementById('alerta-reactiv-count');
  if(countEl) countEl.textContent=candidates.length+' clientes';
  const body=document.getElementById('alerta-reactiv-body');
  if(!candidates.length){
    body.innerHTML='<p style="color:var(--muted-2);font-size:12px;padding:6px 0">Sin candidatos con ese umbral.</p>';
    return;
  }
  let html='<table><thead><tr><th>#</th><th>Cliente</th><th>&Uacute;ltima compra</th><th>Hist&oacute;rico</th></tr></thead><tbody>';
  candidates.forEach(({c,lastA,lastM,meses,hist},i)=>{
    html+=`<tr><td>${i+1}</td><td>${c}</td><td>${MONTHS[lastM-1]} ${lastA}&nbsp;<span class="status status-warn">${meses}m</span></td><td>${fmtFull(hist)}</td></tr>`;
  });
  html+='</tbody></table>';
  body.innerHTML=html;
}

function renderAlertaAusentes(){
  const input=document.getElementById('alerta-activos-n');
  if(input&&!input._init){
    input._init=true;
    input.addEventListener('change',()=>{
      alertActivosN=Math.max(1,Math.min(5,parseInt(input.value)||3));
      input.value=alertActivosN;
      renderAlertaAusentes();
    });
  }
  const n=alertActivosN;
  const rangeYears=Array.from({length:n},(_,i)=>CURRENT_YEAR-n+i); // [CURRENT_YEAR-N .. CURRENT_YEAR-1]
  const titleEl=document.getElementById('alerta-activos-title');
  if(titleEl) titleEl.textContent='Sin comprar en '+CURRENT_YEAR;
  const thisYearClients=new Set(VENTAS.filter(r=>r.a===CURRENT_YEAR).map(r=>r.c));
  // Totals in range years per client
  const rangeTotals={};
  VENTAS.filter(r=>rangeYears.includes(r.a)).forEach(r=>{
    rangeTotals[r.c]=(rangeTotals[r.c]||0)+toAmount(r);
  });
  const candidates=Object.entries(CLIENT_META)
    .filter(([c,cm])=>rangeYears.some(y=>cm.years.has(y))&&!thisYearClients.has(c))
    .map(([c,cm])=>({
      c,
      lastYear:Math.max(...[...cm.years].filter(y=>y<CURRENT_YEAR)),
      rangeTotal:rangeTotals[c]||0
    }))
    .sort((a,b)=>b.rangeTotal-a.rangeTotal)
    .slice(0,20);
  const countEl=document.getElementById('alerta-activos-count');
  if(countEl) countEl.textContent=candidates.length+' clientes';
  const body=document.getElementById('alerta-activos-body');
  if(!candidates.length){
    body.innerHTML=`<p style="color:var(--muted-2);font-size:12px;padding:6px 0">Todos los activos en esos a&ntilde;os ya compraron en ${CURRENT_YEAR}.</p>`;
    return;
  }
  const yr0=rangeYears[0], yr1=rangeYears[rangeYears.length-1];
  let html=`<table><thead><tr><th>#</th><th>Cliente</th><th>&Uacute;lt. a&ntilde;o</th><th>${yr0===yr1?yr0:yr0+'&ndash;'+yr1}</th></tr></thead><tbody>`;
  candidates.forEach(({c,lastYear,rangeTotal},i)=>{
    html+=`<tr><td>${i+1}</td><td>${c}</td><td>${lastYear}</td><td>${fmtFull(rangeTotal)}</td></tr>`;
  });
  html+='</tbody></table>';
  body.innerHTML=html;
}

// ---- Nacional vs Importado ----
function origenByYear(){
  // {year: {nacional, importado, otros}} — respects month filter
  const res={};
  ALL_YEARS.forEach(y=>{ res[y]={nacional:0,importado:0,otros:0}; });
  VENTAS.filter(r=>inMonth(r)).forEach(r=>{
    const o=origenOf(r.p||'');
    res[r.a][o]+=toAmount(r);
  });
  return res;
}

// Vieja renderOrigen (la del panel C&P) eliminada: el deep dive vive en la pestaña Origen.

// ---- Diario tab ----
function dailyAggregation(){
  // Returns array of {y,m,d, totalARS, totalUSD, facturas} sorted chronologically, respecting filters
  const map={}; // key = 'y-m-d' -> {y,m,d,totalARS,totalUSD,facSet}
  VENTAS.filter(r=>selYears.has(r.a)&&inMonth(r)).forEach(r=>{
    const k=r.a+'-'+r.m+'-'+r.d;
    if(!map[k]) map[k]={y:r.a,m:r.m,d:r.d,totalARS:0,totalUSD:0,facs:new Set()};
    map[k].totalARS+=r.t;
    map[k].totalUSD+=toUSD(r);
    map[k].facs.add(r.tv+'-'+r.f); // unique facturas (combine tipo+num)
  });
  const arr=Object.values(map).map(o=>({y:o.y,m:o.m,d:o.d,totalARS:o.totalARS,totalUSD:o.totalUSD,facturas:o.facs.size}));
  arr.sort((a,b)=> (b.y-a.y) || (b.m-a.m) || (b.d-a.d));
  return arr;
}

function renderDiarioKPIs(daily){
  const yrLabel=[...selYears].sort().join(', ');
  const moLabel=selMonths.size===12?'todos los meses':[...selMonths].sort((a,b)=>a-b).map(m=>MONTHS[m-1]).join(', ');
  document.getElementById('diario-sub').textContent=yrLabel+' · '+moLabel;
  let total=0, days=0, bestVal=0, bestDay='', totalFacs=0;
  daily.forEach(d=>{
    const val=currency==='USD'?d.totalUSD:d.totalARS;
    total+=val;
    if(val!==0) days++;
    totalFacs+=d.facturas;
    if(val>bestVal){ bestVal=val; bestDay=String(d.d).padStart(2,'0')+'/'+String(d.m).padStart(2,'0')+'/'+String(d.y).slice(2); }
  });
  const avg = days>0 ? total/days : 0;
  const kpis=[
    {lbl:'TOTAL PER&Iacute;ODO', val:fmtK(total), sub:fmtFull(total), col:'#2563eb'},
    {lbl:'D&Iacute;AS CON VENTAS', val:String(days), sub:totalFacs+' facturas totales', col:'#0891b2'},
    {lbl:'PROMEDIO DIARIO', val:fmtK(avg), sub:'sobre d&iacute;as con ventas', col:'#10b981'},
    {lbl:'MEJOR D&Iacute;A', val:bestDay||'—', sub:fmtK(bestVal), col:'#f59e0b'},
  ];
  document.getElementById('diario-kpis').innerHTML=kpis.map(k=>`
    <div style="background:#fff;border-radius:10px;padding:18px 20px;box-shadow:0 1px 3px rgba(0,0,0,.04);border:1px solid #eef0f3;border-left:4px solid ${k.col}">
      <div style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.7px;margin-bottom:6px">${k.lbl}</div>
      <div style="font-size:22px;font-weight:700;color:${k.col};line-height:1.1">${k.val}</div>
      <div style="font-size:11px;color:#6b7280;margin-top:6px">${k.sub}</div>
    </div>`).join('');
}

function chartDiarioBars(daily){
  if(!daily.length) return '<p style="color:#9ca3af;padding:30px;text-align:center">Sin ventas en el per&iacute;odo seleccionado</p>';
  const W=Math.max(900, Math.min(daily.length*22, 2200));
  const H=320, PL=70, PR=20, PT=20, PB=58;
  const CW=W-PL-PR, CH=H-PT-PB;
  const getDailyVal=d=>currency==='USD'?d.totalUSD:d.totalARS;
  let maxVal=Math.max(...daily.map(getDailyVal));
  let minVal=Math.min(0,...daily.map(getDailyVal));
  const range = maxVal - minVal || 1;
  const padding = range*0.1;
  const yMax = maxVal + padding;
  const yMin = minVal - (minVal<0?padding:0);
  const yRange = yMax - yMin || 1;
  const yToCoord=(v)=>PT+CH*(1-(v-yMin)/yRange);
  const zeroY = yToCoord(0);
  const barW = Math.min(CW/daily.length*0.85, 22);
  const step = CW/daily.length;

  let s=svg(W,H);
  // Grid + Y axis labels
  for(let i=0;i<=5;i++){
    const t=i/5;
    const v=yMin+yRange*t;
    const y=yToCoord(v);
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${fmtK(v)}</text>`;
  }
  // Zero line
  s+=`<line x1="${PL}" y1="${zeroY.toFixed(1)}" x2="${W-PR}" y2="${zeroY.toFixed(1)}" stroke="#9ca3af" stroke-width="1"/>`;

  // Month separators
  let prevYM=null;
  daily.forEach((d,i)=>{
    const ym=d.y*100+d.m;
    if(prevYM!==null && ym!==prevYM){
      const x=PL+i*step;
      s+=`<line x1="${x.toFixed(1)}" y1="${PT}" x2="${x.toFixed(1)}" y2="${PT+CH}" stroke="#d1d5db" stroke-dasharray="3,3"/>`;
    }
    prevYM=ym;
  });

  // Bars
  daily.forEach((d,i)=>{
    const x=PL+i*step+(step-barW)/2;
    const dval=getDailyVal(d);
    const valY=yToCoord(dval);
    const barTop=Math.min(valY,zeroY);
    const barH=Math.abs(valY-zeroY);
    const col=dval>=0?'#2563eb':'#dc2626';
    s+=`<rect x="${x.toFixed(1)}" y="${barTop.toFixed(1)}" width="${barW.toFixed(1)}" height="${barH.toFixed(1)}" fill="${col}" rx="1.5" opacity=".88"><title>${String(d.d).padStart(2,'0')}/${String(d.m).padStart(2,'0')}/${d.y}: ${fmtFull(dval)} (${d.facturas} fact.)</title></rect>`;
  });

  // X axis labels - days (sparse)
  const tickEvery = daily.length<=15 ? 1 : daily.length<=40 ? 2 : daily.length<=80 ? 5 : 10;
  let prevMonth=null;
  daily.forEach((d,i)=>{
    const x=PL+i*step+step/2;
    const showDay = (i%tickEvery===0) || (i===daily.length-1) || (prevMonth!==null && d.m!==prevMonth);
    if(showDay){
      s+=`<text x="${x.toFixed(1)}" y="${(PT+CH+14).toFixed(1)}" text-anchor="middle" font-size="9" fill="#6b7280">${d.d}</text>`;
    }
    // Month label at the start of each month
    if(prevMonth===null || d.m!==prevMonth){
      s+=`<text x="${x.toFixed(1)}" y="${(PT+CH+30).toFixed(1)}" text-anchor="start" font-size="11" fill="#1f2937" font-weight="700">${MONTHS[d.m-1]} '${String(d.y).slice(2)}</text>`;
    }
    prevMonth=d.m;
  });
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#cbd5e1"/>`;
  s+=`<line x1="${PL}" y1="${PT}" x2="${PL}" y2="${PT+CH}" stroke="#cbd5e1"/>`;
  s+='</svg>';
  // Wrap in scroll container if wide
  return `<div style="overflow-x:auto;width:100%">${s}</div>`;
}

function renderDiarioTable(daily){
  document.getElementById('diario-tbl-sub').textContent=daily.length+' d&iacute;as';
  if(!daily.length){
    document.getElementById('table-diario').innerHTML='<p style="color:#9ca3af;padding:20px">Sin datos en el per&iacute;odo</p>';
    return;
  }
  // Group by month for visual breaks
  let html='<table><thead><tr><th>Fecha</th><th>D&iacute;a</th><th>Facturas</th><th style="text-align:right">ARS</th><th style="text-align:right">USD</th></tr></thead><tbody>';
  let curMonth=null, monthTotalARS=0, monthTotalUSD=0, monthDays=0;
  const flushMonth=()=>{
    if(curMonth!==null && monthDays>0){
      html+=`<tr style="background:#dbeafe;font-weight:700;color:#1e40af;font-size:13px"><td colspan="3" style="text-align:right">Total ${MONTHS[curMonth[1]-1]} '${String(curMonth[0]).slice(2)} (${monthDays} d&iacute;as)</td><td style="text-align:right">${fmtFull(monthTotalARS)}</td><td style="text-align:right">${fmtFull(monthTotalUSD)}</td></tr>`;
    }
  };
  const dayNames=['Dom','Lun','Mar','Mi&eacute;','Jue','Vie','S&aacute;b'];
  daily.forEach(d=>{
    const ym=[d.y,d.m];
    if(curMonth===null||curMonth[0]!==ym[0]||curMonth[1]!==ym[1]){
      flushMonth();
      curMonth=ym; monthTotalARS=0; monthTotalUSD=0; monthDays=0;
    }
    monthTotalARS+=d.totalARS; monthTotalUSD+=d.totalUSD; monthDays++;
    const date=new Date(d.y,d.m-1,d.d);
    const dn=dayNames[date.getDay()];
    const colARS=d.totalARS<0?'color:#dc2626':'';
    const colUSD=d.totalUSD<0?'color:#dc2626':'';
    html+=`<tr><td>${String(d.d).padStart(2,'0')}/${String(d.m).padStart(2,'0')}/${d.y}</td><td>${dn}</td><td>${d.facturas}</td><td style="text-align:right;${colARS}">${fmtFull(d.totalARS)}</td><td style="text-align:right;${colUSD}">${fmtFull(d.totalUSD)}</td></tr>`;
  });
  flushMonth();
  // Grand total
  const gtARS=daily.reduce((s,d)=>s+d.totalARS,0);
  const gtUSD=daily.reduce((s,d)=>s+d.totalUSD,0);
  html+=`<tr style="background:#1f2937;color:#fff;font-weight:700"><td colspan="3" style="text-align:right">TOTAL PER&Iacute;ODO</td><td style="text-align:right">${fmtFull(gtARS)}</td><td style="text-align:right">${fmtFull(gtUSD)}</td></tr>`;
  html+='</tbody></table>';
  document.getElementById('table-diario').innerHTML=html;
}

function renderDiario(){
  const daily=dailyAggregation();
  renderDiarioKPIs(daily);
  document.getElementById('chart-diario').innerHTML=chartDiarioBars(daily);
  document.getElementById('diario-chart-sub').textContent=daily.length+' d&iacute;as · barras rojas = NC neto del d&iacute;a';
  renderDiarioTable(daily);
}

function chartOrigenStacked(byYear){
  const W=520, H=280, PL=58, PR=20, PT=20, PB=35;
  const CW=W-PL-PR, CH=H-PT-PB;
  const years=ALL_YEARS;
  const maxVal=Math.max(...years.map(y=>byYear[y].nacional+byYear[y].importado))*1.1||1;
  const step=CW/years.length;
  const barW=step*0.62;
  let s=svg(W,H);
  for(let i=0;i<=4;i++){
    const y=PT+CH*(1-i/4);
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${fmtK(maxVal*i/4)}</text>`;
  }
  years.forEach((yr,i)=>{
    const d=byYear[yr];
    const x=PL+i*step+(step-barW)/2;
    const hNac=(d.nacional/maxVal)*CH;
    const hImp=(d.importado/maxVal)*CH;
    const yNac=PT+CH-hNac;
    const yImp=yNac-hImp;
    const tp=d.nacional+d.importado;
    const pNac=tp?Math.round(d.nacional/tp*100):0;
    const pImp=tp?Math.round(d.importado/tp*100):0;
    s+=`<rect x="${x.toFixed(1)}" y="${yNac.toFixed(1)}" width="${barW.toFixed(1)}" height="${hNac.toFixed(1)}" fill="#10b981" rx="2"><title>${yr} Nacional: ${fmtFull(d.nacional)} (${pNac}% del total)</title></rect>`;
    s+=`<rect x="${x.toFixed(1)}" y="${yImp.toFixed(1)}" width="${barW.toFixed(1)}" height="${hImp.toFixed(1)}" fill="#f59e0b" rx="2"><title>${yr} Importado: ${fmtFull(d.importado)} (${pImp}% del total)</title></rect>`;
    s+=`<text x="${(x+barW/2).toFixed(1)}" y="${H-8}" text-anchor="middle" font-size="10" fill="#6b7280">${yr}${PARTIAL_YEARS.has(yr)?'*':''}</text>`;
    if(d.nacional+d.importado>0){
      s+=`<text x="${(x+barW/2).toFixed(1)}" y="${(yImp-4).toFixed(1)}" text-anchor="middle" font-size="10" fill="#111827" font-weight="600">${fmtK(d.nacional+d.importado)}</text>`;
    }
  });
  // Legend
  s+=`<rect x="${PL}" y="2" width="10" height="10" fill="#10b981" rx="2"/><text x="${PL+14}" y="11" font-size="11" fill="#374151">Nacional</text>`;
  s+=`<rect x="${PL+85}" y="2" width="10" height="10" fill="#f59e0b" rx="2"/><text x="${PL+99}" y="11" font-size="11" fill="#374151">Importado</text>`;
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

function chartOrigenPct(byYear){
  const W=520, H=280, PL=45, PR=20, PT=20, PB=35;
  const CW=W-PL-PR, CH=H-PT-PB;
  const years=ALL_YEARS;
  let s=svg(W,H);
  for(let i=0;i<=4;i++){
    const y=PT+CH*(1-i/4);
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${i*25}%</text>`;
  }
  const pts=years.map((y,i)=>{
    const d=byYear[y];
    const tp=d.nacional+d.importado;
    const p=tp?d.importado/tp*100:0;
    const x=PL+(i/(years.length-1||1))*CW;
    const ny=PT+CH*(1-p/100);
    return [x,ny,p,y];
  });
  // Area under line
  let area=`M ${pts[0][0].toFixed(1)} ${(PT+CH).toFixed(1)}`;
  pts.forEach(p=>{ area+=` L ${p[0].toFixed(1)} ${p[1].toFixed(1)}`; });
  area+=` L ${pts[pts.length-1][0].toFixed(1)} ${(PT+CH).toFixed(1)} Z`;
  s+=`<path d="${area}" fill="#f59e0b" opacity=".15"/>`;
  // Line
  let path='';
  pts.forEach((p,i)=>{ path+=(i?' L ':'M ')+p[0].toFixed(1)+' '+p[1].toFixed(1); });
  s+=`<path d="${path}" fill="none" stroke="#f59e0b" stroke-width="2.5"/>`;
  // Points + labels
  pts.forEach(p=>{
    s+=`<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="4" fill="#f59e0b"><title>${p[3]}: ${p[2].toFixed(1)}% importado</title></circle>`;
    s+=`<text x="${p[0].toFixed(1)}" y="${(p[1]-9).toFixed(1)}" text-anchor="middle" font-size="11" fill="#92400e" font-weight="600">${p[2].toFixed(1)}%</text>`;
  });
  years.forEach((y,i)=>{
    const x=PL+(i/(years.length-1||1))*CW;
    s+=`<text x="${x.toFixed(1)}" y="${H-8}" text-anchor="middle" font-size="10" fill="#6b7280">${y}${PARTIAL_YEARS.has(y)?'*':''}</text>`;
  });
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

function chartProductEvolution(fams, pBY){
  const W=520, H=280, PL=55, PR=80, PT=20, PB=35;
  const CW=W-PL-PR, CH=H-PT-PB;
  const years=ALL_YEARS;
  const colors=['#2563eb','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4'];
  let maxVal=0;
  fams.forEach(f=>{ years.forEach(y=>{ const v=(pBY[f]&&pBY[f][y])||0; if(v>maxVal) maxVal=v; }); });
  maxVal*=1.1||1;
  let s=svg(W,H);
  for(let i=0;i<=4;i++){
    const y=PT+CH*(1-i/4);
    s+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="#f0f1f3"/>`;
    s+=`<text x="${PL-6}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="10" fill="#9ca3af">${fmtK(maxVal*i/4)}</text>`;
  }
  fams.forEach((fam,fi)=>{
    const col=colors[fi%colors.length];
    const pts=years.map((y,i)=>{
      const v=(pBY[fam]&&pBY[fam][y])||0;
      const x=PL+(i/(years.length-1||1))*CW;
      const ny=PT+CH*(1-v/maxVal);
      return [x,ny,v,y];
    });
    let path='';
    pts.forEach((p,i)=>{ path+=(i?' L ':'M ')+p[0].toFixed(1)+' '+p[1].toFixed(1); });
    s+=`<path d="${path}" fill="none" stroke="${col}" stroke-width="2.2"/>`;
    pts.forEach(p=>{
      s+=`<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="3.5" fill="${col}"><title>${fam} ${p[3]}: ${fmtFull(p[2])}</title></circle>`;
    });
    // Right side label
    const lastPt=pts[pts.length-1];
    const flbl=PROD_LABELS[fam]||fam;
    s+=`<text x="${(W-PR+5).toFixed(1)}" y="${(lastPt[1]+4).toFixed(1)}" font-size="11" fill="${col}" font-weight="600">${flbl}</text>`;
  });
  years.forEach((y,i)=>{
    const x=PL+(i/(years.length-1||1))*CW;
    s+=`<text x="${x.toFixed(1)}" y="${H-6}" text-anchor="middle" font-size="10" fill="#6b7280">${y}</text>`;
  });
  s+=`<line x1="${PL}" y1="${PT+CH}" x2="${W-PR}" y2="${PT+CH}" stroke="#e5e7eb"/>`;
  s+='</svg>';
  return s;
}

// ---- Target table ----
function renderTargetTable(){
  const lbl = document.getElementById('target-table-currency');
  if(lbl) lbl.textContent = 'Vista en '+currency;

  const cols = MONTHS; // ['Ene'..'Dic']
  const now = TODAY_YEAR*100+TODAY_MONTH;

  let html = '<table><thead><tr><th>Año</th>';
  cols.forEach((m,i) => { html+=`<th style="text-align:center">${m}</th>`; });
  html += '</tr></thead><tbody>';

  ALL_YEARS.forEach(y => {
    html += `<tr><td><b>${y}</b></td>`;
    for(let m=1; m<=12; m++){
      const isPast  = y*100+m < now;
      const isCur   = y*100+m === now;
      const isFut   = y*100+m > now;
      const hasData = !!VENTAS.find(r=>r.a===y&&r.m===m);
      // Only show cells for months that have data or are in the future for current/future years
      if(!hasData && y < TODAY_YEAR){ html+='<td style="color:var(--muted-2);text-align:center">—</td>'; continue; }
      const val = getTargetDisplay(y,m);
      const cellStyle = [
        'text-align:center;font-variant-numeric:tabular-nums;padding:5px 6px;cursor:pointer',
        isCur  ? 'background:var(--accent-soft);font-weight:700' : '',
        isPast && hasData ? 'color:var(--muted)' : '',
      ].filter(Boolean).join(';');
      html+=`<td style="${cellStyle}" data-y="${y}" data-m="${m}" class="target-cell">${fmtK(val)}</td>`;
    }
    html += '</tr>';
  });
  html += '</tbody></table>';

  const container = document.getElementById('target-table');
  container.innerHTML = html;

  // Inline editing: click → replace cell with input
  container.querySelectorAll('.target-cell').forEach(cell => {
    cell.addEventListener('click', function(){
      if(this.querySelector('input')) return; // already editing
      const y=+this.dataset.y, m=+this.dataset.m;
      const currentVal = getTargetDisplay(y,m);
      const inp = document.createElement('input');
      inp.type='number'; inp.value=currentVal; inp.min=0; inp.step=5000;
      inp.style.cssText='width:72px;font-size:12px;padding:2px 4px;text-align:right;border:1px solid var(--accent);border-radius:4px;font-family:inherit;font-variant-numeric:tabular-nums';
      this.textContent='';
      this.appendChild(inp);
      inp.focus(); inp.select();
      const save = ()=>{
        const v=parseInt(inp.value);
        if(v>0){ setMonthTarget(y,m,v); updateTargets(); renderAll(); }
        else renderTargetTable();
      };
      inp.addEventListener('blur', save);
      inp.addEventListener('keydown', e=>{
        if(e.key==='Enter'){ inp.blur(); }
        if(e.key==='Escape'){ renderTargetTable(); }
      });
    });
  });
}

// ---- Estrategia ----
function renderEstrategia(){
  // Calculate latest 6-month average vs target
  const allMonths=[];
  ALL_YEARS.forEach(y=>{
    const ms=monthlyForYear(y);
    ms.forEach((v,i)=>{ if(v>0 && !isPartialMonth(y,i)) allMonths.push({y,m:i+1,v}); });
  });
  const last6=allMonths.slice(-6);
  const avg6=last6.reduce((a,b)=>a+b.v,0)/(last6.length||1);
  const gap=TARGET-avg6;
  const gapPct=pct(avg6,TARGET);

  // Best historical month
  const bestEver=allMonths.reduce((a,b)=>b.v>a.v?b:a, {v:0});

  // Year over year for current year
  const ytdCurrent=monthlyForYear(CURRENT_YEAR).reduce((a,b)=>a+b,0);
  const ytdPrev=monthlyForYear(CURRENT_YEAR-1).slice(0,monthlyForYear(CURRENT_YEAR).filter(v=>v>0).length).reduce((a,b)=>a+b,0);
  const ytdYoy=ytdPrev?(ytdCurrent/ytdPrev-1)*100:0;

  const cards=[
    {cls:gapPct>=100?'good':'warn',h:'Promedio últimos 6 meses',big:fmtK(avg6),sub:gapPct>=100?'✓ Por encima del target':'A '+fmtK(Math.abs(gap))+' del target ('+fmtK(TARGET)+')'},
    {cls:'',h:'Mejor mes histórico',big:fmtK(bestEver.v||0),sub:bestEver.v?MONTHS_FULL[bestEver.m-1]+' '+bestEver.y:'–'},
    {cls:ytdYoy>=0?'good':'warn',h:'YTD '+CURRENT_YEAR+' vs '+(CURRENT_YEAR-1),big:(ytdYoy>=0?'+':'')+ytdYoy.toFixed(0)+'%',sub:fmtK(ytdCurrent)+' vs '+fmtK(ytdPrev)+' (mismos meses)'},
  ];
  document.getElementById('strat-cards').innerHTML=cards.map(c=>`
    <div class="strat-card ${c.cls}">
      <h4>${c.h}</h4>
      <div class="big">${c.big}</div>
      <p>${c.sub}</p>
    </div>`).join('');

  document.getElementById('chart-gap').innerHTML=chartGap();
  document.getElementById('chart-season').innerHTML=chartSeasonality();

  // Recommendations (simple data-driven)
  const vt2025=vendorTotals(new Set([CURRENT_YEAR-1]));
  const topVend=Object.entries(vt2025).sort((a,b)=>b[1]-a[1])[0];
  const ct=clientTotals(new Set(ALL_YEARS));
  const cliEntries=Object.entries(ct).sort((a,b)=>b[1]-a[1]);
  const top10cliPct=cliEntries.slice(0,10).reduce((a,b)=>a+b[1],0)/cliEntries.reduce((a,b)=>a+b[1],0)*100;

  // Seasonality peaks
  const seas=new Array(12).fill(0);
  const cnt=new Array(12).fill(0);
  ALL_YEARS.filter(y=>!PARTIAL_YEARS.has(y)).forEach(y=>{
    monthlyForYear(y).forEach((v,i)=>{ if(v>0){seas[i]+=v;cnt[i]++;} });
  });
  const seasAvg=seas.map((v,i)=>cnt[i]?v/cnt[i]:0);
  const topMonths=seasAvg.map((v,i)=>[v,i]).sort((a,b)=>b[0]-a[0]).slice(0,3);

  const recs=[
    {ic:'&#9889;', h:'Cerrar la brecha mensual', body:`Falta ${fmtK(Math.max(0,gap))} promedio por mes para llegar a ${fmtK(TARGET)}. Equivale a ~${(Math.max(0,gap)/(currency==='USD'?30000:30000*currentTC())).toFixed(1)} cliente${gap>(currency==='USD'?30000:30000*currentTC())?'s':''} nuevos de tama&ntilde;o medio por mes.`},
    {ic:'&#128101;', h:'Reforzar al top vendedor', body:topVend?`${VEND_LABELS[topVend[0]]||topVend[0]} aporta ${fmtK(topVend[1])} (${pct(topVend[1], Object.values(vt2025).reduce((a,b)=>a+b,0))}% del total ${CURRENT_YEAR-1}). Asegurar backup/colaboracion para no depender de una sola persona.`:'-'},
    {ic:'&#128202;', h:'Concentracion de cartera', body:`Los 10 primeros clientes representan el ${top10cliPct.toFixed(0)}% de la facturacion. ${top10cliPct>60?'Diversificar es prioridad - perder uno duele.':'Concentracion saludable.'}`},
    {ic:'&#128197;', h:'Aprovechar la estacionalidad', body:`Los mejores meses historicos son: <b>${topMonths.map(([v,i])=>MONTHS_FULL[i]).join(', ')}</b>. Concentrar lanzamientos y empuje comercial en esos meses puede acelerar el cumplimiento del objetivo anual.`},
  ];
  document.getElementById('recommendations').innerHTML=recs.map(r=>`
    <div style="display:flex;gap:12px;padding:12px 0;border-bottom:1px solid #f3f4f6">
      <div style="font-size:20px">${r.ic}</div>
      <div style="flex:1">
        <div style="font-weight:600;color:#111827;margin-bottom:4px">${r.h}</div>
        <div style="font-size:13px;color:#4b5563;line-height:1.5">${r.body}</div>
      </div>
    </div>`).join('');
}

// ---- Main render ----
// ---- Monthly evolution charts per tab ----
// If multiple years selected -> seasonality view (one line per year, Jan-Dec axis).
// If only one year -> chronological timeline.

function renderEvolResumen(){
  const el=document.getElementById('chart-evol-resumen');
  const sub=document.getElementById('evol-resumen-sub');
  if(selYears.size>1){
    if(sub) sub.textContent='Una l&iacute;nea por a&ntilde;o para detectar estacionalidad';
    el.innerHTML = chartSeasonalityByYear(r=>true);
  } else {
    if(sub) sub.textContent=currency+' facturado mes a mes';
    const series=[{name:'Facturaci&oacute;n total', color:'#2563eb', byKey:byKeyMap(r=>true)}];
    el.innerHTML = chartMonthlyTimeline(series, {area:true});
  }
}

function renderEvolVend(){
  const el=document.getElementById('chart-evol-vend');
  const sub=document.getElementById('evol-vend-sub');
  const vendors = ALL_VENDORS_RANKED.filter(v=>selVendors.has(v));
  if(selYears.size>1){
    if(sub) sub.textContent='Estacionalidad del equipo seleccionado · una l&iacute;nea por a&ntilde;o';
    const vendSet = new Set(vendors);
    el.innerHTML = chartSeasonalityByYear(r=>vendSet.has(r.v));
  } else {
    if(sub) sub.textContent='Una l&iacute;nea por vendedor seleccionado';
    const series = vendors.slice(0,8).map(v=>({
      name: VEND_LABELS[v]||v,
      color: VEND_PALETTE[v]||'#6b7280',
      byKey: byKeyMap(r=>r.v===v)
    }));
    el.innerHTML = chartMonthlyTimeline(series, {rightPad: 30});
  }
}

function renderEvolProd(){
  const el=document.getElementById('chart-evol-prod');
  const sub=document.getElementById('evol-prod-sub');
  const pt=productTotals(selYears);
  const top6 = Object.entries(pt).sort((a,b)=>b[1]-a[1]).slice(0,6).map(e=>e[0]);
  if(selYears.size>1){
    if(sub) sub.textContent='Estacionalidad de las top '+top6.length+' familias · una l&iacute;nea por a&ntilde;o';
    const top6Set = new Set(top6);
    el.innerHTML = chartSeasonalityByYear(r=>top6Set.has(r.p));
  } else {
    if(sub) sub.textContent='Top 6 familias';
    const palette=['#2563eb','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4'];
    const series = top6.map((p,i)=>({
      name: PROD_LABELS[p]||p,
      color: palette[i%palette.length],
      byKey: byKeyMap(r=>r.p===p)
    }));
    el.innerHTML = chartMonthlyTimeline(series, {rightPad: 30});
  }
}

function renderEvolEstr(){
  const el=document.getElementById('chart-evol-estr');
  if(selYears.size>1){
    el.innerHTML = chartSeasonalityByYear(r=>true, {target:TARGET});
  } else {
    const series=[{name:'Facturaci&oacute;n', color:'#2563eb', byKey:byKeyMap(r=>true)}];
    el.innerHTML = chartMonthlyTimeline(series, {target:TARGET, area:true});
  }
}

// ---- Origen tab ----
let selOrigen = 'ambos'; // 'ambos' | 'nacional' | 'importado'
function origenMatches(r){
  const o=origenOf(r.p||'');
  if(selOrigen==='ambos') return o==='nacional'||o==='importado';
  return o===selOrigen;
}
function origenLabel(){
  return selOrigen==='ambos'?'Nacional + Importado': (selOrigen==='nacional'?'Nacional':'Importado');
}
function origenColor(){
  return selOrigen==='nacional'?'#10b981': selOrigen==='importado'?'#f59e0b':'#2563eb';
}

function origenPeriodLabel(){
  const n=selMonths.size;
  const MONTHS_SHORT=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
  if(n===12) return 'todo el año';
  const ms=[...selMonths].sort((a,b)=>a-b);
  if(ms.length===1) return MONTHS_SHORT[ms[0]-1];
  return MONTHS_SHORT[ms[0]-1]+'–'+MONTHS_SHORT[ms[ms.length-1]-1];
}
function renderOrigenKPIs(){
  const yrLabel=[...selYears].sort().join(', ');
  const periodLabel=origenPeriodLabel();
  const fullLabel=yrLabel+' · '+periodLabel;
  const rows=VENTAS.filter(r=>selYears.has(r.a)&&inMonth(r)&&origenMatches(r));
  let total=0, byVend={}, byCli={};
  rows.forEach(r=>{
    const v=toAmount(r); total+=v;
    byVend[r.v]=(byVend[r.v]||0)+v;
    byCli[r.c]=(byCli[r.c]||0)+v;
  });
  // Total de productos (nacional+importado) para calcular el share
  let totalAll=0;
  VENTAS.filter(r=>selYears.has(r.a)&&inMonth(r)).forEach(r=>{
    const o=origenOf(r.p||'');
    if(o==='nacional'||o==='importado') totalAll+=toAmount(r);
  });
  const share = totalAll>0 ? total/totalAll*100 : 0;
  const topV = Object.entries(byVend).sort((a,b)=>b[1]-a[1])[0]||['—',0];
  const topC = Object.entries(byCli).sort((a,b)=>b[1]-a[1])[0]||['—',0];
  const col = origenColor();
  // Actualizar label de período en el header del panel
  const lbl=document.getElementById('origen-period-label');
  if(lbl) lbl.textContent = selMonths.size===12 ? '' : '→ '+periodLabel;

  const kpis=[
    {lbl:'TOTAL '+origenLabel().toUpperCase(), val:fmtK(total), sub:fullLabel, col},
    {lbl:'% DEL MIX DE PRODUCTOS', val:share.toFixed(1)+'%', sub:'de '+fmtK(totalAll)+' total · '+periodLabel, col},
    {lbl:'TOP VENDEDOR', val:(VEND_LABELS[topV[0]]||topV[0]||'—'), sub:fmtK(topV[1]), col},
    {lbl:'TOP CLIENTE', val:(topC[0]||'—').substring(0,28), sub:fmtK(topC[1]), col},
  ];
  document.getElementById('origen-kpis').innerHTML=kpis.map(k=>`
    <div style="background:#fff;border-radius:10px;padding:18px 20px;box-shadow:0 1px 3px rgba(0,0,0,.04);border:1px solid #eef0f3;border-left:4px solid ${k.col}">
      <div style="font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.7px;margin-bottom:6px">${k.lbl}</div>
      <div style="font-size:22px;font-weight:700;color:${k.col};line-height:1.1">${k.val}</div>
      <div style="font-size:11px;color:#6b7280;margin-top:6px">${k.sub}</div>
    </div>`).join('');
}

function renderEvolOrigen(){
  const el=document.getElementById('chart-evol-origen');
  const sub=document.getElementById('evol-origen-sub');
  if(selYears.size>1){
    if(sub) sub.textContent='Estacionalidad de '+origenLabel()+' · una l&iacute;nea por a&ntilde;o';
    el.innerHTML = chartSeasonalityByYear(r=>origenMatches(r));
  } else {
    if(sub) sub.textContent='Facturaci&oacute;n mes a mes — '+origenLabel();
    const series=[{name:origenLabel(), color:origenColor(), byKey:byKeyMap(origenMatches)}];
    el.innerHTML = chartMonthlyTimeline(series, {area:true});
  }
}

// ---- Pie chart ----
function chartPie(entries, opts={}){
  if(!entries.length) return '<p style="color:var(--muted-2);padding:20px">Sin datos</p>';
  const total=entries.reduce((s,e)=>s+e[1],0);
  if(!total) return '<p style="color:var(--muted-2);padding:20px">Sin datos</p>';
  // Paleta derivada del sistema de diseño Luctron
  const COLORS=['#0C2136','#3E688F','#2E7A4F','#B07410','#5C8AB5','#62B689','#6d4aad','#B33B3A','#7AA3CC','#E5B25C'];
  const R=88, CX=130, CY=100;
  // Calcular altura dinamica segun filas de leyenda
  const nRows=Math.ceil(entries.length/2);
  const legendH=nRows*17+10;
  const H=CY+R+14+legendH;
  let s=`<svg viewBox="0 0 260 ${H}" style="width:100%;display:block">`;
  // Sectores
  let angle=-Math.PI/2;
  entries.forEach((e,i)=>{
    const frac=e[1]/total;
    const end=angle+frac*2*Math.PI;
    const x1=CX+R*Math.cos(angle), y1=CY+R*Math.sin(angle);
    const x2=CX+R*Math.cos(end),   y2=CY+R*Math.sin(end);
    const large=frac>0.5?1:0;
    const pct=(frac*100).toFixed(1);
    const lbl=(opts.labels&&opts.labels[e[0]])||e[0];
    s+=`<path d="M${CX},${CY} L${x1.toFixed(2)},${y1.toFixed(2)} A${R},${R} 0 ${large},1 ${x2.toFixed(2)},${y2.toFixed(2)} Z" fill="${COLORS[i%COLORS.length]}" stroke="#fff" stroke-width="2"><title>${lbl}: ${fmtFull(e[1])} · ${pct}%</title></path>`;
    // Etiqueta de % encima del sector (solo si es visible)
    if(frac>0.07){
      const mid=angle+frac*Math.PI;
      const lx=CX+(R*0.65)*Math.cos(mid), ly=CY+(R*0.65)*Math.sin(mid);
      s+=`<text x="${lx.toFixed(1)}" y="${(ly+3).toFixed(1)}" text-anchor="middle" font-size="10" font-weight="700" fill="#fff">${Math.round(frac*100)}%</text>`;
    }
    angle=end;
  });
  // Leyenda debajo
  const ly0=CY+R+18;
  entries.forEach((e,i)=>{
    const row=Math.floor(i/2), col=i%2;
    const lx=8+col*126, ly=ly0+row*17;
    const lbl=((opts.labels&&opts.labels[e[0]])||e[0]).substring(0,13);
    s+=`<rect x="${lx}" y="${ly-7}" width="9" height="9" rx="2" fill="${COLORS[i%COLORS.length]}"/>`;
    s+=`<text x="${lx+13}" y="${ly}" font-size="9.5" fill="#6B6B6B">${lbl}</text>`;
  });
  s+='</svg>';
  return s;
}

function renderOrigenFamilies(){
  const sub=document.getElementById('origen-fam-sub');
  if(sub) sub.textContent=origenLabel()+' · '+[...selYears].sort().join(', ');
  const fam={};
  VENTAS.filter(r=>selYears.has(r.a)&&inMonth(r)&&origenMatches(r)).forEach(r=>{
    fam[r.p]=(fam[r.p]||0)+toAmount(r);
  });
  const entries=Object.entries(fam).sort((a,b)=>b[1]-a[1]).slice(0,10);
  document.getElementById('chart-origen-fam').innerHTML=chartHBars(entries,{max:10,labelW:110,color:origenColor(),labels:PROD_LABELS});
  document.getElementById('chart-origen-pie').innerHTML=chartPie(entries,{labels:PROD_LABELS});
}

function renderOrigenClients(){
  const sub=document.getElementById('origen-cli-sub');
  if(sub) sub.textContent='Nacional vs Importado por cliente · top 15 · '+[...selYears].sort().join(', ');
  // Per-client: nacional + importado split
  const byCli={};
  VENTAS.filter(r=>selYears.has(r.a)&&inMonth(r)).forEach(r=>{
    const o=origenOf(r.p||'');
    if(o!=='nacional'&&o!=='importado') return;
    if(!byCli[r.c]) byCli[r.c]={nacional:0,importado:0};
    byCli[r.c][o]+=toAmount(r);
  });
  // If a specific origen is selected, sort by that; otherwise by combined total
  const sortKey = selOrigen==='nacional' ? 'n' : selOrigen==='importado' ? 'i' : 'total';
  let mapped=Object.entries(byCli).map(([c,d])=>({
    label:c||'(sin cliente)',
    n:d.nacional,
    i:d.importado,
    total:d.nacional+d.importado
  }));
  // Cuando hay un origen seleccionado, descartar clientes que no compran ese tipo
  if(selOrigen!=='ambos'){
    mapped = mapped.filter(e => e[sortKey] > 0);
  }
  const entries = mapped.sort((a,b)=>b[sortKey]-a[sortKey]).slice(0,15);
  document.getElementById('chart-origen-cli').innerHTML=chartHBarsDouble(entries,{labelW:170});
}

// Horizontal bar chart with two parallel bars per row (nacional + importado)
function chartHBarsDouble(entries, opts={}){
  if(!entries.length) return '<p style="color:#9ca3af;padding:20px">Sin datos</p>';
  const ROW=42, BAR_H=14, BAR_GAP=3;
  const W=620, PL=opts.labelW||170, PR=70, PT=8;
  const H=PT+entries.length*ROW+24;
  const maxVal=Math.max(...entries.map(e=>Math.max(e.n,e.i)))||1;
  let s=svg(W,H);
  entries.forEach((e,i)=>{
    const y=PT+i*ROW;
    const bw1=(e.n/maxVal)*(W-PL-PR);
    const bw2=(e.i/maxVal)*(W-PL-PR);
    const lbl=(e.label||'').substring(0,22);
    s+=`<text x="${PL-6}" y="${(y+ROW/2+4).toFixed(1)}" text-anchor="end" font-size="11" fill="#1f2937" font-weight="500">${lbl}</text>`;
    // Nacional bar (green)
    s+=`<rect x="${PL}" y="${(y+5).toFixed(1)}" width="${Math.max(bw1,0.5).toFixed(1)}" height="${BAR_H}" fill="#10b981" rx="2"><title>${lbl} - Nacional: ${fmtFull(e.n)}</title></rect>`;
    if(e.n>0) s+=`<text x="${(PL+bw1+5).toFixed(1)}" y="${(y+5+BAR_H-3).toFixed(1)}" font-size="10" fill="#065f46" font-weight="600">${fmtK(e.n)}</text>`;
    // Importado bar (amber)
    const y2=y+5+BAR_H+BAR_GAP;
    s+=`<rect x="${PL}" y="${y2.toFixed(1)}" width="${Math.max(bw2,0.5).toFixed(1)}" height="${BAR_H}" fill="#f59e0b" rx="2"><title>${lbl} - Importado: ${fmtFull(e.i)}</title></rect>`;
    if(e.i>0) s+=`<text x="${(PL+bw2+5).toFixed(1)}" y="${(y2+BAR_H-3).toFixed(1)}" font-size="10" fill="#92400e" font-weight="600">${fmtK(e.i)}</text>`;
  });
  // Legend at bottom
  const legendY=H-8;
  s+=`<rect x="${PL}" y="${(legendY-10).toFixed(1)}" width="11" height="9" fill="#10b981" rx="1"/>`;
  s+=`<text x="${(PL+16).toFixed(1)}" y="${(legendY-2).toFixed(1)}" font-size="11" fill="#374151" font-weight="500">Nacional</text>`;
  s+=`<rect x="${(PL+85).toFixed(1)}" y="${(legendY-10).toFixed(1)}" width="11" height="9" fill="#f59e0b" rx="1"/>`;
  s+=`<text x="${(PL+101).toFixed(1)}" y="${(legendY-2).toFixed(1)}" font-size="11" fill="#374151" font-weight="500">Importado</text>`;
  s+='</svg>';
  return s;
}

function renderOrigenFamTable(){
  const sub=document.getElementById('origen-tbl-sub');
  if(sub) sub.textContent=origenLabel();
  // For each family that matches origen, show yearly breakdown
  const fams=new Set();
  VENTAS.filter(r=>origenMatches(r)).forEach(r=>fams.add(r.p));
  const famArr=[...fams];
  const pBY={};
  famArr.forEach(f=>pBY[f]={});
  VENTAS.filter(r=>fams.has(r.p)&&inMonth(r)).forEach(r=>{
    pBY[r.p][r.a]=(pBY[r.p][r.a]||0)+toAmount(r);
  });
  // Order by total in selected years
  famArr.sort((a,b)=>{
    let ta=0,tb=0;
    selYears.forEach(y=>{ ta+=pBY[a][y]||0; tb+=pBY[b][y]||0; });
    return tb-ta;
  });
  const totalAll=famArr.reduce((s,f)=>{ let t=0; selYears.forEach(y=>t+=pBY[f][y]||0); return s+t; },0);
  let html='<table><thead><tr><th>Familia</th><th>Origen</th>'+ALL_YEARS.map(y=>`<th>${y}${PARTIAL_YEARS.has(y)?'*':''}</th>`).join('')+'<th>Total per&iacute;odo</th><th>%</th></tr></thead><tbody>';
  famArr.forEach(f=>{
    const row=ALL_YEARS.map(y=>pBY[f][y]||0);
    let t=0; selYears.forEach(y=>t+=pBY[f][y]||0);
    const o=origenOf(f);
    const oTag=o==='importado'?'<span style="background:#fef3c7;color:#92400e;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700">IMPORT</span>':'<span style="background:#dcfce7;color:#166534;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700">NACIONAL</span>';
    html+=`<tr><td><b>${PROD_LABELS[f]||f}</b></td><td>${oTag}</td>${row.map(v=>`<td>${v>0?fmtK(v):'—'}</td>`).join('')}<td><b>${fmtFull(t)}</b></td><td>${totalAll?(t/totalAll*100).toFixed(1):0}%</td></tr>`;
  });
  html+='</tbody></table>';
  document.getElementById('origen-fam-table').innerHTML=html;
}

function renderOrigen(){
  renderOrigenKPIs();
  renderEvolOrigen();
  renderOrigenFamilies();
  renderOrigenClients();
  renderOrigenFamTable();
  // Re-render the year-by-year stack + pct chart (uses the existing functions)
  renderOrigenOverview();
}

function renderOrigenOverview(){
  // Stack + pct charts — these were previously inside Clientes & Productos
  const byYear=origenByYear();
  document.getElementById('chart-orig-stack').innerHTML=chartOrigenStacked(byYear);
  document.getElementById('chart-orig-pct').innerHTML=chartOrigenPct(byYear);

  // Year-by-year table
  let html='<table><thead><tr><th>A&ntilde;o</th><th>Nacional</th><th>Importado</th><th>Otros</th><th>Total productos</th><th>% Importado</th></tr></thead><tbody>';
  let sNac=0,sImp=0,sOt=0;
  ALL_YEARS.forEach(y=>{
    const d=byYear[y];
    const tp=d.nacional+d.importado;
    const impPct=tp?d.importado/tp*100:0;
    sNac+=d.nacional;sImp+=d.importado;sOt+=d.otros;
    html+=`<tr><td>${y}${PARTIAL_YEARS.has(y)?'*':''}</td><td>${fmtK(d.nacional)}</td><td>${fmtK(d.importado)}</td><td>${fmtK(d.otros)}</td><td>${fmtFull(tp)}</td><td>${impPct.toFixed(1)}%</td></tr>`;
  });
  const tp=sNac+sImp;
  html+=`<tr class="total"><td>TOTAL</td><td>${fmtFull(sNac)}</td><td>${fmtFull(sImp)}</td><td>${fmtFull(sOt)}</td><td>${fmtFull(tp)}</td><td>${tp?(sImp/tp*100).toFixed(1):0}%</td></tr>`;
  html+='</tbody></table>';
  document.getElementById('orig-table').innerHTML=html;
}

function renderAll(){
  // Update filter badge
  const yrs=[...selYears].sort();
  document.getElementById('filter-badge').textContent=yrs.join(', ');

  renderKPIs();
  renderEvolResumen();
  renderAnnualChart();
  renderTopVendResumen();
  renderAnnualTable();
  renderMonthly();
  renderVendores();
  renderEvolVend();
  renderClientes();
  renderAlertasComerciales();
  renderEvolProd();
  renderOrigen();
  renderDiario();
  renderEstrategia();
  renderTargetTable();
  renderEvolEstr();
}

// ---- Filters ----
function setupYearPills(){
  const c=document.getElementById('year-pills');
  c.innerHTML='';
  ALL_YEARS.forEach(y=>{
    const b=document.createElement('button');
    b.className='year-pill'+(selYears.has(y)?' active':'');
    b.textContent=y+(PARTIAL_YEARS.has(y)?'*':'');
    b.onclick=()=>{
      if(selYears.has(y)){
        if(selYears.size>1){selYears.delete(y);b.classList.remove('active');}
      }else{
        selYears.add(y);b.classList.add('active');
      }
      renderAll();
    };
    c.appendChild(b);
  });
}

document.getElementById('sel-todos').onclick=()=>{
  selYears=new Set(ALL_YEARS);
  setupYearPills();
  renderAll();
};
document.getElementById('sel-ultimos3').onclick=()=>{
  const last3=ALL_YEARS.slice(-3);
  selYears=new Set(last3);
  setupYearPills();
  renderAll();
};

// ---- Month filter pills ----
const MONTH_LABELS=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
function setupMonthPills(){
  const c=document.getElementById('month-pills');
  c.innerHTML='';
  for(let m=1;m<=12;m++){
    const b=document.createElement('button');
    b.className='month-pill'+(selMonths.has(m)?' active':'');
    b.textContent=MONTH_LABELS[m-1];
    b.onclick=()=>{
      if(selMonths.has(m)){
        if(selMonths.size>1){selMonths.delete(m);b.classList.remove('active');}
      }else{
        selMonths.add(m);b.classList.add('active');
      }
      updateMonthBadge();
      renderAll();
    };
    c.appendChild(b);
  }
  updateMonthBadge();
}
function updateMonthBadge(){
  const n=selMonths.size;
  const badge=document.getElementById('filter-badge-months');
  if(!badge) return;
  if(n===12) badge.textContent='12 meses';
  else if(n===1){ const m=[...selMonths][0]; badge.textContent=MONTH_LABELS[m-1]; }
  else {
    const ms=[...selMonths].sort((a,b)=>a-b);
    badge.textContent=ms.map(m=>MONTH_LABELS[m-1]).join(' · ');
  }
}
function setMonths(arr){
  selMonths=new Set(arr);
  setupMonthPills();
  renderAll();
}
document.getElementById('sel-months-actual').onclick=()=>setMonths([new Date().getMonth()+1]);
document.getElementById('sel-months-todos').onclick=()=>setMonths([1,2,3,4,5,6,7,8,9,10,11,12]);
document.getElementById('sel-months-q1').onclick=()=>setMonths([1,2,3]);
document.getElementById('sel-months-q2').onclick=()=>setMonths([4,5,6]);
document.getElementById('sel-months-q3').onclick=()=>setMonths([7,8,9]);
document.getElementById('sel-months-q4').onclick=()=>setMonths([10,11,12]);
document.getElementById('sel-months-ytd').onclick=()=>{
  const now=new Date(); const m=now.getMonth()+1;
  setMonths(Array.from({length:m},(_,i)=>i+1));
};
setupMonthPills();

// ---- Currency toggle ----
function setCurrency(c){
  if(c===currency) return;
  currency = c;
  updateTargets();
  document.getElementById('curr-usd').classList.toggle('active', c==='USD');
  document.getElementById('curr-ars').classList.toggle('active', c==='ARS');
  updateCurrencyLabels();
  renderAll();
}
function updateCurrencyLabels(){
  // Currency badge
  const cb=document.getElementById('filter-badge-curr');
  if(cb){
    cb.textContent=currency;
    cb.style.background=currency==='USD'?'#dcfce7':'#fef3c7';
    cb.style.color=currency==='USD'?'#166534':'#92400e';
  }
  const evolSub=document.getElementById('evol-estr-sub');
  if(evolSub) evolSub.textContent='Cada mes vs target ('+fmtK(TARGET)+')';
  const gapTitle=document.getElementById('gap-title');
  if(gapTitle) gapTitle.textContent='Análisis de brecha vs objetivo '+fmtK(TARGET)+'/mes';
  const noteTC=document.getElementById('note-tc-text');
  if(noteTC){
    if(currency==='USD'){
      noteTC.innerHTML='<b>Vista en USD:</b> ventas en ARS convertidas con TC BNA oficial hist&oacute;rico mensual. Las facturas en USD se toman directamente.';
    } else {
      noteTC.innerHTML='<b>Vista en ARS:</b> ventas en USD convertidas con TC BNA oficial hist&oacute;rico mensual. Las facturas en ARS se toman directamente. Target nominal: '+fmtK(TARGET)+'/mes (USD 215K al TC actual ~'+Math.round(currentTC())+').';
    }
  }
}
document.getElementById('curr-usd').onclick=()=>setCurrency('USD');
document.getElementById('curr-ars').onclick=()=>setCurrency('ARS');

// ---- Origen toggle (Ambos / Nacional / Importado) ----
document.querySelectorAll('.orig-btn').forEach(b=>{
  b.onclick=()=>{
    selOrigen=b.dataset.or;
    document.querySelectorAll('.orig-btn').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    renderOrigen();
  };
});

// ---- Origen period selector ----
function syncOrigenPeriodBtns(){
  const cur=[...selMonths].sort((a,b)=>a-b).join(',');
  document.querySelectorAll('.orig-period-btn').forEach(b=>{
    const v=b.dataset.months;
    const match = v==='all' ? selMonths.size===12 : v===cur;
    b.classList.toggle('active', match);
  });
}
document.querySelectorAll('.orig-period-btn').forEach(b=>{
  b.onclick=()=>{
    const v=b.dataset.months;
    if(v==='all'){
      selMonths=new Set([1,2,3,4,5,6,7,8,9,10,11,12]);
    } else {
      selMonths=new Set(v.split(',').map(Number));
    }
    setupMonthPills();   // sincroniza las pills globales
    updateMonthBadge();
    syncOrigenPeriodBtns();
    renderOrigen();
  };
});
// Sincronizar visualmente al arrancar
syncOrigenPeriodBtns();

// ---- Target input (filter bar — edita el mes en curso) ----
(function(){
  const inp = document.getElementById('target-input');
  const lbl = document.getElementById('target-currency-label');
  function syncDisplay(){
    inp.value = getTargetDisplay(TODAY_YEAR, TODAY_MONTH);
    inp.step = currency==='ARS' ? 1000000 : 5000;
    lbl.textContent = currency+'/mes · '+MONTHS[TODAY_MONTH-1]+' '+TODAY_YEAR;
  }
  inp.addEventListener('change', ()=>{
    const v = parseInt(inp.value);
    if(v > 0){ setMonthTarget(TODAY_YEAR, TODAY_MONTH, v); updateTargets(); renderAll(); }
    syncDisplay();
  });
  inp.addEventListener('keydown', e=>{ if(e.key==='Enter') inp.blur(); });
  // Re-sync when currency toggles
  const _orig = updateTargets;
  updateTargets = function(){ _orig(); syncDisplay(); };
  syncDisplay();
})();

// Vendedor quick filters
document.getElementById('sel-vend-todos').onclick=function(){
  selVendors=new Set(ALL_VENDORS_RANKED);
  vendQuickFilter='todos';
  document.getElementById('sel-vend-todos').classList.add('active');
  document.getElementById('sel-vend-activo').classList.remove('active');
  renderVendPills(); renderVendChart(); renderEvolVend();
};
document.getElementById('sel-vend-activo').onclick=function(){
  selVendors=new Set(ACTIVE_VENDORS.filter(v=>ALL_VENDORS_RANKED.includes(v)));
  vendQuickFilter='activo';
  document.getElementById('sel-vend-activo').classList.add('active');
  document.getElementById('sel-vend-todos').classList.remove('active');
  renderVendPills(); renderVendChart(); renderEvolVend();
};

// Tab navigation
document.querySelectorAll('.tab').forEach(t=>{
  t.onclick=()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById('panel-'+t.dataset.tab).classList.add('active');
  };
});

setupYearPills();
updateCurrencyLabels();
renderAll();

// ---- Botón Actualizar datos (requiere servidor servidor_dashboard.py) ----
async function actualizarDashboard(){
  const btn = document.getElementById('btn-refresh-dash');
  if(location.protocol === 'file:'){
    alert('Para usar Actualizar, abrí el dashboard desde el servidor:\\n\\n1. Doble clic en INICIAR_DASHBOARD.bat\\n2. Se abre en http://localhost:8766\\n\\n(Estás viendo el archivo directamente, sin servidor)');
    return;
  }
  const orig = btn.innerHTML;
  btn.innerHTML = '⏳ Actualizando desde SQL...';
  btn.disabled = true;
  try {
    const r = await fetch('/api/rebuild', {method:'POST'});
    const j = await r.json();
    if(j.ok){
      btn.innerHTML = '✓ Listo, recargando...';
      setTimeout(()=>location.reload(), 600);
    } else {
      btn.innerHTML = orig; btn.disabled = false;
      alert('Error al actualizar: ' + (j.msg||'desconocido'));
    }
  } catch(e){
    btn.innerHTML = orig; btn.disabled = false;
    alert('Error: ' + e.message);
  }
}
</script>
</body>
</html>"""

out = 'C:/Users/usuario/OneDrive/Escritorio/CLAUDE/dashboard_ventas.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"OK: {out}")
print(f"Size: {len(html)/1024:.0f} KB")
