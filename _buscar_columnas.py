import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.7.11;DATABASE=z_Buffer;UID=visor;PWD=visor', timeout=15)
cur = conn.cursor()

# 1. Todas las columnas de la vista vFacturas-Articulos
cur.execute("""
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'vFacturas-Articulos' ORDER BY ORDINAL_POSITION
""")
print("=== Columnas vFacturas-Articulos ===")
for r in cur.fetchall():
    print(" ", r[0])

# 2. Buscar columnas con BONIF / NETO / DESC / PRE en toda la base
cur.execute("""
SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
WHERE COLUMN_NAME LIKE '%BONIF%' OR COLUMN_NAME LIKE '%NETO%'
   OR COLUMN_NAME LIKE '%NETORI%' OR COLUMN_NAME LIKE '%_DESC%'
   OR COLUMN_NAME LIKE 'CVRF%'
ORDER BY TABLE_NAME, COLUMN_NAME
""")
print("\n=== Columnas BONIF/NETO/DESC/CVRF* en la base ===")
for r in cur.fetchall():
    print(f"  {r[0]}.{r[1]}")
conn.close()
