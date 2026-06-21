"""
Servidor local para reuniones de ventas Luctron.
Uso:  python servidor_reunion.py
Luego abrir http://localhost:8765 en el browser.
"""
import http.server
import socketserver
import json
import os
import datetime
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
PARENT = ROOT.parent  # carpeta CLAUDE (donde vive ventas_data_v5.json)
DATA_DIR = ROOT / "data"
REUNIONES_DIR = ROOT / "reuniones"
HTML_FILE = ROOT / "reunion_ventas.html"
# Usar el mismo archivo de datos que el dashboard de ventas
DATA_FILE = PARENT / "ventas_data_v5.json"
TC_FILE   = PARENT / "tc_bna.json"   # tipo de cambio BNA oficial por fecha
REFRESH_TS = DATA_DIR / "ultimo_refresh.txt"
TARGETS_FILE = DATA_DIR / "targets.json"

PORT = 8765

# Mapeo carpeta -> nombre completo y vendor_id en DB
VENDEDORES = {
    "facundo_oroza": "FACUNDO OROZA",
    "federico_caffarelli": "FEDERICO CAFFARELLI",
    "lucas_luna": "LUCAS LUNA",
    "inx2_nacho": "INX2 ILUMINACION SA",
}
# Para reuniones de equipo se usa la clave "equipo"
EQUIPO_KEY = "equipo"

def ahora_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Mismas dos bases que el dashboard de ventas
# z_Buffer  = historico hasta may-2026  -> dbLuctron
# z_Bufer2  = desde jun-2026 en adelante -> LuctronDB2026
# Usar '20260601' sin guiones (formato YYYYMMDD, inequivoco con locale espanol)
DATABASES = [
    ("z_Buffer",  "CVCL_FECHA_EMI < '20260601'",  "dbLuctron"),
    ("z_Bufer2",  "CVCL_FECHA_EMI >= '20260601'", "LuctronDB2026"),
]

