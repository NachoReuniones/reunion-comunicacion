# Pull NETO correcto: vIngreso-Ventas.TOTAL (neto, con signo, con descuento) + vendedor de vFacturas
# Consulta ambas bases: z_Buffer (historico) + z_Bufer2 (nuevo) y concatena.
import pyodbc, json

# Corte entre bases: z_Buffer aporta hasta el 31-may-2026, z_Bufer2 desde el 1-jun-2026.
# (fecha,  filtro SQL sobre CVCL_FECHA_EMI)
# OJO: formato 'YYYYMMDD' sin guiones. El server tiene DATEFORMAT dmy (locale
# espanol) y '2026-06-01' lo lee como 6-ene-2026. '20260601' es inequivoco.
DATABASES = [
    ('z_Buffer', "CVCL_FECHA_EMI < '20260601'"),
    ('z_Bufer2', "CVCL_FECHA_EMI >= '20260601'"),
]

def build_query(date_filter):
    return f"""
    WITH ing AS (
        SELECT CVCL_FECHA_EMI fe, CVCL_TIPO_VAR tv, CVCL_NUMERO_CVCL nu,
               CLIE_NOMBRE cli, CA01_NOMBRE fam, ARTS_NOMBRE art,
               SUM(TOTAL) total, SUM(CVRF_CANT_ING) cant
        FROM [dbo].[vIngreso-Ventas]
        WHERE YEAR(CVCL_FECHA_EMI) >= 2020 AND {date_filter}
        GROUP BY CVCL_FECHA_EMI, CVCL_TIPO_VAR, CVCL_NUMERO_CVCL,
                 CLIE_NOMBRE, CA01_NOMBRE, ARTS_NOMBRE
    ),
    fac AS (
        SELECT CVCL_FECHA_EMI fe, CVCL_TIPO_VAR tv, CVCL_NUMERO_CVCL nu,
               MAX(VEND_NOMBRE) vend, MAX(CTEC_MONEDA) moneda
        FROM [dbo].[vFacturas-Articulos]
        WHERE YEAR(CVCL_FECHA_EMI) >= 2020 AND {date_filter}
        GROUP BY CVCL_FECHA_EMI, CVCL_TIPO_VAR, CVCL_NUMERO_CVCL
    )
    SELECT ing.fe, ing.tv, ing.nu, ing.cli, ing.fam, ing.art,
           ing.total, ing.cant, fac.vend, fac.moneda
    FROM ing
    LEFT JOIN fac ON ing.fe=fac.fe AND ing.tv=fac.tv AND ing.nu=fac.nu
    WHERE ing.total <> 0
"""

def _query_db(db_name, date_filter):
    conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER=192.168.7.11;DATABASE={db_name};UID=visor;PWD=visor', timeout=60)
    try:
        cur = conn.cursor()
        cur.execute(build_query(date_filter))
        return cur.fetchall()
    finally:
        conn.close()

def pull(verbose=True):
    data = []
    for db_name, date_filter in DATABASES:
        rows = _query_db(db_name, date_filter)
        if verbose:
            print(f"  {db_name}: {len(rows)} filas")
        for r in rows:
            fe = r[0]
            total = float(r[6]) if r[6] is not None else 0.0
            cant = float(r[7]) if r[7] is not None else 0.0
            # cantidad con signo segun el total (NC restan unidades)
            cant_signed = cant if total >= 0 else -abs(cant)
            data.append({
                'a': fe.year, 'm': fe.month, 'd': fe.day,
                'v': (r[8] or 'SIN ASIGNAR').strip(),
                'c': (r[3] or '').strip(),
                'p': (r[4] or '').strip(),
                'f': str(int(r[2])) if r[2] is not None else '',
                'tv': (r[1] or '').strip(),
                'mo': (r[9] or 'PS').strip(),
                't': total,   # TOTAL NETO en pesos, con signo
                'q': cant_signed
            })
    return data

if __name__ == '__main__':
    data = pull()
    out = r'C:\Users\usuario\OneDrive\Escritorio\CLAUDE\ventas_data_v5.json'
    json.dump(data, open(out,'w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
    print(f"Filas: {len(data)}")
    # Controles
    from collections import defaultdict
    by_year = defaultdict(float)
    sin_vend = 0
    for r in data:
        by_year[r['a']] += r['t']
        if r['v'] == 'SIN ASIGNAR': sin_vend += 1
    print("\n=== TOTAL NETO por año (ARS) ===")
    for y in sorted(by_year):
        print(f"  {y}: {by_year[y]:,.0f}")
    print(f"\nLineas sin vendedor asignado: {sin_vend} ({sin_vend/len(data)*100:.1f}%)")
    # Factura 174 control
    f174 = [r for r in data if r['f']=='174' and r['tv']=='FC4' and r['a']==2026]
    print(f"\nFactura FC4 174 (control): {sum(r['t'] for r in f174):,.2f} ARS (esperado 26.900.648,77)")
