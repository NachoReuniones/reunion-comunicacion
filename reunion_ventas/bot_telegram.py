"""
Bot de Telegram para agregar temas al checklist de reuniones Luctron.

Uso:
  1. Crear bot con @BotFather en Telegram -> copiar el token
  2. Editar data/bot_config.json con el token y tu user_id de Telegram
  3. El bot se inicia automáticamente junto al servidor (servidor_reunion.py)
     También se puede correr solo: python bot_telegram.py

Comandos disponibles en el chat:
  /ayuda         — muestra esta ayuda
  /lista         — muestra los temas pendientes de todos
  /lista facundo — muestra solo los de un vendedor

Agregar temas:
  facundo: hablar de cliente ABC         -> agrega a Facundo Oroza
  equipo: revisar targets junio          -> agrega a Reunión de Equipo
  federico: seguimiento ANKA             -> agrega a Federico Caffarelli
  lucas: demo producto nuevo             -> agrega a Lucas Luna

Atajos de nombre (sin acento, sin apellido, cualquier capitalización):
  fa / fac / facundo   -> Facundo Oroza
  fe / fed / federico  -> Federico Caffarelli
  lu / luc / lucas     -> Lucas Luna
  na / nacho / inx2    -> INX2 / Nacho
  eq / equipo          -> Reunión de Equipo

Notas de voz: si tenés OpenAI configurado en bot_config.json se transcriben
automáticamente. Si no, el bot te pedirá que escribas el texto.
"""

import json
import os
import time
import threading
import urllib.request
import urllib.error
import urllib.parse
import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
DATA_DIR = ROOT / "data"
CONFIG_FILE = DATA_DIR / "bot_config.json"
ESTADO_FILE = DATA_DIR / "estado_reunion.json"

# ── Mapeo de alias -> clave interna ──────────────────────────────────────────
ALIAS_MAP = {
    # Facundo Oroza
    "fa": "facundo_oroza", "fac": "facundo_oroza", "facu": "facundo_oroza",
    "facundo": "facundo_oroza", "oroza": "facundo_oroza",
    # Federico Caffarelli
    "fe": "federico_caffarelli", "fed": "federico_caffarelli",
    "fede": "federico_caffarelli", "federico": "federico_caffarelli",
    "caffarelli": "federico_caffarelli",
    # Lucas Luna
    "lu": "lucas_luna", "luc": "lucas_luna", "lucas": "lucas_luna",
    "luna": "lucas_luna",
    # INX2 / Nacho
    "na": "inx2_nacho", "nacho": "inx2_nacho", "inx2": "inx2_nacho",
    "inx": "inx2_nacho",
    # Equipo
    "eq": "equipo", "equipo": "equipo", "team": "equipo",
}

NOMBRES = {
    "facundo_oroza":      "Facundo Oroza",
    "federico_caffarelli": "Federico Caffarelli",
    "lucas_luna":          "Lucas Luna",
    "inx2_nacho":          "INX2 / Nacho",
    "equipo":              "Reunión de Equipo",
}

_config_cache = None
_config_mtime = 0


def cargar_config():
    global _config_cache, _config_mtime
    if not CONFIG_FILE.exists():
        return None
    mtime = CONFIG_FILE.stat().st_mtime
    if mtime != _config_mtime:
        _config_cache = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        _config_mtime = mtime
    return _config_cache


def usuario_permitido(user_id):
    cfg = cargar_config()
    if not cfg:
        return False
    allowed = cfg.get("allowed_users", [])
    if not allowed:
        return True   # sin lista = todos permitidos (útil durante setup)
    return user_id in allowed


# ── Estado / checklist ───────────────────────────────────────────────────────

