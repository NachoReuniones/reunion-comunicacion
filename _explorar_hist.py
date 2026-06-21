import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.7.11;DATABASE=z_Buffer;UID=visor;PWD=visor', timeout=15)
cur = conn.cursor()

# Columnas de vHIST_Comp
cur.execute("""
SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'vHIST_Comp' ORDER BY ORDINAL_POSITION
""")
print("=== Columnas vHIST_Comp ===")
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]})")

# Sample factura 174 Farmacity en vHIST_Comp
print("\n=== Factura FC4 174 en vHIST_Comp ===")
try:
    cur.execute("SELECT TOP 5 * FROM [dbo].[vHIST_Comp] WHERE CVCL_NUMERO_CVCL = 174 AND CVCL_TIPO_VAR = 'FC4'")
    cols = [c[0] for c in cur.description]
    for row in cur.fetchall():
        print("---")
        for c, v in zip(cols, row):
            print(f"  {c} = {v}")
except Exception as e:
    print("Error:", e)
conn.close()
