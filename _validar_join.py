import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.7.11;DATABASE=z_Buffer;UID=visor;PWD=visor', timeout=20)
cur = conn.cursor()

# 1. Ver columnas exactas de vIngreso-Ventas
cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='vIngreso-Ventas' ORDER BY ORDINAL_POSITION")
print("=== Columnas vIngreso-Ventas ===")
for r in cur.fetchall():
    print(" ", r[0])

# 2. Una factura DL: ver si TOTAL esta en USD o pesos
print("\n=== Factura DL ejemplo (Arpec FE4) en vIngreso vs vFacturas ===")
cur.execute("""
SELECT TOP 3 i.CVCL_TIPO_VAR, i.CVCL_NUMERO_CVCL, i.ARTS_NOMBRE, i.CVRF_CANT_ING, i.TOTAL,
       f.CVRF_PRE_BRUORI_SI, f.CTEC_MONEDA, f.VEND_NOMBRE
FROM [dbo].[vIngreso-Ventas] i
INNER JOIN [dbo].[vFacturas-Articulos] f
  ON i.CVCL_FECHA_EMI=f.CVCL_FECHA_EMI AND i.CVCL_TIPO_VAR=f.CVCL_TIPO_VAR
  AND i.CVCL_NUMERO_CVCL=f.CVCL_NUMERO_CVCL AND i.ARTS_NOMBRE=f.ARTS_NOMBRE
WHERE f.CTEC_MONEDA='DL' AND YEAR(i.CVCL_FECHA_EMI)=2026
""")
cols=[c[0] for c in cur.description]
for row in cur.fetchall():
    print("  ", dict(zip(cols,row)))

# 3. Verificar si el JOIN duplica filas: contar lineas en cada vista para mayo 2026
cur.execute("SELECT COUNT(*) FROM [dbo].[vFacturas-Articulos] WHERE YEAR(CVCL_FECHA_EMI)=2026 AND MONTH(CVCL_FECHA_EMI)=5")
print("\nLineas vFacturas mayo:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM [dbo].[vIngreso-Ventas] WHERE YEAR(CVCL_FECHA_EMI)=2026 AND MONTH(CVCL_FECHA_EMI)=5")
print("Lineas vIngreso mayo:", cur.fetchone()[0])
cur.execute("""
SELECT COUNT(*) FROM [dbo].[vIngreso-Ventas] i
INNER JOIN [dbo].[vFacturas-Articulos] f
  ON i.CVCL_FECHA_EMI=f.CVCL_FECHA_EMI AND i.CVCL_TIPO_VAR=f.CVCL_TIPO_VAR
  AND i.CVCL_NUMERO_CVCL=f.CVCL_NUMERO_CVCL AND i.ARTS_NOMBRE=f.ARTS_NOMBRE
WHERE YEAR(i.CVCL_FECHA_EMI)=2026 AND MONTH(i.CVCL_FECHA_EMI)=5
""")
print("Lineas JOIN mayo:", cur.fetchone()[0], "(si es mayor que vIngreso, el join duplica)")
conn.close()
