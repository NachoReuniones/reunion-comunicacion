---
name: Preferencias para dashboards y reportes
description: Nacho prefiere dashboards HTML autocontenidos en USD, con foco en facturación y vendedores.
type: feedback
---

Para entregables de análisis comercial en este proyecto:

- **Formato preferido:** dashboard HTML interactivo de un solo archivo, con los datos embebidos adentro (sin servidor, abrir con doble clic).
- **Moneda:** dólares, usando el tipo de cambio que ya viene en la base de ventas. Esto neutraliza la inflación argentina al comparar 6 años de historia.
- **Métricas prioritarias del primer corte:** facturación total ($) y ventas por vendedor, con cortes anual y mensual (YoY y MoM).

**Why:** la base cubre desde enero 2020 (~6 años) y en pesos nominales las comparaciones YoY no tienen sentido por la inflación. Nacho confirmó que el TC viene en la base, así que conviene apoyarse en eso en lugar de pegarle a una API externa.

**How to apply:** por defecto mostrar los KPIs en USD; si en algún momento se necesita ARS, hacerlo como vista secundaria/toggle, no como vista principal.
