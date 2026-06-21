"""
Servidor local para el Dashboard de Ventas Luctron.
Uso:  python servidor_dashboard.py  (o doble clic en INICIAR_DASHBOARD.bat)
Abre http://localhost:8766 en el browser.

El boton "Actualizar datos" del dashboard:
  1. Re-baja las facturas desde SQL Server
  2. Regenera el HTML (corre build_dashboard_v2.py)
  3. Recarga la pagina con los datos frescos
"""
import http.server
import socketserver
import json
import os
import sys
import subprocess
import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
HTML_FILE  = ROOT / "dashboard_ventas.html"
DATA_FILE  = ROOT / "ventas_data_v5.json"
TC_FILE    = ROOT / "tc_bna.json"
BUILD_SCRIPT = ROOT / "build_dashboard_v2.py"

PORT = 8766

def ahora_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Bases de datos a consultar:
#   z_Buffer  = base vieja (historico)  -> aporta hasta el 31-may-2026
#   z_Bufer2  = base nueva               -> aporta desde el 1-jun-2026
# Se separan por fecha de corte para NO duplicar el periodo en que ambas
# bases tienen registros. Los numeros de comprobante se reiniciaron desde
# cero en la base nueva, asi que el corte por fecha es lo unico confiable.
# (nombre_base,  filtro SQL sobre CVCL_FECHA_EMI)
# OJO: usar formato 'YYYYMMDD' sin guiones. El server tiene DATEFORMAT dmy
# (locale espanol) y '2026-06-01' lo interpreta como 6-ene-2026. '20260601'
# es inequivoco (siempre ano-mes-dia).
DATABASES = [
    ("z_Buffer",  "CVCL_FECHA_EMI < '20260601'",  "dbLuctron"),
    ("z_Bufer2",  "CVCL_FECHA_EMI >= '20260601'", "LuctronDB2026"),
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

NC_CABECERA_QUERY = """
    SELECT
        cv.CVCL_FECHA_EMI,
        cv.CVCL_TIPO_VAR,
        cv.CVCL_NUMERO_CVCL,
        cl.CLIE_NOMBRE,
        vend.VEND_NOMBRE,
        ctec.CTEC_MONEDA,
        ctec.CTEC_IMP_TOT_LOC,
        ctec.CTEC_SIGNO
    FROM {db}.dbo.CCOB_CVCL cv
    INNER JOIN {db}.dbo.CCOB_CLIE cl
        ON cv.CVCL_CLIENTE = cl.CLIE_CLIENTE
    INNER JOIN {db}.dbo.CCOB_CVCC cvcc
        ON  cv.CVCL_NUMERO_CVCL  = cvcc.CVCC_NUMERO_CVCL
        AND cv.CVCL_TIPO_VAR      = cvcc.CVCC_TIPO_CVCL
        AND cv.CVCL_SUCURSAL_IMP  = cvcc.CVCC_SUCURSAL_CVCL
        AND cv.CVCL_DIVISION_CVCL = cvcc.CVCC_DIVISION_CVCL
    INNER JOIN {db}.dbo.CCOB_CTEC ctec
        ON cvcc.CVCC_CTACTE_CTEC = ctec.CTEC_CTACTE_CTEC
    INNER JOIN {db}.dbo.CCOB_ECTC ectc
        ON ctec.CTEC_CTACTE_CTEC = ectc.ECTC_CTACTE_CTEC
    INNER JOIN {db}.dbo.SIST_VEND vend
        ON ectc.ECTC_VENDEDOR = vend.VEND_VENDEDOR
    WHERE cv.CVCL_TIPO_VAR LIKE 'N%'
      AND YEAR(cv.CVCL_FECHA_EMI) >= 2020
      AND {date_filter}
      AND ctec.CTEC_IMP_TOT_LOC <> 0
      AND NOT EXISTS (
          SELECT 1 FROM {db}.dbo.VENT_CVRF cvrf
          WHERE cvrf.CVRF_NUMERO_CVCL  = cv.CVCL_NUMERO_CVCL
            AND cvrf.CVRF_TIPO_CVCL     = cv.CVCL_TIPO_VAR
            AND cvrf.CVRF_SUCURSAL_CVCL = cv.CVCL_SUCURSAL_IMP
            AND cvrf.CVRF_DIVISION_CVCL = cv.CVCL_DIVISION_CVCL
      )
"""

def _query_db(db_name, date_filter, db_luctron):
    """Corre la consulta de ventas contra una base puntual y devuelve las filas crudas."""
    import pyodbc
    conn = pyodbc.connect(
        f"DRIVER={{SQL Server}};SERVER=192.168.7.11;DATABASE={db_name};UID=visor;PWD=visor",
        timeout=60)
    try:
        cur = conn.cursor()
        cur.execute(build_query(date_filter))
        return cur.fetchall()
    finally:
        conn.close()

def _query_nc_cabecera(db_name, date_filter, db_luctron):
    """Trae NC de cabecera (sin renglones de articulos) que vIngreso-Ventas ignora."""
    import pyodbc
    conn = pyodbc.connect(
        f"DRIVER={{SQL Server}};SERVER=192.168.7.11;DATABASE={db_name};UID=visor;PWD=visor",
        timeout=60)
    try:
        cur = conn.cursor()
        df = date_filter.replace('CVCL_FECHA_EMI', 'cv.CVCL_FECHA_EMI')
        cur.execute(NC_CABECERA_QUERY.format(db=db_luctron, date_filter=df))
        return cur.fetchall()
    finally:
        conn.close()

def repull_sql():
    """Re-baja datos NETOS desde vIngreso-Ventas (TOTAL ya tiene descuento y signo).
    Une con vFacturas-Articulos para traer el vendedor y la moneda del comprobante.
    Consulta ambas bases (z_Buffer hasta may-2026 + z_Bufer2 desde jun-2026) y concatena.
    Tambien captura NC de cabecera sin renglones de articulos via CCOB_CTEC."""
    data = []
    for db_name, date_filter, db_luctron in DATABASES:
        # Query principal
        rows = _query_db(db_name, date_filter, db_luctron)
        for r in rows:
            fe = r[0]
            total = float(r[6]) if r[6] is not None else 0.0
            cant = float(r[7]) if r[7] is not None else 0.0
            cant_signed = cant if total >= 0 else -abs(cant)
            data.append({
                "a": fe.year, "m": fe.month, "d": fe.day,
                "v": (r[8] or "SIN ASIGNAR").strip(),
                "c": (r[3] or "").strip(),
                "p": (r[4] or "").strip(),
                "f": str(int(r[2])) if r[2] is not None else "",
                "tv": (r[1] or "").strip(),
                "mo": (r[9] or "PS").strip(),
                "t": total,
                "q": cant_signed,
            })
        # NC de cabecera sin renglones
        for r in _query_nc_cabecera(db_name, date_filter, db_luctron):
            fe    = r[0]
            bruto = float(r[6]) if r[6] is not None else 0.0
            signo = (r[7] or '').strip()
            total = -bruto if signo == 'H' else bruto
            if total == 0:
                continue
            data.append({
                "a": fe.year, "m": fe.month, "d": fe.day,
                "v": (r[4] or "SIN ASIGNAR").strip(),
                "c": (r[3] or "").strip(),
                "p": "NC CABECERA",
                "f": str(int(r[2])) if r[2] is not None else "",
                "tv": (r[1] or "").strip(),
                "mo": (r[5] or "PS").strip(),
                "t": total,
                "q": -1.0 if total < 0 else 1.0,
            })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    return len(data)

def actualizar_tc_bna():
    """Descarga el dolar BNA oficial (venta) de Ambito para fechas faltantes."""
    import urllib.request as ur, time as _time
    tc = {}
    if TC_FILE.exists():
        tc = json.loads(TC_FILE.read_text(encoding="utf-8"))
    hoy = datetime.datetime.now().date()
    if tc:
        desde = (datetime.date.fromisoformat(max(tc.keys())) + datetime.timedelta(days=1))
    else:
        desde = datetime.date(2020, 1, 1)
    if desde > hoy:
        return len(tc)
    def fetch_chunk(d_desde, d_hasta):
        url = f"https://mercados.ambito.com/dolar/oficial/historico-general/{d_desde}/{d_hasta}"
        req = ur.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        rows = json.loads(ur.urlopen(req, timeout=20).read())
        out = {}
        for row in rows[1:]:
            try:
                d, m, a = row[0].split("/")
                fecha = f"{a}-{m}-{d}"
                venta = float(row[2].replace(",", "."))
                if fecha not in out:
                    out[fecha] = venta
            except Exception:
                pass
        return out
    for año in range(desde.year, hoy.year + 1):
        d_desde = max(desde, datetime.date(año, 1, 1)).isoformat()
        d_hasta = min(hoy,   datetime.date(año, 12, 31)).isoformat()
        tc.update(fetch_chunk(d_desde, d_hasta))
        _time.sleep(0.3)
    TC_FILE.write_text(json.dumps(tc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(tc)

def rebuild_html():
    """Corre build_dashboard_v2.py para regenerar el HTML con los datos frescos."""
    result = subprocess.run([sys.executable, str(BUILD_SCRIPT)],
                            cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[:500] or "build fallo")
    return result.stdout.strip()


class Handler(http.server.SimpleHTTPRequestHandler):
    def _json(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        if self.path in ("/", "/index.html", "/dashboard_ventas.html"):
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_FILE.read_text(encoding="utf-8").encode("utf-8"))
            except Exception as e:
                self._json(500, {"ok": False, "msg": str(e)})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/rebuild":
            try:
                n = repull_sql()
                try:
                    actualizar_tc_bna()
                except Exception:
                    pass
                out = rebuild_html()
                self._json(200, {"ok": True, "n": n, "ts": ahora_str(),
                                 "msg": f"{n} filas · {out}"})
            except Exception as e:
                self._json(500, {"ok": False, "msg": str(e)})
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *args):
        pass


def main():
    os.chdir(ROOT)
    print(f"\n{'='*58}")
    print(f"  Dashboard de Ventas Luctron")
    print(f"  Abri en el browser: http://localhost:{PORT}")
    print(f"  Para frenar: Ctrl+C")
    print(f"{'='*58}\n")
    try:
        import webbrowser
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")


if __name__ == "__main__":
    main()