QUERY_TEMPLATE = """
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

def actualizar_tc_bna():
    """Descarga el dolar BNA oficial (venta) de Ambito para fechas faltantes.
    Solo pide a la API los dias que no estan en tc_bna.json todavia."""
    import urllib.request as ur
    tc = {}
    if TC_FILE.exists():
        tc = json.loads(TC_FILE.read_text(encoding="utf-8"))
    hoy = datetime.date.today()
    # Determinar desde cuando bajar (ultimo dia conocido + 1)
    if tc:
        ultimo = max(tc.keys())
        desde = (datetime.date.fromisoformat(ultimo) + datetime.timedelta(days=1))
    else:
        desde = datetime.date(2020, 1, 1)
    if desde > hoy:
        return len(tc)  # ya esta al dia
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
    # Bajar en bloques anuales para no sobrecargar
    import time as _time
    año_inicio = desde.year
    año_fin    = hoy.year
    for año in range(año_inicio, año_fin + 1):
        d_desde = max(desde, datetime.date(año, 1, 1)).isoformat()
        d_hasta = min(hoy,   datetime.date(año, 12, 31)).isoformat()
        chunk = fetch_chunk(d_desde, d_hasta)
        tc.update(chunk)
        _time.sleep(0.3)
    TC_FILE.write_text(json.dumps(tc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(tc)

def refrescar_datos_sql():
    """Re-baja datos NETOS desde vIngreso-Ventas.
    Consulta ambas bases (z_Buffer hasta may-2026 + z_Bufer2 desde jun-2026).
    Ademas captura NC de cabecera (sin renglones de articulos) via CCOB_CTEC,
    que vIngreso-Ventas ignora por usar INNER JOIN con VENT_CVRF."""
    import pyodbc
    data = []
    for db_name, date_filter, db_luctron in DATABASES:
        conn = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER=192.168.7.11;DATABASE={db_name};UID=visor;PWD=visor",
            timeout=60)
        try:
            cur = conn.cursor()
            # --- Query principal: facturas y NC con renglones de articulos ---
            cur.execute(QUERY_TEMPLATE.format(date_filter=date_filter))
            rows = cur.fetchall()
            for r in rows:
                fe = r[0]
                total = float(r[6]) if r[6] is not None else 0.0
                cant  = float(r[7]) if r[7] is not None else 0.0
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
            # --- Query suplementaria: NC de cabecera sin renglones de articulos ---
            # Estas NC tienen tipo_var LIKE 'N%' y no tienen filas en VENT_CVRF.
            # El importe se obtiene de CCOB_CTEC (CTEC_IMP_TOT_LOC).
            # Signo 'H' en CCOB_CTEC => el monto es un credito (negativo para ventas).
            cur.execute(f"""
                SELECT
                    cv.CVCL_FECHA_EMI,
                    cv.CVCL_TIPO_VAR,
                    cv.CVCL_NUMERO_CVCL,
                    cl.CLIE_NOMBRE,
                    vend.VEND_NOMBRE,
                    ctec.CTEC_MONEDA,
                    ctec.CTEC_IMP_TOT_LOC,
                    ctec.CTEC_SIGNO
                FROM {db_luctron}.dbo.CCOB_CVCL cv
                INNER JOIN {db_luctron}.dbo.CCOB_CLIE cl
                    ON cv.CVCL_CLIENTE = cl.CLIE_CLIENTE
                INNER JOIN {db_luctron}.dbo.CCOB_CVCC cvcc
                    ON  cv.CVCL_NUMERO_CVCL   = cvcc.CVCC_NUMERO_CVCL
                    AND cv.CVCL_TIPO_VAR       = cvcc.CVCC_TIPO_CVCL
                    AND cv.CVCL_SUCURSAL_IMP   = cvcc.CVCC_SUCURSAL_CVCL
                    AND cv.CVCL_DIVISION_CVCL  = cvcc.CVCC_DIVISION_CVCL
                INNER JOIN {db_luctron}.dbo.CCOB_CTEC ctec
                    ON cvcc.CVCC_CTACTE_CTEC = ctec.CTEC_CTACTE_CTEC
                INNER JOIN {db_luctron}.dbo.CCOB_ECTC ectc
                    ON ctec.CTEC_CTACTE_CTEC = ectc.ECTC_CTACTE_CTEC
                INNER JOIN {db_luctron}.dbo.SIST_VEND vend
                    ON ectc.ECTC_VENDEDOR = vend.VEND_VENDEDOR
                WHERE cv.CVCL_TIPO_VAR LIKE 'N%'
                  AND YEAR(cv.CVCL_FECHA_EMI) >= 2020
                  AND {date_filter.replace('CVCL_FECHA_EMI', 'cv.CVCL_FECHA_EMI')}
                  AND ctec.CTEC_IMP_TOT_LOC <> 0
                  AND NOT EXISTS (
                      SELECT 1 FROM {db_luctron}.dbo.VENT_CVRF cvrf
                      WHERE cvrf.CVRF_NUMERO_CVCL  = cv.CVCL_NUMERO_CVCL
                        AND cvrf.CVRF_TIPO_CVCL     = cv.CVCL_TIPO_VAR
                        AND cvrf.CVRF_SUCURSAL_CVCL = cv.CVCL_SUCURSAL_IMP
                        AND cvrf.CVRF_DIVISION_CVCL = cv.CVCL_DIVISION_CVCL
                  )
            """)
            for r in cur.fetchall():
                fe   = r[0]
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
        finally:
            conn.close()
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    with open(REFRESH_TS, "w", encoding="utf-8") as f:
        f.write(ahora_str())
    # Actualizar TC BNA al mismo tiempo
    try:
        actualizar_tc_bna()
    except Exception:
        pass
    return len(data)


def listar_reuniones(vendor_key):
    """Lista archivos .md de un vendedor o equipo, ordenados por fecha (más nueva primero)."""
    folder = REUNIONES_DIR / vendor_key
    folder.mkdir(parents=True, exist_ok=True)
    files = sorted([f.name for f in folder.glob("*.md")], reverse=True)
    return files


def leer_reunion(vendor_key, filename):
    folder = REUNIONES_DIR / vendor_key
    safe = "".join(c for c in filename if c.isalnum() or c in "-_.")
    p = folder / safe
    if not p.exists() or not p.is_file():
        return None
    return p.read_text(encoding="utf-8")


def cargar_targets():
    if not TARGETS_FILE.exists():
        return {
            "equipo_mensual_usd": 175000,
            "vendedores": {k: {"mensual_usd": 0, "comentario": ""} for k in VENDEDORES}
        }
    return json.loads(TARGETS_FILE.read_text(encoding="utf-8"))


def guardar_targets(payload):
    TARGETS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def guardar_reunion(vendor_key, payload):
    """Guarda una reunión nueva como .md. vendor_key puede ser 'equipo' o un vendedor."""
    folder = REUNIONES_DIR / vendor_key
    folder.mkdir(parents=True, exist_ok=True)
    fecha = payload.get("fecha") or datetime.date.today().isoformat()
    safe_fecha = "".join(c for c in fecha if c.isalnum() or c == "-")
    filename = f"{safe_fecha}.md"
    p = folder / filename
    # Si existe, agregar sufijo HHMMSS
    if p.exists():
        ts = datetime.datetime.now().strftime("%H%M%S")
        filename = f"{safe_fecha}_{ts}.md"
        p = folder / filename
    contenido = render_reunion_md(vendor_key, payload)
    p.write_text(contenido, encoding="utf-8")
    return filename


def render_reunion_md(vendor_key, payload):
    if vendor_key == EQUIPO_KEY:
        nombre = "Equipo de Ventas (Facundo + Federico + Lucas)"
    else:
        nombre = VENDEDORES.get(vendor_key, vendor_key)
    fecha = payload.get("fecha") or datetime.date.today().isoformat()
    kpis = payload.get("kpis", {})
    notas = payload.get("notas", "")
    proximos_pasos = payload.get("proximosPasos", "")
    alertas = payload.get("alertas", [])
    lines = [
        f"# Reunión — {nombre}",
        f"**Fecha:** {fecha}",
        f"**Guardado:** {ahora_str()}",
        "",
        "## KPIs al momento de la reunión",
    ]
    for k, v in kpis.items():
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    if alertas:
        lines.append("## Alertas detectadas")
        for a in alertas:
            lines.append(f"- ⚠️ {a}")
        lines.append("")
    lines.append("## Notas")
    lines.append(notas or "_(sin notas)_")
    lines.append("")
    lines.append("## Próximos pasos / compromisos")
    lines.append(proximos_pasos or "_(sin definir)_")
    lines.append("")
    return "\n".join(lines)


class Handler(http.server.SimpleHTTPRequestHandler):
    def _json(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def _text(self, code, body, ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.wfile.write(body)

    def do_GET(self):
        try:
            path = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(path.query)
            p = path.path

            if p in ("/", "/index.html"):
                self._text(200, HTML_FILE.read_text(encoding="utf-8"),
                           ctype="text/html; charset=utf-8")
                return

            if p == "/api/data":
                if not DATA_FILE.exists():
                    self._json(200, {"ok": False, "data": [], "ts": None,
                                     "msg": "Datos aún no cargados. Tocá 'Actualizar'."})
                    return
                ts = REFRESH_TS.read_text(encoding="utf-8") if REFRESH_TS.exists() else "?"
                data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                self._json(200, {"ok": True, "data": data, "ts": ts, "n": len(data)})
                return

            if p == "/api/reuniones":
                vk = qs.get("vendor", [""])[0]
                if vk not in VENDEDORES and vk != EQUIPO_KEY:
                    self._json(400, {"ok": False, "msg": "vendor inválido"})
                    return
                self._json(200, {"ok": True, "files": listar_reuniones(vk)})
                return

            if p == "/api/reunion":
                vk = qs.get("vendor", [""])[0]
                fn = qs.get("file", [""])[0]
                if vk not in VENDEDORES and vk != EQUIPO_KEY:
                    self._json(400, {"ok": False, "msg": "vendor inválido"})
                    return
                contenido = leer_reunion(vk, fn)
                if contenido is None:
                    self._json(404, {"ok": False, "msg": "no encontrado"})
                    return
                self._json(200, {"ok": True, "contenido": contenido})
                return

            if p == "/api/targets":
                self._json(200, {"ok": True, "targets": cargar_targets()})
                return

            if p == "/api/tc":
                if not TC_FILE.exists():
                    self._json(200, {})
                    return
                self._text(200, TC_FILE.read_text(encoding="utf-8"),
                           ctype="application/json; charset=utf-8")
                return

            if p == "/api/hubspot":
                hs_file = DATA_DIR / "hubspot_pipeline.json"
                if not hs_file.exists():
                    self._json(200, {"ok": False, "msg": "Sin snapshot HubSpot"})
                    return
                self._text(200, hs_file.read_text(encoding="utf-8"),
                           ctype="application/json; charset=utf-8")
                return

            if p == "/api/eventos":
                ev_file = ROOT / "eventos.json"
                if not ev_file.exists():
                    self._json(200, [])
                    return
                self._text(200, ev_file.read_text(encoding="utf-8"),
                           ctype="application/json; charset=utf-8")
                return

            if p == "/api/estado":
                estado_file = DATA_DIR / "estado_reunion.json"
                if not estado_file.exists():
                    self._json(200, {})
                    return
                self._text(200, estado_file.read_text(encoding="utf-8"),
                           ctype="application/json; charset=utf-8")
                return

            self._text(404, "Not found")
        except Exception as e:
            self._json(500, {"ok": False, "msg": str(e)})

    def do_POST(self):
        try:
            path = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(path.query)
            p = path.path
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                body = json.loads(raw) if raw else {}
            except Exception:
                body = {}

            if p == "/api/refresh":
                try:
                    n = refrescar_datos_sql()
                    self._json(200, {"ok": True, "n": n, "ts": ahora_str(),
                                     "msg": f"OK · {n} filas refrescadas"})
                except Exception as e:
                    self._json(500, {"ok": False, "msg": f"Error SQL: {e}"})
                return

            if p == "/api/guardar":
                vk = qs.get("vendor", [""])[0]
                if vk not in VENDEDORES and vk != EQUIPO_KEY:
                    self._json(400, {"ok": False, "msg": "vendor inválido"})
                    return
                filename = guardar_reunion(vk, body)
                self._json(200, {"ok": True, "filename": filename,
                                 "msg": f"Guardado · {filename}"})
                return

            if p == "/api/borrar_reuniones":
                vk = qs.get("vendor", [""])[0]
                if vk not in VENDEDORES and vk != EQUIPO_KEY:
                    self._json(400, {"ok": False, "msg": "vendor inválido"})
                    return
                files = body if isinstance(body, list) else []
                folder = REUNIONES_DIR / vk
                borrados = []
                for fn in files:
                    fn = os.path.basename(fn)
                    if not fn.endswith(".md"):
                        continue
                    fp = folder / fn
                    if fp.exists():
                        fp.unlink()
                        borrados.append(fn)
                self._json(200, {"ok": True, "borrados": borrados})
                return

            if p == "/api/targets":
                try:
                    guardar_targets(body)
                    self._json(200, {"ok": True, "msg": "Targets actualizados"})
                except Exception as e:
                    self._json(500, {"ok": False, "msg": str(e)})
                return

            if p == "/api/eventos":
                try:
                    ev_file = ROOT / "eventos.json"
                    if isinstance(body, list):
                        ev_file.write_text(json.dumps(body, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
                        self._json(200, {"ok": True, "msg": f"{len(body)} eventos guardados"})
                    else:
                        self._json(400, {"ok": False, "msg": "Se esperaba array JSON"})
                except Exception as e:
                    self._json(500, {"ok": False, "msg": str(e)})
                return

            if p == "/api/estado":
                try:
                    estado_file = DATA_DIR / "estado_reunion.json"
                    if isinstance(body, dict):
                        # Merge con estado existente para no perder datos de otras keys
                        estado = {}
                        if estado_file.exists():
                            try: estado = json.loads(estado_file.read_text(encoding="utf-8"))
                            except: estado = {}
                        estado.update(body)
                        estado_file.write_text(json.dumps(estado, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
                        self._json(200, {"ok": True})
                    else:
                        self._json(400, {"ok": False, "msg": "Se esperaba objeto JSON"})
                except Exception as e:
                    self._json(500, {"ok": False, "msg": str(e)})
                return

            self._text(404, "Not found")
        except Exception as e:
            self._json(500, {"ok": False, "msg": str(e)})

    def log_message(self, format, *args):
        # Silenciar logs de cada request, solo errores
        pass


def main():
    os.chdir(ROOT)
    DATA_DIR.mkdir(exist_ok=True)
    REUNIONES_DIR.mkdir(exist_ok=True)
    for k in VENDEDORES:
        (REUNIONES_DIR / k).mkdir(exist_ok=True)
    (REUNIONES_DIR / EQUIPO_KEY).mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Servidor de Reuniones Luctron")
    print(f"  Abrí en el browser: http://localhost:{PORT}")
    print(f"  Para frenar: Ctrl+C")
    print(f"{'='*60}\n")

    # Intentar iniciar el bot de Telegram (opcional)
    try:
        from bot_telegram import iniciar_bot
        iniciar_bot()
    except Exception as e:
        print(f"[Bot] No se pudo iniciar: {e}")

    # Auto-abrir el browser
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
