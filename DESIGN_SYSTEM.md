# Sistema de Diseño · Estilo Luctron

> Documento técnico para replicar el look & feel de **LUMI** en cualquier aplicación. Todo lo de acá está pensado para que un dev lo copie, lo adapte al stack que use, y obtenga una app visualmente consistente.
>
> **Stack de origen**: HTML + CSS + JS plano (sin frameworks). Pero los principios y las variables CSS aplican a cualquier framework (React, Vue, Svelte, Angular, etc.) — solo cambia la sintaxis para consumirlos.

---

## Tabla de contenidos

1. [Filosofía visual](#1-filosofía-visual)
2. [Paleta de colores](#2-paleta-de-colores)
3. [Tipografía](#3-tipografía)
4. [Espaciado, bordes y radios](#4-espaciado-bordes-y-radios)
5. [Layout · App shell](#5-layout--app-shell)
6. [Componentes](#6-componentes)
7. [Sistema de status (semáforo)](#7-sistema-de-status-semáforo)
8. [Tema claro / oscuro](#8-tema-claro--oscuro)
9. [Iconografía](#9-iconografía)
10. [Microinteracciones](#10-microinteracciones)
11. [Reglas duras (qué NO hacer)](#11-reglas-duras-qué-no-hacer)
12. [Snippets listos para copiar](#12-snippets-listos-para-copiar)

---

## 1 · Filosofía visual

El estilo es **"SaaS moderno minimalista"** — pensado para apps internas donde la gente pasa horas mirando datos. Tres principios:

| Principio | Cómo se aplica |
|---|---|
| **Sobriedad cromática** | Color solo donde aporta significado (status, branding, foco). Todo lo demás es neutro. |
| **Densidad sin opresión** | Mucha info por pantalla, pero con respiración: padding generoso adentro, gaps medidos entre elementos. |
| **Jerarquía clara** | Tres niveles de texto (titulo / cuerpo / muted), nunca más. La negrita es para datos, no para decorar. |

**Inspiración**: Stripe Dashboard, Linear, Notion, Vercel. Tono profesional, no juguetón. Sin emojis. Sin gradientes berretas. Sin sombras dramáticas.

**Lo que NO somos**: Material Design (demasiados shadows, demasiados ripples). Bootstrap (genérico, identidad pobre). Tailwind UI default (gris azulado, todo igual).

---

## 2 · Paleta de colores

### 2.1 Paleta de marca (Luctron)

Solo se usan **estos 7 colores** como base. Todo lo demás deriva de ellos.

| Token | Hex | Uso típico |
|---|---|---|
| `--c-dark` | `#000000` | Hover sobre botones primary, fondo en dark mode profundo |
| `--c-midnight` | `#0F0F0F` | Botones primary, sidebar activo (light), chips activos |
| `--c-deep-blue` | `#0C2136` | **Feature cards**, KPI destacado, logo gradient, navy de marca |
| `--c-misty-blue` | `#3E688F` | Accent secundario, focus de inputs, avatar gradient, activo en dark |
| `--c-white` | `#FFFFFF` | Superficie principal en light, texto sobre dark |
| `--c-light-gray` | `#E8E8E8` | Bordes generales en light |
| `--c-medium-gray` | `#B0B0B0` | Texto muted secundario |

**Regla**: si te tienta meter otro color, mirá si podés conseguir el mismo efecto con opacidad o luminosidad de los existentes.

### 2.2 Tokens semánticos (LIGHT)

Lo que el dev usa día a día NO son los colores de marca directamente, sino estos tokens que les dan significado:

```css
:root {
    /* Superficies */
    --bg:               #F2F2F2;   /* fondo de página */
    --surface:          #FFFFFF;   /* cards, modales, panel principal */
    --surface-2:        #FAFAFA;   /* fondos internos de KPIs, descripciones */
    --surface-hover:    #F6F6F6;   /* hover sobre superficies clickeables */
    --feature-bg:       #0C2136;   /* card destacada / "highlight" */

    /* Bordes */
    --border:           #E4E4E4;   /* default para cards, inputs */
    --border-soft:      #EDEDED;   /* separadores internos sutiles */
    --border-strong:    #D8D8D8;   /* hover sobre bordes */

    /* Texto */
    --text:             #0F0F0F;   /* títulos y datos importantes */
    --text-2:           #2A2A2A;   /* cuerpo de texto normal */
    --muted:            #6B6B6B;   /* labels, metadata, info secundaria */
    --muted-2:          #9A9A9A;   /* placeholder, info terciaria */
    --on-dark:          #FFFFFF;   /* texto sobre fondos oscuros (feature) */
    --on-dark-muted:    #B7C3D1;   /* texto secundario sobre fondos oscuros */

    /* Accent */
    --accent:           #0C2136;   /* CTA primario, valor destacado */
    --accent-2:         #3E688F;   /* focus, hover, secondary CTA */
    --accent-soft:      #ECF1F7;   /* fondo de selección/activo, badges acento */
}
```

### 2.3 Tokens semánticos (DARK)

```css
[data-theme="dark"] {
    --bg:               #0A0A0A;
    --surface:          #131313;
    --surface-2:        #181818;
    --surface-hover:    #1E1E1E;
    --feature-bg:       #0C2136;

    --border:           #262626;
    --border-soft:      #1F1F1F;
    --border-strong:    #333333;

    --text:             #F5F5F5;
    --text-2:           #D6D6D6;
    --muted:            #8B8B8B;
    --muted-2:          #5F5F5F;

    --accent:           #3E688F;
    --accent-2:         #5C8AB5;
    --accent-soft:      #14233A;
}
```

### 2.4 Colores de status (semáforo)

Para indicar estados: éxito, alerta, error, informativo. Tienen 5 variantes cada uno: color base, fondo, borde, fondo-fila, fondo-fila-hover (las últimas dos para pintar renglones de tablas).

```css
:root {
    /* 🔴 ROJO — crítico / error */
    --rojo:             #B33B3A;
    --rojo-bg:          #FDECEC;
    --rojo-border:      #F5C9C8;
    --rojo-row:         #FBE5E5;
    --rojo-row-hover:   #F7D4D3;

    /* 🟡 AMARILLO — atención / pendiente */
    --amarillo:          #B07410;
    --amarillo-bg:       #FCF3DE;
    --amarillo-border:   #ECD79B;
    --amarillo-row:      #FAEECC;
    --amarillo-row-hover:#F5E2B0;

    /* 🟢 VERDE — éxito / OK */
    --verde:            #2E7A4F;
    --verde-bg:         #E8F4ED;
    --verde-border:     #B8DCC4;
    --verde-row:        #DCEFE2;
    --verde-row-hover:  #C7E5D0;

    /* 🔵 AZUL — informativo / sobre-rango */
    --azul-st:          #3E688F;
    --azul-st-bg:       #E8EEF5;
    --azul-st-border:   #BACBDF;
    --azul-row:         #DCE5EE;
    --azul-row-hover:   #C7D4E3;
}
```

**En dark mode** se mantiene la semántica pero con foreground más luminoso y backgrounds translúcidos:

```css
[data-theme="dark"] {
    --rojo:        #E07D7C;
    --rojo-bg:     rgba(179, 59, 58, .16);
    --rojo-border: rgba(179, 59, 58, .35);
    /* ... resto análogo */

    --amarillo:    #E5B25C;
    --verde:       #62B689;
    --azul-st:     #7AA3CC;
}
```

### 2.5 Cuándo usar cada color de status

| Color | Significado | Ejemplos |
|---|---|---|
| 🔴 Rojo | Acción urgente / crítica | Errores, items sin stock, alertas de seguridad |
| 🟡 Amarillo | Atención / advertencia | Items por agotarse, validaciones blandas |
| 🟢 Verde | Estado óptimo / éxito | "Guardado", items en rango ideal, confirmaciones |
| 🔵 Azul | Informativo / sobre lo esperado | Sobre-stock, info neutral, datos sin alarma |

**Regla**: nunca usar rojo para "muy alto" en contextos donde rojo significa error. Confunde. El color comunica significado, no escala.

---

## 3 · Tipografía

### 3.1 Familia

**Inter** (Google Fonts) — variable weights de 400 a 700. Es la fuente que usan Linear, Notion, Stripe. Diseñada para UI, excelente en pantalla en cualquier tamaño.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

```css
:root {
    --font: "Inter", ui-sans-serif, -apple-system, BlinkMacSystemFont,
            "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
}

body {
    font-family: var(--font);
    font-size: 13.5px;       /* base un poco más chico que el browser default — más SaaS */
    line-height: 1.5;
    letter-spacing: -0.005em;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
```

### 3.2 Escala tipográfica

| Uso | Tamaño | Peso | Letter-spacing | Notas |
|---|---|---|---|---|
| **Hero / Page title** | 20px | 700 | -0.4px | Título de página, máximo uno por vista |
| **Section title** | 15-16px | 700 | -0.2px | Título de tarjeta importante |
| **Card title** | 13-14px | 600 | -0.1px | Header de card secundaria |
| **KPI value** | 17-22px | 700 | -0.4px | Valor numérico grande (font-variant-numeric: tabular-nums) |
| **Body** | 12-13px | 400-500 | 0 | Texto general, párrafos |
| **Label / metadata** | 10-11px | 600 | 0.5px | uppercase | Etiquetas de campos, headers de tabla |
| **Caption / muted** | 10-11px | 400 | 0 | Subtítulos, info secundaria |
| **Monospace** | 11-12px | 500 | 0 | IDs, códigos, fechas tipo `13/04/2026` |

### 3.3 Reglas

- **Solo 3 jerarquías visibles por pantalla**: título → cuerpo → muted. Más niveles confunden.
- **Negrita = dato**: usar `font-weight: 700` para números importantes y `600` para títulos. NO para destacar palabras random en párrafos.
- **Uppercase + letter-spacing 0.5-0.7px** para labels y metadata (estilo dashboard moderno).
- **`font-variant-numeric: tabular-nums`** SIEMPRE en valores numéricos — evita que los dígitos "salten" entre filas de una tabla.
- **`letter-spacing: -0.005em`** sobre body como base — Inter se ve mejor un toque más apretada.
- **Letter-spacing negativo en títulos** (-0.2 a -0.5px según tamaño) — más moderno.

### 3.4 Color del texto

| Token | Cuándo |
|---|---|
| `--text` | Títulos, datos importantes (números, nombres, identificadores) |
| `--text-2` | Cuerpo de texto largo, descripciones |
| `--muted` | Labels uppercase, metadata, sub-textos |
| `--muted-2` | Placeholder, info terciaria (raramente visible) |

---

## 4 · Espaciado, bordes y radios

### 4.1 Espaciado

No usamos una escala matemática estricta. Usamos estos valores específicos según contexto:

| Valor | Uso |
|---|---|
| `2px` | gap entre elementos super-apretados (sub-labels) |
| `4-6px` | gap entre items en una pill/chip, padding interno mínimo |
| `8-10px` | gap entre cards, padding compacto |
| `10-14px` | gap estándar entre componentes, padding de cards |
| `14-22px` | padding interno de cards grandes (modal, hero) |
| `24-32px` | padding de página, separación entre secciones grandes |

**Regla**: la **densidad** del estilo es media-alta. Si te encontrás con paddings de 30-40px, probablemente sobre-espaciaste.

### 4.2 Border radius

```css
:root {
    --radius:           14px;   /* cards, modales (default) */
    --radius-sm:        10px;   /* KPIs, secciones internas */
    --radius-xs:        6px;    /* botones icon, badges */
    --pill:             999px;  /* pills, chips, toggles, badges, avatares */
}
```

| Token | Uso |
|---|---|
| `--radius` (14px) | Cards principales, modales, login card |
| `--radius-sm` (10px) | KPIs, sub-cards, inputs |
| `--radius-xs` (6px) | Botones icon, menu items, separadores internos |
| `--pill` (999px) | Pills de status, chips de filtro, avatares, toggles, search input |

**Regla**: cards grandes → 14px. Inputs y sub-elementos → 10px. Pills → 999px. **Nunca cuadrado (0px)**, salvo iconos.

### 4.3 Bordes

```css
border: 1px solid var(--border);            /* default para cards, inputs */
border-bottom: 1px solid var(--border-soft); /* separadores horizontales */
border-color: var(--border-strong);          /* hover sobre bordes */
```

**Regla**: borde 1px siempre. Nunca 2px (queda Bootstrap). Para énfasis se cambia el COLOR del borde, no el grosor.

### 4.4 Sombras

Sombras súper sutiles, **muy raramente**. Solo en modales/dropdowns/login card.

```css
/* Modal */
box-shadow: 0 16px 48px rgba(0,0,0,0.06);

/* Dropdown */
box-shadow: 0 12px 28px rgba(0,0,0,0.12);

/* Dark mode — un poco más intensas porque el fondo es oscuro */
[data-theme="dark"] .modal { box-shadow: 0 16px 48px rgba(0,0,0,0.4); }
```

**Regla**: si una card "normal" necesita sombra, probablemente le falta jerarquía por otro lado (color, tamaño, posición). NO sombrear todo.

---

## 5 · Layout · App shell

### 5.1 Estructura general

La app tiene **3 áreas fijas**:

```
┌──────┬────────────────────────────────────────────┐
│      │  TOPBAR (60px alto, sticky)                │
│ SIDE ├────────────────────────────────────────────┤
│ BAR  │                                            │
│      │  MAIN (contenido scrolleable, padding 24px)│
│ 64px │                                            │
│      │                                            │
└──────┴────────────────────────────────────────────┘
```

```css
:root {
    --sidebar-w: 64px;
    --topbar-h: 60px;
}

.app-shell {
    display: grid;
    grid-template-columns: var(--sidebar-w) 1fr;
    min-height: 100vh;
}
```

### 5.2 Sidebar (64px)

**Vertical, icon-only**, fija a la izquierda. Items de 40×40px con tooltip al hover (aparece a la derecha).

- Logo arriba (36×36, gradient)
- Items de navegación con SVG centrado (18×18, stroke-width 1.7)
- `.sidebar-spacer { flex: 1 }` empuja items secundarios (Admin, Ajustes) abajo
- Estado activo: fondo `--c-midnight` + texto `--c-white`

### 5.3 Topbar (60px)

**Horizontal, sticky**. De izquierda a derecha:

1. Title de la página (14px, 600)
2. Tabs en pill (opcional) — fondo `--bg`, items activos con fondo `--c-midnight`
3. Spacer
4. Search input (240px, pill, fondo `--bg`)
5. Theme toggle (icon-btn circular)
6. Notificaciones (icon-btn)
7. User pill (avatar + nombre + dropdown)

### 5.4 Main

```css
.app-main {
    padding: 24px 32px;
    max-width: 1600px;
    margin: 0 auto;
}
```

Padding lateral mayor que el vertical. Max-width centra en monitores grandes.

### 5.5 Layouts internos comunes

**2 columnas**:
```css
.layout-2col {
    display: grid;
    grid-template-columns: minmax(340px, 0.8fr) 1.2fr;
    gap: 10px;
    align-items: start;
}
@media (max-width: 1200px) { .layout-2col { grid-template-columns: 1fr; } }
```

**Stats row** (cards horizontales de KPIs grandes):
```css
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 12px;
}
@media (max-width: 1100px) { .stats-row { grid-template-columns: repeat(2, 1fr); } }
```

**KPI grid** (dentro de una card):
```css
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}
@media (max-width: 1100px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
```

---

## 6 · Componentes

### 6.1 Card (la base de todo)

```css
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    transition: border-color .12s;
}
```

**Variantes**:
- `.card.feature` — fondo `--feature-bg` (navy oscuro), texto blanco. Para destacar 1 card por sección.
- `.card.collapsible` — cabecera clickeable que pliega/despliega el contenido.

**Padding interno**:
- Card simple: `16-18px`
- Card con header propio: `padding: 0` en el `.card`, y `14-22px` dentro del `.card-header` y `.card-body` separados
- Card compacta (KPI, mini): `9-12px`

### 6.2 Stat card (KPI grande, top de página)

```html
<div class="stat-card zona-rojo">
    <div class="stat-card-head">
        <span class="stat-card-label">Crítico</span>
        <div class="stat-card-icon"><svg>...</svg></div>
    </div>
    <div class="stat-card-value">42</div>
    <div class="stat-card-foot">requieren acción</div>
</div>
```

```css
.stat-card { padding: 11px 14px; }
.stat-card-label { font-size: 11.5px; color: var(--muted); }
.stat-card-icon { width: 24px; height: 24px; border-radius: 6px; }   /* fondo según zona */
.stat-card-value { font-size: 22px; font-weight: 700; letter-spacing: -0.4px; }
.stat-card-foot { font-size: 10.5px; color: var(--muted); }
```

Variante `feature`: fondo `--feature-bg` (navy), texto blanco, ribbon de color arriba.

### 6.3 KPI (interno de detalle)

KPI compacto dentro de un grid:

```html
<div class="kpi">
    <div class="kpi-label">Stock actual</div>
    <div class="kpi-value">393 <span class="kpi-unit">UN</span></div>
</div>
```

```css
.kpi {
    background: var(--surface-2);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius-sm);
    padding: 9px 11px;
}
.kpi-label { font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 17px; font-weight: 700; }
.kpi-unit  { font-size: 10.5px; color: var(--muted); }
```

**Variantes**: `.kpi.highlight` (fondo `--feature-bg`), `.kpi.threshold-rojo`, `.kpi.threshold-amarillo` (status-tinted).

### 6.4 Botones

**Primary** (CTA principal):
```css
.btn-primary {
    background: var(--c-midnight);
    color: var(--c-white);
    border: none;
    border-radius: var(--pill);
    padding: 8px 16px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
}
.btn-primary:hover { background: var(--c-dark); }
[data-theme="dark"] .btn-primary { background: var(--c-misty-blue); }
```

**Secondary** (acción secundaria):
```css
.btn-secondary {
    background: transparent;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: var(--pill);
    padding: 8px 16px;
    font-weight: 600;
}
.btn-secondary:hover { border-color: var(--border-strong); background: var(--surface-hover); }
```

**Icon button** (acción pura ícono, en topbar/sidebar):
```css
.icon-btn {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: var(--bg);
    border: none;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
}
.icon-btn:hover { background: var(--surface-hover); }
```

**Icon button inline** (en filas de tabla, acción destructiva):
```css
.btn-icon {
    background: transparent;
    border: none;
    color: var(--muted);
    padding: 6px;
    border-radius: var(--radius-xs);
}
.btn-icon:hover { color: var(--text); background: var(--surface-hover); }
.btn-icon.danger:hover { color: var(--rojo); background: var(--rojo-bg); }
```

**Reglas**:
- Botón principal: forma pill (no rectangular). Para que se distinga de inputs/cards.
- Solo UN primary por área visible. Más es ruido.
- Padding asimétrico: más horizontal que vertical (`8px 16px`).

### 6.5 Pills, chips y badges

**Status pill** (estado visible):
```css
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: var(--pill);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.2px;
}
.status-pill.zona-rojo     { background: var(--rojo-bg); color: var(--rojo); }
.status-pill.zona-amarillo { background: var(--amarillo-bg); color: var(--amarillo); }
.status-pill.zona-verde    { background: var(--verde-bg); color: var(--verde); }
.status-pill.zona-azul     { background: var(--azul-st-bg); color: var(--azul-st); }
```

**Filter chip** (filtros activables):
```css
.chip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--pill);
    padding: 5px 11px;
    font-size: 11.5px;
    font-weight: 500;
    color: var(--text-2);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.chip:hover { border-color: var(--border-strong); }
.chip.active {
    background: var(--c-midnight);
    color: var(--c-white);
    border-color: var(--c-midnight);
}
```

**Chip dot** (puntito de color a la izquierda del label):
```css
.chip-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; }
```

**Chip count** (badge numérico a la derecha):
```css
.chip-count {
    background: rgba(0,0,0,.06);
    border-radius: var(--pill);
    padding: 0 6px;
    font-size: 10.5px;
    font-weight: 600;
    min-width: 18px;
    text-align: center;
}
.chip.active .chip-count { background: rgba(255,255,255,.18); }
```

### 6.6 Inputs

```css
input[type="text"], input[type="search"], input[type="password"], input[type="email"] {
    width: 100%;
    padding: 9px 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text);
    font-size: 13px;
    font-family: inherit;
    transition: border-color .12s, background .12s;
    box-sizing: border-box;
}
input::placeholder { color: var(--muted-2); }
input:focus {
    outline: none;
    background: var(--surface);
    border-color: var(--accent-2);
}
```

**Search input** (con ícono dentro, en topbar):
```css
.search-input {
    border-radius: var(--pill);
    padding-left: 34px;
    background: var(--bg);
}
/* SVG del ícono absolute positioned al `left: 12px` con color var(--muted-2) */
```

**⚠ Patrón reutilizable `.search-row`** — IMPORTANTE ponerlo en `base.css`, no en CSS de un módulo:

```html
<div class="search-row">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
    <input type="search" placeholder="Buscar...">
</div>
```

```css
.search-row { position: relative; }
.search-row svg {
    position: absolute; left: 12px; top: 50%;
    transform: translateY(-50%);
    width: 14px; height: 14px;
    color: var(--muted-2);
    pointer-events: none;
}
.search-row input {
    width: 100%;
    padding: 9px 12px 9px 34px;
    background: var(--bg);
    border: 1px solid transparent;
    border-radius: var(--pill);
    box-sizing: border-box;
    /* ... */
}
```

**Bug clásico**: si los estilos viven solo en el CSS de UN módulo, otros módulos que usen `.search-row` van a ver el SVG renderizado a tamaño natural (gigante, ~150px). El SVG necesita `width/height` explícitos para no salirse de control.

### 6.7 Tablas

```css
.table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.table thead th {
    background: var(--surface);
    color: var(--muted);
    font-weight: 600;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: left;
    padding: 7px 14px;
    border-bottom: 1px solid var(--border-soft);
    position: sticky;
    top: 0;
    z-index: 1;
}
.table tbody td {
    padding: 6px 14px;
    border-bottom: 1px solid var(--border-soft);
    font-variant-numeric: tabular-nums;
}
.table tbody tr:last-child td { border-bottom: none; }
.table tbody tr:hover { background: var(--surface-hover); }
```

**Filas pintadas por status** (semáforo):
```css
.table tbody tr.zona-rojo     { background: var(--rojo-row); }
.table tbody tr.zona-rojo:hover { background: var(--rojo-row-hover); }
/* ... idem para amarillo, verde, azul */
```

### 6.8 Modal

```css
.modal { position: fixed; inset: 0; z-index: 100; }
.modal-backdrop {
    position: absolute; inset: 0;
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(4px);
}
.modal-window {
    position: relative;
    margin: 6vh auto;
    width: min(94vw, 540px);
    background: var(--surface);
    border-radius: var(--radius);
    box-shadow: 0 16px 48px rgba(0,0,0,0.3);
}
.modal-header {
    padding: 16px 22px;
    border-bottom: 1px solid var(--border-soft);
    display: flex; justify-content: space-between; align-items: center;
}
.modal-body { padding: 18px 22px 20px; }
.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 16px;
}
```

**Pattern**: backdrop con blur, ventana centrada, header con `×` para cerrar, footer con botones a la derecha (secondary "Cancelar" + primary "Guardar"). Esc cierra.

### 6.9 Dropdown / menu flotante

```css
.dropdown {
    position: absolute;
    top: calc(100% + 6px);
    right: 0;
    min-width: 220px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    box-shadow: 0 12px 28px rgba(0,0,0,0.12);
    padding: 4px;
    z-index: 50;
    opacity: 0;
    transform: translateY(-4px);
    pointer-events: none;
    transition: opacity .12s, transform .12s;
}
.dropdown.open {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
}
.dropdown-item {
    display: flex; align-items: center; gap: 8px;
    width: 100%;
    background: transparent;
    border: none;
    padding: 8px 12px;
    border-radius: var(--radius-xs);
    cursor: pointer;
    font-size: 12.5px;
    text-align: left;
}
.dropdown-item:hover { background: var(--surface-hover); }
```

### 6.10 Avatar (iniciales)

```css
.avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--c-deep-blue), var(--c-misty-blue));
    color: var(--c-white);
    display: flex; align-items: center; justify-content: center;
    font-weight: 600;
    font-size: 11.5px;
}
```

**Tamaños**: 26px (en filas), 28px (topbar), 36px (sidebar logo), 44px (login). Mismo gradient siempre.

---

## 7 · Sistema de status (semáforo)

4 zonas con significado universal en toda la app:

| Zona | Color | Significado | Cuándo usar |
|---|---|---|---|
| 🔴 **Rojo** | `--rojo` | Crítico / urgente | Errores, items en zona crítica, alertas |
| 🟡 **Amarillo** | `--amarillo` | Atención / pendiente | Por agotarse, warning, validación blanda |
| 🟢 **Verde** | `--verde` | Óptimo / éxito | "Guardado", en rango ideal |
| 🔵 **Azul** | `--azul-st` | Informativo / sobre | Sobre-stock, info neutra |

Para CADA zona hay 5 variantes:
- `--xxx` → foreground (texto, íconos)
- `--xxx-bg` → background suave (pill, kpi, badge)
- `--xxx-border` → borde
- `--xxx-row` → fondo de fila en tabla
- `--xxx-row-hover` → fondo de fila en hover

**Patrón típico** (status pill):
```html
<span class="status-pill zona-rojo">Crítico · -0,58</span>
```

```css
.status-pill.zona-rojo {
    background: var(--rojo-bg);
    color: var(--rojo);
    border: 1px solid var(--rojo-border);  /* opcional */
}
```

---

## 8 · Tema claro / oscuro

### 8.1 Estructura

- **Light por defecto** (en `:root`)
- **Dark se activa con `data-theme="dark"`** en el `<html>` root
- Toggle persiste en `localStorage['lumi.theme']`

### 8.2 Pre-paint script (evita el "flash" blanco al cargar dark)

Va en el `<head>`, ANTES de cualquier CSS:

```html
<script>
(function () {
    try {
        var t = localStorage.getItem('lumi.theme');
        if (!t) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', t);
    } catch (e) {
        document.documentElement.setAttribute('data-theme', 'light');
    }
})();
</script>
```

Esto setea el atributo ANTES de pintar, así no se ve el flash de luz cuando el usuario tiene tema oscuro.

### 8.3 Botón de toggle

```html
<button class="theme-toggle" id="themeToggle" aria-label="Cambiar tema">
    <svg class="icon-sun">...</svg>
    <svg class="icon-moon">...</svg>
</button>
```

```css
.theme-toggle .icon-sun { display: none; }
.theme-toggle .icon-moon { display: block; }
[data-theme="dark"] .theme-toggle .icon-sun { display: block; }
[data-theme="dark"] .theme-toggle .icon-moon { display: none; }
```

```javascript
document.getElementById('themeToggle').addEventListener('click', function () {
    var cur = document.documentElement.getAttribute('data-theme') || 'light';
    var next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('lumi.theme', next); } catch (e) {}
});
```

### 8.4 Reglas para que dark funcione bien

- **Nunca hardcodear colores** (`color: #333`, `background: white`). Siempre var.
- **Status colors en dark** son más luminosos y los backgrounds son `rgba(.... 0.16)` (translúcidos) para que se integren al fondo oscuro.
- **Sombras en dark** más intensas (0.4-0.5 alpha vs 0.06-0.12 en light).
- **No usar `filter: invert()`** — es un truco feo, rompe imágenes/SVGs con color.

---

## 9 · Iconografía

**Librería**: [Feather Icons](https://feathericons.com/) — SVGs inline, stroke-based, 24×24 viewBox.

**Características**:
- `fill="none"` (nunca rellenos)
- `stroke="currentColor"` (heredan color del texto)
- `stroke-width="2"` (default), `1.7` en sidebar para que se vea más delicado
- `stroke-linecap="round"`, `stroke-linejoin="round"`

**Tamaños típicos**:
| Contexto | Tamaño |
|---|---|
| Sidebar | 18×18 (stroke 1.7) |
| Icon button topbar | 15×15 |
| Botones inline | 14×14 |
| Stat card | 12-14×12-14 |
| Stroke fino dentro de tabla | 14×14 |

**Cómo se usan** (inline directo en HTML, no librería JS):

```html
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
    <path d="..."/>
</svg>
```

**Por qué inline y no `<img>` o librería**:
- El color del trazo cambia automáticamente con `currentColor` (theme-aware sin esfuerzo)
- Cero requests HTTP extra
- Cero dependencia JS
- Custom tweaks fáciles (cambiar stroke, agregar animaciones)

---

## 10 · Microinteracciones

Animaciones **muy sutiles**. Todo es `transition: ... .12s` (a veces `.15s`). Nada de bounce, ease-out, spring.

### Cosas que SÍ tienen transición:

| Elemento | Transición |
|---|---|
| Hover de card / item | `background-color .12s` |
| Hover de borde | `border-color .12s` |
| Focus de input | `border-color .12s, background .12s` |
| Toggle de theme | `background-color .15s, color .15s` en body |
| Dropdown abrir/cerrar | `opacity .12s, transform .12s` (slide-down 4px) |
| Chevron de collapsible | `transform .15s` (rotate -90deg) |
| Tooltip aparecer | `opacity .12s` |
| Botón press | `transform .05s` (translateY 1px) |

### Cosas que NO tienen transición:

- Cambios de contenido (renderizar una tabla, mostrar/ocultar una card por modo)
- Carga de datos (mostrar skeleton es OK pero sin animación de aparición)
- Modal aparecer (aparece de una, no necesita anim — el backdrop ya da contexto)

**Regla de oro**: si dudás si una transición está bien, sacala. La interacción sin animación se siente más rápida.

---

## 11 · Reglas duras (qué NO hacer)

| ❌ NO | ✅ Sí |
|---|---|
| Usar `box-shadow` en cards "normales" | Bordes 1px + background separado |
| Sombras dramáticas | Sombras 0.06-0.12 alpha, solo en modal/dropdown/login |
| Más de 1 botón "primary" por área visible | 1 primary + N secondary |
| Animaciones de 300-500ms | 100-150ms máximo |
| Colores random fuera de la paleta | Solo paleta + status |
| Bordes 2px+ | Siempre 1px, cambiar COLOR para énfasis |
| Esquinas en 0px (cuadrado puro) | Mínimo `--radius-xs` (6px), salvo SVGs |
| Emojis decorativos en UI | SVG icons (Feather) |
| Inputs con border-radius 4-6px | 10px (`--radius-sm`) para form, 999 (pill) para search |
| Gradientes coloridos | Solo navy `--c-deep-blue → --c-misty-blue` (logos, avatares) |
| Texto en italic | Casi nunca. Si necesitás énfasis, usá peso |
| `letter-spacing: 0` en labels | Usá 0.5-0.7px para uppercase |
| Sub-textos en negro al 70% opacidad | Usar `--muted` que tiene color sólido específico |
| Saltos numéricos en tablas (sin tabular-nums) | SIEMPRE `font-variant-numeric: tabular-nums` en números |
| Hardcodear `#FFFFFF` en JSX/templates | `var(--surface)` |
| Background images decorativos | Cero. Solo radial-gradients muy sutiles en hero/login |

---

## 12 · Snippets listos para copiar

### 12.1 Bloque de CSS variables completo

Pegá esto al principio de tu `base.css` y ya tenés todo lo que necesitás:

```css
:root {
    /* === Paleta principal === */
    --c-dark:           #000000;
    --c-midnight:       #0F0F0F;
    --c-deep-blue:      #0C2136;
    --c-misty-blue:     #3E688F;
    --c-white:          #FFFFFF;
    --c-light-gray:     #E8E8E8;
    --c-medium-gray:    #B0B0B0;

    /* === Superficies (LIGHT) === */
    --bg:               #F2F2F2;
    --surface:          #FFFFFF;
    --surface-2:        #FAFAFA;
    --surface-hover:    #F6F6F6;
    --feature-bg:       var(--c-deep-blue);

    --border:           #E4E4E4;
    --border-soft:      #EDEDED;
    --border-strong:    #D8D8D8;

    --text:             #0F0F0F;
    --text-2:           #2A2A2A;
    --muted:            #6B6B6B;
    --muted-2:          #9A9A9A;
    --on-dark:          #FFFFFF;
    --on-dark-muted:    #B7C3D1;

    --accent:           var(--c-deep-blue);
    --accent-2:         var(--c-misty-blue);
    --accent-soft:      #ECF1F7;

    /* === Status (LIGHT) === */
    --rojo:             #B33B3A;
    --rojo-bg:          #FDECEC;
    --rojo-border:      #F5C9C8;
    --rojo-row:         #FBE5E5;
    --rojo-row-hover:   #F7D4D3;

    --amarillo:         #B07410;
    --amarillo-bg:      #FCF3DE;
    --amarillo-border:  #ECD79B;
    --amarillo-row:     #FAEECC;
    --amarillo-row-hover:#F5E2B0;

    --verde:            #2E7A4F;
    --verde-bg:         #E8F4ED;
    --verde-border:     #B8DCC4;
    --verde-row:        #DCEFE2;
    --verde-row-hover:  #C7E5D0;

    --azul-st:          #3E688F;
    --azul-st-bg:       #E8EEF5;
    --azul-st-border:   #BACBDF;
    --azul-row:         #DCE5EE;
    --azul-row-hover:   #C7D4E3;

    /* === Tipografía === */
    --font: "Inter", ui-sans-serif, -apple-system, BlinkMacSystemFont,
        "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;

    /* === Layout === */
    --radius:           14px;
    --radius-sm:        10px;
    --radius-xs:        6px;
    --pill:             999px;

    --sidebar-w:        64px;
    --topbar-h:         60px;
}

[data-theme="dark"] {
    --bg:               #0A0A0A;
    --surface:          #131313;
    --surface-2:        #181818;
    --surface-hover:    #1E1E1E;
    --feature-bg:       var(--c-deep-blue);

    --border:           #262626;
    --border-soft:      #1F1F1F;
    --border-strong:    #333333;

    --text:             #F5F5F5;
    --text-2:           #D6D6D6;
    --muted:            #8B8B8B;
    --muted-2:          #5F5F5F;

    --accent:           var(--c-misty-blue);
    --accent-2:         #5C8AB5;
    --accent-soft:      #14233A;

    --rojo:             #E07D7C;
    --rojo-bg:          rgba(179, 59, 58, .16);
    --rojo-border:      rgba(179, 59, 58, .35);
    --rojo-row:         rgba(179, 59, 58, .10);
    --rojo-row-hover:   rgba(179, 59, 58, .18);

    --amarillo:         #E5B25C;
    --amarillo-bg:      rgba(176, 116, 16, .16);
    --amarillo-border:  rgba(176, 116, 16, .38);
    --amarillo-row:     rgba(176, 116, 16, .10);
    --amarillo-row-hover:rgba(176, 116, 16, .18);

    --verde:            #62B689;
    --verde-bg:         rgba(46, 122, 79, .16);
    --verde-border:     rgba(46, 122, 79, .38);
    --verde-row:        rgba(46, 122, 79, .10);
    --verde-row-hover:  rgba(46, 122, 79, .18);

    --azul-st:          #7AA3CC;
    --azul-st-bg:       rgba(62, 104, 143, .18);
    --azul-st-border:   rgba(62, 104, 143, .4);
    --azul-row:         rgba(62, 104, 143, .12);
    --azul-row-hover:   rgba(62, 104, 143, .22);
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; height: 100%; }

body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 13.5px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    letter-spacing: -0.005em;
    transition: background-color .15s, color .15s;
}
```

### 12.2 HTML base (head + body shell)

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi App</title>

    <!-- Pre-paint del tema (evita flash en dark mode) -->
    <script>
    (function () {
        try {
            var t = localStorage.getItem('app.theme');
            if (!t) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', t);
        } catch (e) {
            document.documentElement.setAttribute('data-theme', 'light');
        }
    })();
    </script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="base.css">
</head>
<body>
    <div class="app-shell">
        <aside class="sidebar">
            <div class="sidebar-logo">M</div>
            <!-- items de nav -->
        </aside>

        <div>
            <header class="topbar">
                <span class="topbar-title">Mi App</span>
                <!-- tabs / search / actions / user -->
            </header>

            <main class="app-main">
                <!-- contenido -->
            </main>
        </div>
    </div>
</body>
</html>
```

### 12.3 Checklist para empezar un módulo nuevo

Cuando hagas una vista/módulo, validá en este orden:

1. **Estructura**: usa `.app-shell` con sidebar 64px + topbar 60px + main.
2. **Page header**: título h1 20px + subtítulo muted + opcional botón primary al lado.
3. **Stats row** (opcional): 2-4 stat cards arriba con KPIs globales.
4. **Layout principal**: 1 columna, 2 columnas (con `.layout-2col`), o grid.
5. **Cards**: cada bloque de info es una card. Header (con título + count) + body. Si tiene mucho contenido, hacela collapsible.
6. **Status**: si hay items con estados, usar zonas rojo/amarillo/verde/azul. Coherente con el resto de la app.
7. **Tablas**: thead sticky, hover row, tabular-nums en números, max-height + overflow auto.
8. **Empty/error states**: siempre prever. Mensajes amables con `--muted`.
9. **Loading**: usar texto "cargando…" en muted dentro del contenedor (no spinner global).
10. **Mobile**: por lo menos colapsar grids a 1 columna en `< 1200px`. La app es para desktop pero que no se rompa.

---

## Apéndice — Convenciones de nombres

### CSS

- Tokens semánticos en `--snake-case` (`--surface-2`, `--rojo-row`).
- Componentes en `.kebab-case` (`.stat-card`, `.user-pill`).
- Modificadores con punto separado (`.kpi.highlight`, `.chip.active`).
- Variantes de zona con prefijo `.zona-*` (`.zona-rojo`).

### HTML

- Atributos `data-*` para estado JS (`data-collapse-key`, `data-zone`).
- `id` para elementos únicos referenciados por JS.
- Clases utilitarias: `.hidden`, `.muted`, `.empty`.

### JS

- Estado global en un objeto `state = { ... }`.
- Funciones puras de render: `renderXxx(data)`.
- Cache de fetches por key: `state.xxxCache[key]`.
- IDs de localStorage prefijados: `app.modulo.key`.

---

**Fin del documento.** Si necesitás aclarar algo o agregar un componente nuevo, mantenelo en este estilo: el secreto es la **consistencia**, no la cantidad de variantes.
