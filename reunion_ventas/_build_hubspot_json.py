import json, os
from datetime import datetime, timezone
from collections import defaultdict

STAGES = {
    "1314050142":"Aliados Comerciales","1173043482":"Recurrente",
    "1084486562":"Pendiente calif","1084486563":"Calificado","1084486564":"No calificado",
    "1084495160":"Descubrimiento","1084495162":"Estudio Luminico","1084495163":"Pendiente Cotizar",
    "1084495164":"Cotizado Negociando","1084495165":"Detenido",
    "1084495166":"Cierre Ganado","1084706394":"Cierre Perdido"
}
OWNER_TO_KEY = {"56594717":"inx2_nacho","80394108":"federico_caffarelli",
                "138774886":"facundo_oroza","79867010":"lucas_luna",
                "58987758":"grisel_fernandez","82060157":"jessica_escobar"}

def normalize_deal(d):
    p = d.get("properties", {})
    amt = float(p.get("amount") or 0)
    is_outlier = amt > 500000
    return {
        "id": d.get("id"),
        "name": p.get("dealname",""),
        "stage_id": p.get("dealstage",""),
        "stage": STAGES.get(p.get("dealstage",""), p.get("dealstage","")),
        "amount": amt if not is_outlier else 0,
        "amount_raw": amt,
        "outlier": is_outlier,
        "currency": p.get("deal_currency_code") or "USD",
        "owner_id": p.get("hubspot_owner_id",""),
        "owner_key": OWNER_TO_KEY.get(p.get("hubspot_owner_id",""), "otro"),
        "created": p.get("createdate",""),
        "modified": p.get("hs_lastmodifieddate",""),
        "closedate": p.get("closedate","")
    }

# 1. Open deals existentes
existing = json.load(open(r"C:\Users\usuario\OneDrive\Escritorio\CLAUDE\reunion_ventas\data\hubspot_pipeline.json","r",encoding="utf-8"))
open_deals = []
for d in existing.get("deals", []):
    owner_id = d.get("owner_id","")
    d["owner_key"] = OWNER_TO_KEY.get(owner_id, "otro")
    if "amount_raw" not in d:
        d["amount_raw"] = d.get("amount", 0)
        d["outlier"] = d["amount_raw"] > 500000
        if d["outlier"]:
            d["amount"] = 0
    open_deals.append(d)
print(f"Open: {len(open_deals)}")

# Win/Loss counts conocidos (de las queries por owner)
won_by_owner = {
    "facundo_oroza": {"count": 20, "name": "Facundo Oroza", "owner_id": "138774886"},
    "federico_caffarelli": {"count": 69, "name": "Federico Caffarelli", "owner_id": "80394108"},
    "lucas_luna": {"count": 42, "name": "Lucas Luna", "owner_id": "79867010"},
    "inx2_nacho": {"count": 0, "name": "INX2 / Nacho", "owner_id": "56594717"}
}
lost_counts = {"facundo_oroza": 24, "federico_caffarelli": 61, "lucas_luna": 81, "inx2_nacho": 0}
for k in won_by_owner:
    w, l = won_by_owner[k]["count"], lost_counts.get(k, 0)
    won_by_owner[k]["lost"] = l
    won_by_owner[k]["win_rate"] = round(w/(w+l)*100, 1) if (w+l) > 0 else None

# Stats por owner del pipeline activo
now = datetime.now(timezone.utc)
def days_since(iso):
    if not iso: return None
    try:
        return (now - datetime.fromisoformat(iso.replace("Z","+00:00"))).days
    except Exception:
        return None

stats_by_owner = {}
def empty_stats():
    return {"open_count":0,"open_amount":0,"by_stage":{},"caliente":[],"estancado":[],"detenido_count":0,"detenido_amount":0}

for d in open_deals:
    k = d["owner_key"]
    if k not in stats_by_owner:
        stats_by_owner[k] = empty_stats()
    s = stats_by_owner[k]
    s["open_count"] += 1
    s["open_amount"] += d["amount"]
    stage = d["stage"]
    if stage not in s["by_stage"]:
        s["by_stage"][stage] = {"count":0,"amount":0}
    s["by_stage"][stage]["count"] += 1
    s["by_stage"][stage]["amount"] += d["amount"]
    if stage == "Detenido":
        s["detenido_count"] += 1
        s["detenido_amount"] += d["amount"]
    if stage == "Cotizado Negociando" and d["amount"] > 0:
        s["caliente"].append({
            "id": d["id"], "name": d["name"], "amount": d["amount"],
            "modified": d["modified"], "days_inactive": days_since(d["modified"])
        })
    ds = days_since(d["modified"])
    if ds is not None and ds >= 30 and stage not in ("Detenido","Cierre Ganado","Cierre Perdido"):
        s["estancado"].append({
            "id": d["id"], "name": d["name"], "amount": d["amount"],
            "stage": stage, "days_inactive": ds
        })

for k, s in stats_by_owner.items():
    s["caliente"] = sorted(s["caliente"], key=lambda x: -x["amount"])[:5]
    s["estancado"] = sorted(s["estancado"], key=lambda x: -x["days_inactive"])[:5]

# Team stats (3 vendedores activos)
EQUIPO = ["facundo_oroza","federico_caffarelli","lucas_luna"]
team_stats = {
    "open_count": sum(stats_by_owner.get(k,{}).get("open_count",0) for k in EQUIPO),
    "open_amount": sum(stats_by_owner.get(k,{}).get("open_amount",0) for k in EQUIPO),
    "by_stage_global": {}
}
for stage_id, label in STAGES.items():
    cnt = sum(stats_by_owner.get(k,{}).get("by_stage",{}).get(label,{}).get("count",0) for k in EQUIPO)
    amt = sum(stats_by_owner.get(k,{}).get("by_stage",{}).get(label,{}).get("amount",0) for k in EQUIPO)
    if cnt > 0:
        team_stats["by_stage_global"][label] = {"count": cnt, "amount": amt}

final = {
    "updated": now.strftime("%Y-%m-%d %H:%M:%S"),
    "open_deals_total": existing.get("total", 254),
    "open_deals_in_data": len(open_deals),
    "open_deals": open_deals,
    "stats_by_owner": stats_by_owner,
    "win_loss_ytd": won_by_owner,
    "team_stats": team_stats
}

output = r"C:\Users\usuario\OneDrive\Escritorio\CLAUDE\reunion_ventas\data\hubspot_pipeline.json"
with open(output, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, separators=(",",":"))

tmp = r"C:\Users\usuario\OneDrive\Escritorio\CLAUDE\reunion_ventas\data\_won_temp.json"
if os.path.exists(tmp):
    os.remove(tmp)

print(f"\nGuardado: {output}")
print(f"\n=== Stats por owner ===")
for k, s in stats_by_owner.items():
    print(f"\n  {k}: {s['open_count']} abiertos, ${s['open_amount']:,.0f} pipeline")
    print(f"    Caliente: {len(s['caliente'])}, Estancados: {len(s['estancado'])}, Detenidos: {s['detenido_count']}")
    if k in won_by_owner:
        w = won_by_owner[k]
        print(f"    Win rate YTD: {w['win_rate']}% ({w['count']}W/{w['lost']}L)")

print(f"\n=== Team ===")
print(f"  {team_stats['open_count']} deals activos, ${team_stats['open_amount']:,.0f} pipeline equipo")