def leer_estado():
    if not ESTADO_FILE.exists():
        return {}
    try:
        return json.loads(ESTADO_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def guardar_estado(estado):
    DATA_DIR.mkdir(exist_ok=True)
    ESTADO_FILE.write_text(json.dumps(estado, ensure_ascii=False, indent=2),
                           encoding="utf-8")


def agregar_tema(vendor_key, texto):
    """Agrega un item al checklist del vendedor/equipo. Devuelve True si OK."""
    estado = leer_estado()
    lsKey = f"reunion_{vendor_key}"
    if lsKey not in estado:
        estado[lsKey] = {"checklist": [], "notas": "", "proximos": ""}
    checklist = estado[lsKey].get("checklist", [])
    checklist.append({"text": texto.strip(), "done": False})
    estado[lsKey]["checklist"] = checklist
    guardar_estado(estado)
    return True


def listar_temas(vendor_key=None):
    """Devuelve dict {vendor_key: [temas pendientes]}."""
    estado = leer_estado()
    resultado = {}
    keys = [vendor_key] if vendor_key else list(NOMBRES.keys())
    for k in keys:
        lsKey = f"reunion_{k}"
        items = estado.get(lsKey, {}).get("checklist", [])
        pendientes = [i["text"] for i in items if not i.get("done")]
        if pendientes:
            resultado[k] = pendientes
    return resultado


# ── Parseo de mensajes ────────────────────────────────────────────────────────

def parsear_mensaje(texto):
    """
    Intenta extraer (vendor_key, tema) de un mensaje libre.
    Formatos aceptados:
      "facundo: hablar de X"       -> colon explícito
      "facundo hablar de X"        -> primera palabra como alias
    Devuelve (vendor_key, tema) o (None, None) si no se reconoce.
    """
    texto = texto.strip()
    if not texto:
        return None, None

    # Probar con separador ":"
    if ":" in texto:
        partes = texto.split(":", 1)
        alias = partes[0].strip().lower().rstrip()
        tema = partes[1].strip()
        if alias in ALIAS_MAP and tema:
            return ALIAS_MAP[alias], tema

    # Probar primera palabra como alias
    palabras = texto.split(None, 1)
    if len(palabras) >= 2:
        alias = palabras[0].lower().rstrip(":")
        tema = palabras[1].strip()
        if alias in ALIAS_MAP and tema:
            return ALIAS_MAP[alias], tema

    return None, None


# ── Transcripción de voz (OpenAI Whisper) ────────────────────────────────────

def transcribir_voz(ogg_path):
    """Transcribe un archivo de audio usando OpenAI Whisper API."""
    cfg = cargar_config()
    api_key = (cfg or {}).get("openai_api_key", "")
    if not api_key:
        return None

    import urllib.request as ur
    import io

    audio_data = Path(ogg_path).read_bytes()
    boundary = "----TelegramBotBoundary"
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="model"\r\n\r\nwhisper-1\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="language"\r\n\r\nes\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="audio.ogg"\r\n'
        f'Content-Type: audio/ogg\r\n\r\n'
    ).encode("utf-8") + audio_data + f'\r\n--{boundary}--\r\n'.encode("utf-8")

    req = ur.Request(
        "https://api.openai.com/v1/audio/transcriptions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
    )
    try:
        resp = json.loads(ur.urlopen(req, timeout=30).read())
        return resp.get("text", "").strip()
    except Exception as e:
        print(f"[Bot] Error Whisper: {e}")
        return None


# ── Telegram API (sin librería externa) ──────────────────────────────────────

