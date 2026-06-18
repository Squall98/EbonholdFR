# -*- coding: utf-8 -*-
# Génère EbonholdFR_Data.lua — descriptions FR (noms en anglais).
# Match EXACT par description (echoes 526 + skill tree 728).
import json, re

import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
DATA = os.path.join(_ROOT, "data")
OUTLUA = os.path.join(_ROOT, "EbonholdFR", "EbonholdFR_Data.lua")


echoes = json.load(open(os.path.join(DATA, "echoes-dump.json"), encoding='utf-8'))
skill = json.load(open(os.path.join(DATA, "skilltree-dump.json"), encoding='utf-8'))
tr = json.load(open(os.path.join(DATA, "fr_translations.json"), encoding='utf-8'))


def norm(s):
    s = (s or "").replace("\\r", " ").replace("\\n", " ").replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", s).strip()


DESCS = {norm(k): v for k, v in tr.get("descs", {}).items()}


def lua_str(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", "\\n")
    return '"' + s + '"'


lines = ["-- EbonholdFR_Data.lua — GÉNÉRÉ (source: data/fr_translations.json)",
         "EbonholdFR_Data = { byId = {} }", "local b = EbonholdFR_Data.byId", ""]

n_echo = n_skill = 0
for sid, e in echoes.items():
    fr = DESCS.get(norm(e.get('desc')))
    if fr:
        lines.append("b[%s] = { desc=%s }" % (sid, lua_str(fr)))
        n_echo += 1
for sid, e in skill.items():
    fr = DESCS.get(norm(e.get('desc')))
    if fr:
        lines.append("b[%s] = { sdesc=%s }" % (sid, lua_str(fr)))
        n_skill += 1

open(OUTLUA, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("Echoes:%d/%d | Skill tree:%d/%d" % (n_echo, len(echoes), n_skill, len(skill)))
