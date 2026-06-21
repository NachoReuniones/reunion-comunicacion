import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.7.11;DATABASE=z_Buffer;UID=visor;PWD=visor', timeout=15)
cur = conn.cursor()

# vIngreso-Ventas para factura 174 (Farmacity, LOEN)
print("=== vIngreso-Ventas FC4 #174 ===")
cur.execute("""
SELECT CVCL_FECHA_EMI, CVCL_TIPO_VAR, CVCL_NUMERO_CVCL, CLIE_NOMBRE, CA01_NOMBRE,
       CVRF_CANT_ING, ARTS_NOMBRE, TOTAL
FROM [dbo].[vIngreso-Ventas]
WHERE CVCL_NUMERO_CVCL = 174 AND CVCL_TIPO_VAR = 'FC4'
""")
cols = [c[0] for c in cur.description]
rows = cur.fetchall()
for row in rows:
    for c, v in zip(cols, row):
        print(f"  {c} = {v}")
    print("---")
print(f"Filas: {len(rows)}")
print("Total esperado (neto real factura): 26.900.648,77")

# Comparar el total de un mes entre los dos métodos
print("\n=== Comparación mayo 2026: bruto (actual) vs TOTAL (vIngreso) ===")
cur.execute("""
SELECT SUM(CVRF_CANT_ING*CVRF_PRE_BRUORI_SI) bruto
FROM [dbo].[vFacturas-Articulos]
WHERE YEAR(CVCL_FECHA_EMI)=2026 AND MONTH(CVCL_FECHA_EMI)=5
  AND CTEC_MONEDA='PS' AND CVCL_TIPO_VAR='FC4'
""")
print("  Bruto (vFacturas) FC4 PS mayo:", cur.fetchone()[0])
cur.execute("""
SELECT SUM(TOTAL) neto
FROM [dbo].[vIngreso-Ventas]
WHERE YEAR(CVCL_FECHA_EMI)=2026 AND MONTH(CVCL_FECHA_EMI)=5
  AND CVCL_TIPO_VAR='FC4'
""")
print("  TOTAL (vIngreso) FC4 mayo:", cur.fetchone()[0])
conn.close()
