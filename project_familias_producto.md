---
name: Familias de producto Luctron
description: Catálogo de familias de producto (campo CA01_NOMBRE) presentes en la base de ventas y su volumen relativo.
metadata:
  type: project
---

La vista `dbo.vFacturas-Articulos` agrupa los artículos en 21 familias (campo `CA01_NOMBRE`). Las principales por volumen de líneas facturadas 2020–2026:

1. **LOEN** — top en volumen (~1.080 líneas), familia principal de Luctron
2. **OSLO** + **OSLO-EX** — segunda familia más vendida (~1.100 líneas combinadas)
3. **AURE** + **AURE-EX** — tercera (~700 líneas combinadas)
4. **MOSS** — ~525 líneas
5. **P3** — ~515 líneas (tubos LED)
6. **SERVICIOS** — ~420 líneas (no es producto físico, es servicio)
7. **NO APLICA** — ~560 líneas (sin clasificar)

Familias menores: ANKA, ODDA, VEGA, ROST, FREI, LEKA, HOLT, BODO, TINN, LENA, LIER.

**Why:** Confirmado en el pull de mayo 2026. Necesario para análisis de portfolio y decisiones de catálogo.

**Aclaraciones importantes (2026-05-21):**
- AURE y OSLO son **líneas distintas**, aunque ambas se aplican a estaciones de servicio. No mezclarlas en análisis.
- El sufijo **-EX** significa **Antiexplosivo (APE)**: son las versiones certificadas para zonas clasificadas / atmósferas explosivas (típicamente requeridas en áreas de carga de combustible). Por lo tanto OSLO-EX y AURE-EX son productos distintos al OSLO/AURE estándar (distinta certificación, distinto precio, distinto caso de uso). Mostrarlos siempre separados y, en el dashboard, etiquetar como "OSLO APE" / "AURE APE" para que sea legible.

**Clasificación nacional vs importado (2026-05-21):**
- **Importadas:** ANKA, HOLT, LENA, VIKS, BODO, LIER
- **Nacionales (producción local de Luctron):** todas las demás (LOEN, OSLO, OSLO-EX, AURE, AURE-EX, MOSS, P3, ODDA, VEGA, ROST, FREI, LEKA, TINN, etc.)
- "SERVICIOS" y "NO APLICA" no son productos físicos — clasificarlos aparte cuando se hagan análisis nacional vs importado.

**Why:** Nacho lo solicitó para poder analizar el mix de producción propia vs reventa, que tiene implicancias muy distintas en márgenes, dependencia de proveedores externos y capital de trabajo.

**How to apply:** En cualquier análisis nuevo, agregar el corte nacional/importado cuando se hable de productos. La evolución del % importado es un indicador estratégico clave (mayor % importado = mayor exposición al TC y dependencia de proveedores; menor % = más valor agregado local).

**How to apply:** Al hablar de productos, referirse a familias (CA01_NOMBRE) en lugar de SKUs individuales (ARTS_NOMBRE), porque la cantidad de artículos individuales es muy alta. Mantener AURE, OSLO, AURE-EX y OSLO-EX siempre separadas. Excluir "SERVICIOS" y "NO APLICA" cuando se analizan tendencias de productos físicos.
