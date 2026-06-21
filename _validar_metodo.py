import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.7.11;DATABASE=z_Buffer;UID=visor;PWD=visor', timeout=30)
cur = conn.cursor()

# 1. TOTAL por prefijo: confirmar que C* es negativo y F/P positivo (signo ya incluido)
cur.execute("""
SELECT LEFT(CVCL_TIPO_VAR,1) pref, COUNT(*) n,
       SUM(CASE WHEN TOTAL<0 THEN 1 ELSE 0 END) negativos,
       SUM(CASE WHEN TOTAL>0 THEN 1 ELSE 0 END) positivos
FROM [dbo].[vIngreso-Ventas]
WHERE YEAR(CVCL_FECHA_EMI) >= 2025
GROUP BY LEFT(CVCL_TIPO_VAR,1)
ORDER BY n DESC
""")
print("=== Signo del TOTAL por prefijo (2025+) ===")
print(f"{'Pref':<6}{'N':>7}{'Negativos':>11}{'Positivos':>11}")
for r in cur.fetchall():
    print(f"{r[0] or '?':<6}{r[1]:>7}{r[2]:>11}{r[3]:>11}")

# 2. Agrupar antes de join: 1 fila por (fecha,tipo,numero,articulo). Comparar count.
cur.execute("""
WITH ing AS (
  SELECT CVCL_FECHA_EMI f, CVCL_TIPO_VAR t, CVCL_NUMERO_CVCL n, ARTS_NOMBRE a,
         SUM(TOTAL) total, SUM(CVRF_CANT_ING) cant
  FROM [dbo].[vIngreso-Ventas]
  WHERE YEAR(CVCL_FECHA_EMI)=2026 AND MONTH(CVCL_FECHA_EMI)=5
  GROUP BY CVCL_FECHA_EMI, CVCL_TIPO_VAR, CVCL_NUMERO_CVCL, ARTS_NOMBRE
)
SELECT COUNT(*), SUM(total) FROM ing
""")
r = cur.fetchone()
print(f"\n=== Mayo 2026 agrupado por renglon-articulo ===")
print(f"Lineas unicas: {r[0]}")
print(f"TOTAL neto mayo (todos los comprobantes): {r[1]:,.2f} ARS")

# 3. Total NETO 2026 completo y comparar con metodo viejo (bruto)
cur.execute("SELECT SUM(TOTAL) FROM [dbo].[vIngreso-Ventas] WHERE YEAR(CVCL_FECHA_EMI)=2026")
neto = cur.fetchone()[0]
cur.execute("SELECT SUM(CVRF_CANT_ING*CVRF_PRE_BRUORI_SI*CASE WHEN LEFT(CVCL_TIPO_VAR,1)='C' THEN -1 ELSE 1 END) FROM [dbo].[vFacturas-Articulos] WHERE YEAR(CVCL_FECHA_EMI)=2026 AND CVRF_CANT_ING>0 AND CVRF_PRE_BRUORI_SI>0 AND CTEC_MONEDA='PS'")
bruto_ps = cur.fetchone()[0]
print(f"\n=== 2026 completo ===")
print(f"NETO (vIngreso TOTAL): {neto:,.0f} ARS")
print(f"Bruto PS (metodo viejo, solo PS): {bruto_ps:,.0f} ARS")

# 4. Verificar que vIngreso tiene los mismos tipos de comprobante que filtrabamos
cur.execute("SELECT DISTINCT CVCL_TIPO_VAR FROM [dbo].[vIngreso-Ventas] WHERE YEAR(CVCL_FECHA_EMI)=2026 ORDER BY CVCL_TIPO_VAR")
print("\n=== Tipos comprobante en vIngreso 2026 ===")
print(", ".join(r[0] for r in cur.fetchall()))
conn.close()
