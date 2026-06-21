---
name: Estructura de la base de ventas Luctron
description: La base de Luctron tiene facturas + ítems desde enero 2020 e incluye tipo de cambio por factura.
type: project
---

La base de ventas de Luctron tiene las siguientes características conocidas (a 2026-04-24):

- Granularidad: una fila por **ítem dentro de cada factura** (cabecera de factura + líneas de detalle).
- Cobertura: desde **enero 2020** hasta el presente (~6 años).
- Incluye **tipo de cambio** asociado a cada operación, lo que permite expresar todo en USD sin depender de fuentes externas.

**Why:** esto es lo que Nacho confirmó al inicio del proyecto. Saber que hay TC en la base es lo que permitió decidir dólares como moneda principal del dashboard.

**How to apply:** al recibir el archivo, validar:
1. Que efectivamente exista una columna de tipo de cambio (puede llamarse "TC", "Cotización", "USD", etc.).
2. Identificar columnas mínimas: fecha, nº factura, cliente, vendedor, código artículo, descripción, cantidad, precio, importe.
3. Revisar consistencia (vendedores con distintos nombres para la misma persona, fechas mal parseadas, importes negativos por notas de crédito, etc.).
