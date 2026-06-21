import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.7.11;DATABASE=z_Buffer;UID=visor;PWD=visor', timeout=20)
cur = conn.cursor()

# 1. Buscar columnas con DTO / DESCUENTO / BONIF / RECARGO / TOTAL en TODAS las vistas
cur.execute("""
SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
WHERE COLUMN_NAME LIKE '%DTO%' OR COLUMN_NAME LIKE '%DESCUENTO%'
   OR COLUMN_NAME LIKE '%BONIF%' OR COLUMN_NAME LIKE '%RECARGO%'
   OR COLUMN_NAME LIKE '%DESCU%' OR COLUMN_NAME LIKE '%_DTO_%'
ORDER BY TABLE_NAME, COLUMN_NAME
""")
print("=== Columnas con DTO/DESCUENTO/BONIF/RECARGO ===")
for r in cur.fetchall():
    print(f"  {r[0]}.{r[1]}")

# 2. Vistas que empiezan con vFactura o tienen 'Comp' (cabecera de comprobante)
cur.execute("""
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_NAME LIKE '%actura%' OR TABLE_NAME LIKE '%Comprob%' OR TABLE_NAME LIKE '%Cabec%'
ORDER BY TABLE_NAME
""")
print("\n=== Vistas factura/comprobante/cabecera ===")
for r in cur.fetchall():
    print(" ", r[0])

# 3. Todas las columnas que empiezan con CVCL (cabecera venta) en cualquier vista
cur.execute("""
SELECT DISTINCT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
WHERE COLUMN_NAME LIKE 'CVCL%'
ORDER BY COLUMN_NAME
""")
print("\n=== Columnas CVCL* (cabecera comprobante) ===")
for r in cur.fetchall():
    print(" ", r[0])
conn.close()