class TelegramBot:
    BASE = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token):
        self.token = token
        self._offset = 0
        self._pending_voice = {}   # chat_id -> file_id (esperando vendor)
        self._stop = threading.Event()

    def _call(self, method, **kwargs):
        url = self.BASE.format(token=self.token, method=method)
        data = json.dumps(kwargs).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            resp = urllib.request.urlopen(req, timeout=20)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"[Bot] HTTP {e.code} en {method}: {body[:200]}")
            return {"ok": False}
        except Exception as e:
            print(f"[Bot] Error en {method}: {e}")
            return {"ok": False}

    def send(self, chat_id, text, parse_mode="HTML"):
        self._call("sendMessage", chat_id=chat_id, text=text,
                   parse_mode=parse_mode)

    def get_updates(self):
        result = self._call("getUpdates", offset=self._offset,
                            timeout=30, allowed_updates=["message"])
        if not result.get("ok"):
            return []
        updates = result.get("result", [])
        if updates:
            self._offset = updates[-1]["update_id"] + 1
        return updates

    def descargar_voz(self, file_id):
        """Descarga un audio de Telegram y lo guarda como .ogg temporal."""
        info = self._call("getFile", file_id=file_id)
        if not info.get("ok"):
            return None
        file_path = info["result"]["file_path"]
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        tmp = DATA_DIR / f"voz_tmp_{int(time.time())}.ogg"
        try:
            urllib.request.urlretrieve(url, tmp)
            return str(tmp)
        except Exception as e:
            print(f"[Bot] Error descargando voz: {e}")
            return None

    def procesar_update(self, update):
        msg = update.get("message", {})
        if not msg:
            return

        chat_id = msg["chat"]["id"]
        user_id = msg.get("from", {}).get("id")
        user_name = msg.get("from", {}).get("first_name", "?")

        # Loguear el user_id para que el dueño pueda configurarlo
        cfg = cargar_config()
        allowed = (cfg or {}).get("allowed_users", [])
        if not usuario_permitido(user_id):
            print(f"[Bot] Mensaje de usuario no permitido — user_id={user_id} ({user_name})")
            print(f"[Bot] Para habilitarlo, agregá {user_id} a allowed_users en data/bot_config.json")
            self.send(chat_id, f"⛔ No tenés permiso. Tu user_id es <code>{user_id}</code>.\nPedile al admin que lo agregue al bot.")
            return
        if not allowed:
            # Sin lista configurada: avisar pero dejar pasar (modo setup)
            print(f"[Bot] ⚠️  allowed_users vacío — cualquiera puede usar el bot. user_id={user_id}")

        text = msg.get("text", "").strip()
        voice = msg.get("voice") or msg.get("audio")

        # ── Voz pendiente: el usuario acaba de mandar el vendor ──────────────
        if chat_id in self._pending_voice:
            file_id = self._pending_voice.pop(chat_id)
            alias = text.lower().strip().rstrip(":")
            vendor_key = ALIAS_MAP.get(alias)
            if not vendor_key:
                self.send(chat_id,
                    f'❓ No reconozco "<b>{text}</b>" como vendedor.\n'
                    f'Usá: facundo, federico, lucas, nacho, equipo')
                self._pending_voice[chat_id] = file_id   # volver a esperar
                return
            # Ahora sí transcribir
            ogg = self.descargar_voz(file_id)
            if not ogg:
                self.send(chat_id, "❌ No pude descargar el audio.")
                return
            self._transcribir_y_agregar(chat_id, vendor_key, ogg)
            return

        # ── Mensaje de voz ────────────────────────────────────────────────────
        if voice:
            file_id = voice["file_id"]
            cfg = cargar_config()
            tiene_whisper = bool((cfg or {}).get("openai_api_key"))

            if not tiene_whisper:
                self.send(chat_id,
                    "🎤 Recibí tu nota de voz pero no tengo configurada la clave de Whisper.\n"
                    "Escribime el tema en texto: <code>facundo: lo que dijiste</code>")
                return

            # Intentar parsear el texto que viene antes de la voz (caption)
            caption = msg.get("caption", "").strip()
            vendor_key, _ = parsear_mensaje(caption) if caption else (None, None)

            if not vendor_key:
                # Preguntar por el vendedor antes de transcribir
                self._pending_voice[chat_id] = file_id
                self.send(chat_id,
                    "🎤 Nota de voz recibida. ¿Para quién es?\n"
                    "<code>facundo</code> / <code>federico</code> / <code>lucas</code> / <code>equipo</code>")
                return

            ogg = self.descargar_voz(file_id)
            if not ogg:
                self.send(chat_id, "❌ No pude descargar el audio.")
                return
            self._transcribir_y_agregar(chat_id, vendor_key, ogg)
            return

        # ── Texto ─────────────────────────────────────────────────────────────
        if not text:
            return

        # Comandos
        if text.startswith("/"):
            self._comando(chat_id, text)
            return

        vendor_key, tema = parsear_mensaje(text)
        if not vendor_key:
            self.send(chat_id,
                "❓ No entendí. Formato:\n"
                "<code>facundo: hablar de cliente X</code>\n"
                "<code>equipo: revisar targets</code>\n\n"
                "Vendedores: facundo · federico · lucas · nacho · equipo\n"
                "Escribí /ayuda para ver todos los comandos.")
            return

        agregar_tema(vendor_key, tema)
        nombre = NOMBRES[vendor_key]
        self.send(chat_id,
            f"✅ Agregado a <b>{nombre}</b>:\n"
            f"<i>· {tema}</i>")

    def _transcribir_y_agregar(self, chat_id, vendor_key, ogg_path):
        self.send(chat_id, "⏳ Transcribiendo...")
        texto = transcribir_voz(ogg_path)
        try:
            Path(ogg_path).unlink(missing_ok=True)
        except Exception:
            pass
        if not texto:
            self.send(chat_id,
                "❌ No pude transcribir el audio. "
                "Escribí el tema manualmente: <code>facundo: lo que querías decir</code>")
            return
        vendor_key2, tema = parsear_mensaje(f"{vendor_key}: {texto}")
        if not tema:
            tema = texto   # usar la transcripción completa como tema
            vendor_key2 = vendor_key
        agregar_tema(vendor_key2, tema)
        nombre = NOMBRES[vendor_key2]
        self.send(chat_id,
            f"🎤 Transcribido y agregado a <b>{nombre}</b>:\n"
            f"<i>· {tema}</i>")

    def _comando(self, chat_id, text):
        cmd = text.split()[0].lower().split("@")[0]
        args = text.split()[1:] if len(text.split()) > 1 else []

        if cmd in ("/start", "/ayuda", "/help"):
            self.send(chat_id, AYUDA_TEXT)

        elif cmd == "/lista":
            vendor_key = None
            if args:
                alias = args[0].lower().rstrip(":")
                vendor_key = ALIAS_MAP.get(alias)

            temas = listar_temas(vendor_key)
            if not temas:
                self.send(chat_id, "📋 No hay temas pendientes.")
                return
            lineas = []
            for k, items in temas.items():
                lineas.append(f"\n<b>{NOMBRES[k]}</b>")
                for i, t in enumerate(items, 1):
                    lineas.append(f"  {i}. {t}")
            self.send(chat_id, "📋 <b>Temas pendientes:</b>" + "\n".join(lineas))

        else:
            self.send(chat_id, "❓ Comando no reconocido. Escribí /ayuda.")

    def run(self):
        print("[Bot] Telegram bot iniciado. Escuchando mensajes...")
        while not self._stop.is_set():
            try:
                updates = self.get_updates()
                for u in updates:
                    self.procesar_update(u)
            except Exception as e:
                print(f"[Bot] Error en loop: {e}")
            time.sleep(1)

    def stop(self):
        self._stop.set()


