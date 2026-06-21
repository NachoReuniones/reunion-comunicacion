import pyodbc
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.7.11;DATABASE=z_Buffer;UID=visor;PWD=visor', timeout=20)
cur = conn.cursor()

# Explorar vCuentas, vCobranzas, vCuenPag - buscar total por comprobante
for vista in ['vCuentas','vCobranzas','vCuenPag']:
    try:
        cur.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{vista}' ORDER BY ORDINAL_POSITION")
        cols = cur.fetchall()
        print(f"=== {vista} ===")
        for c in cols:
            print(f"  {c[0]} ({c[1]})")
        print()
    except Exception as e:
        print(f"{vista}: error {e}\n")
conn.close()
