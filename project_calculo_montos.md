---
name: Reglas de cálculo de montos de venta Luctron
description: Cómo calcular el monto facturado a partir de la vista dbo.vFacturas-Articulos (signo, moneda, exclusiones).
metadata:
  type: project
---

## ⚠️ CORRECCIÓN CRÍTICA (2026-05-28): usar vIngreso-Ventas.TOTAL, no el precio bruto

**El método correcto NO es `vFacturas-Articulos`** (que solo tiene el precio de LISTA bruto, `CVRF_PRE_BRUORI_SI`, SIN el descuento por artículo). Calcular `cantidad × precio bruto` infla los montos enormemente (ej. factura Farmacity FC4 #174: bruto $93,2M vs neto real $26,9M — ¡un 71% de descuento por artículo!).

**Método correcto:**
- **Fuente del monto:** `dbo.vIngreso-Ventas`, columna **`TOTAL`** — ya viene con el descuento por artículo aplicado (precio neto × cantidad).
- **El TOTAL ya trae el signo:** facturas (F*, P*) positivas, notas de crédito (C*, N*) negativas. **NO aplicar ninguna regla de signo por prefijo** — el sistema ya lo hace (verificado: 213 C* y 103 N* todas negativas).
- **El TOTAL está siempre en PESOS** (incluso para comprobantes facturados en DL). Por lo tanto: ARS = TOTAL directo; USD = TOTAL / TC del mes.
- **Vendedor y moneda:** `vIngreso-Ventas` no tiene VEND_NOMBRE ni CTEC_MONEDA. Unir con `vFacturas-Articulos` agregada a nivel factura: `JOIN ON fecha + tipo_var + numero`, tomando MAX(VEND_NOMBRE), MAX(CTEC_MONEDA).
- **Evitar duplicación:** agrupar `vIngreso-Ventas` por (fecha, tipo, numero, cliente, familia, articulo) antes del join; agrupar `vFacturas` por (fecha, tipo, numero). Join 1:N limpio.
- Filtrar `ing.total <> 0`.

El pull canónico está en `_pull_neto_v5.py` y replicado en `servidor_dashboard.py` y `reunion_ventas/servidor_reunion.py`. Genera `ventas_data_v5.json`.

Totales netos de control (ARS): 2024 $1.789M · 2025 $2.561M · 2026 YTD(may) $1.150M.

**Limitación conocida — descuento de pie de factura (2026-05-28):** Algunas facturas tienen, además del descuento por artículo (ya incluido en TOTAL), un **descuento global de pie de factura** que se aplica sobre el subtotal (después del descuento por artículo). No se pudo determinar si el `TOTAL` de vIngreso-Ventas lo incluye prorrateado o no, porque **no se encontró ninguna columna ni vista accesible con ese descuento global ni con el total final del comprobante**. Nacho indicó dejarlo así por ahora. Implicancia: las facturas que tuvieron descuento de pie podrían estar levemente sobreestimadas en los dashboards. Si en el futuro aparece una vista con el total final del comprobante (o el % de descuento de cabecera), revisar este punto.

---

## Método viejo (DEPRECADO — inflaba ~21%+ los montos)
Lo de abajo era el criterio anterior con `vFacturas-Articulos`. Se mantiene como referencia histórica pero NO usar para montos.

Para calcular ventas netas a partir de `dbo.vFacturas-Articulos`:

## 1. Signo según prefijo de `CVCL_TIPO_VAR`
**Todos los valores en la tabla vienen positivos.** El signo lo determina el prefijo del tipo de comprobante:

| Prefijo | Naturaleza | Signo |
|---|---|---|
| `F*` | Factura (con IVA) | **+ suma** |
| `P*` | Factura sin IVA | **+ suma** |
| `C*` | Nota de crédito | **− resta** |
| `N*` | Desconocido (NC, NF, N4 — pocos casos y antiguos) | **+ suma** (provisional) |
| `APD`, `000` | Desconocido | **+ suma** (provisional, marginal) |

**Regla simple:** todo lo que arranca con `C` resta; el resto suma.

## 2. Monto por línea
```
monto_linea = signo × CVRF_CANT_ING × CVRF_PRE_BRUORI_SI
```
- `CVRF_PRE_BRUORI_SI` es el **precio bruto unitario original** (sin IVA según convención del sistema).
- `CVRF_CANT_ING` es la cantidad ingresada.

## 3. Moneda
- `CTEC_MONEDA = 'DL'` → el monto ya está en USD.
- `CTEC_MONEDA = 'PS'` → el monto está en ARS; convertir a USD usando TC histórico mensual (en el dashboard uso BNA oficial aproximado embebido).

## 4. Filtros que aplico
- `CVRF_CANT_ING > 0` y `CVRF_PRE_BRUORI_SI > 0` (descarta líneas anuladas / regalos).
- Desde 2020 en adelante.
- **NO filtrar más por tipo_var**: las NC ahora entran con signo negativo, no se excluyen.

## 5. Materialidad de las NC (verificado mayo 2026)
Las notas de crédito (C*) son ~471 líneas (vs ~5117 facturas). En 2024-2025 representan ~$350M ARS por año — material, ignorarlas inflaba sustancialmente las ventas.

**Why:** Confirmado por Nacho el 2026-05-21. Antes el dashboard filtraba NC en vez de restarlas, lo cual sobreestimaba la facturación neta.

**How to apply:** Cualquier consulta nueva sobre montos debe aplicar el signo por prefijo. Si aparecen tipos de comprobante nuevos que no empiezan con F/P/C/N, confirmar con Nacho antes de asumir signo.