AYUDA_TEXT = """
🤖 <b>Bot de Reuniones Luctron</b>

<b>Agregar un tema:</b>
<code>facundo: hablar con cliente ABC</code>
<code>equipo: revisar targets junio</code>
<code>lucas: demo producto nuevo</code>

<b>Atajos de nombre:</b>
fa / facundo → Facundo Oroza
fe / federico → Federico Caffarelli
lu / lucas → Lucas Luna
na / nacho → INX2 / Nacho
eq / equipo → Reunión de Equipo

<b>Nota de voz:</b>
Mandá un audio y el bot pregunta para quién es,
luego transcribe automáticamente (requiere Whisper).

<b>Comandos:</b>
/lista — temas pendientes de todos
/lista facundo — solo de un vendedor
/ayuda — esta ayuda
""".strip()


# ── Inicio standalone ─────────────────────────────────────────────────────────

def iniciar_bot():
    """Inicia el bot en un thread daemon. Llamar desde servidor_reunion.py."""
    cfg = cargar_config()
    if not cfg:
        print("[Bot] No se encontró data/bot_config.json — bot de Telegram deshabilitado.")
        print("[Bot] Copiá bot_config.example.json a data/bot_config.json y configuralo.")
        return None
    token = cfg.get("telegram_token", "")
    if not token or token == "TU_TOKEN_AQUI":
        print("[Bot] Token de Telegram no configurado en data/bot_config.json — bot deshabilitado.")
        return None
    bot = TelegramBot(token)
    t = threading.Thread(target=bot.run, daemon=True, name="TelegramBot")
    t.start()
    return bot


if __name__ == "__main__":
    cfg = cargar_config()
    if not cfg:
        print("Creá el archivo data/bot_config.json antes de correr el bot.")
        print("Copiá bot_config.example.json como punto de partida.")
        raise SystemExit(1)
    token = cfg.get("telegram_token", "")
    if not token or token == "TU_TOKEN_AQUI":
        print("Configurá el token en data/bot_config.json")
        raise SystemExit(1)
    bot = TelegramBot(token)
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot detenido.")
