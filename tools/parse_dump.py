# -*- coding: utf-8 -*-
"""
Parse un fichier SavedVariables de l'addon EbonholdEchoDump et régénère
data/echoes-dump.json et data/skilltree-dump.json.

Utilisation :
    python parse_dump.py "<chemin vers EbonholdEchoDump.lua>"

Le fichier se trouve dans votre dossier WoW, par ex. :
    <WoW>\\WTF\\Account\\<COMPTE>\\SavedVariables\\EbonholdEchoDump.lua

Pré-requis : pip install slpp
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

try:
    from slpp import slpp as lua
except ImportError:
    print("Module manquant : pip install slpp")
    sys.exit(2)

raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
data = lua.decode(raw[raw.find("{"):])

perks = data.get("perks", {}) or {}
skilltree = data.get("skilltree", {}) or {}
server = data.get("server", {}) or {}
pdb = server.get("PerkDatabase", {}) or {}


def families(sid):
    e = pdb.get(sid) or pdb.get(str(sid)) or {}
    f = e.get("families")
    if isinstance(f, dict):
        f = [f[k] for k in sorted(f)]
    return ", ".join(f) if f else ""


echoes = {}
for k, v in perks.items():
    try:
        sid = int(k)
    except Exception:
        continue
    if isinstance(v, dict):
        echoes[str(sid)] = {"name": v.get("name"), "desc": v.get("desc"),
                            "quality": v.get("quality"), "family": families(sid)}

skill = {}
for k, v in skilltree.items():
    try:
        sid = int(k)
    except Exception:
        continue
    if isinstance(v, dict):
        skill[str(sid)] = {"name": v.get("name"), "desc": (v.get("desc") or "").replace("\r", ""),
                           "cost": v.get("cost"), "nodeId": v.get("nodeId"), "rank": v.get("rank")}

json.dump(echoes, open(os.path.join(DATA, "echoes-dump.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(skill, open(os.path.join(DATA, "skilltree-dump.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("echoes-dump.json: %d echoes | skilltree-dump.json: %d noeuds" % (len(echoes), len(skill)))
