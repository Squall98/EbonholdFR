# -*- coding: utf-8 -*-
# Génère EbonholdFR_Data.lua — descriptions FR (noms en anglais).
# Match EXACT par description (echoes 526 + skill tree 728).
import json, re

DATA = r"../data"
OUTLUA = r"../EbonholdFR/EbonholdFR_Data.lua"

echoes = json.load(open(DATA + r"\echoes-dump.json", encoding='utf-8'))
skill = json.load(open(DATA + r"\skilltree-dump.json", encoding='utf-8'))
tr = json.load(open(DATA + r"\fr_translations.json", encoding='utf-8'))
try:
    affixes_fr = json.load(open(DATA + r"\affixes_fr.json", encoding='utf-8'))
except FileNotFoundError:
    affixes_fr = {}
try:
    affixes_dump = json.load(open(DATA + r"\affixes-dump.json", encoding='utf-8'))
except FileNotFoundError:
    affixes_dump = {}
try:
    affix_effect_fr = json.load(open(DATA + r"\affix_effect_fr.json", encoding='utf-8'))
except FileNotFoundError:
    affix_effect_fr = {}
try:
    tomes_fr = json.load(open(DATA + r"\tomes_fr.json", encoding='utf-8'))
except FileNotFoundError:
    tomes_fr = {}


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

n_affix = 0
for sid, fr in affixes_fr.items():
    if fr:
        lines.append("b[%s] = { sdesc=%s }" % (sid, lua_str(fr)))
        n_affix += 1

# table des effets d'affixes (pour les affixes gravés sur les objets)
lines.append("")
lines.append("EbonholdFR_Data.affixEffectFR = {}")
lines.append("local ae = EbonholdFR_Data.affixEffectFR")
for en, fr in affix_effect_fr.items():
    if fr:
        lines.append("ae[%s] = %s" % (lua_str(en), lua_str(fr)))

# table des descriptions COMPLÈTES d'affixes (EN -> FR) : grimoire/spellbook
lines.append("")
lines.append("EbonholdFR_Data.affixDescFR = {}")
lines.append("local ad = EbonholdFR_Data.affixDescFR")
n_ad = 0
for sid, a in affixes_dump.items():
    en = a.get("desc")
    fr = affixes_fr.get(str(sid))
    if en and fr:
        lines.append("ad[%s] = %s" % (lua_str(en), lua_str(fr)))
        n_ad += 1

# table des tomes (nom d'echo -> texte FR complet de la ligne "Use:")
lines.append("")
lines.append("EbonholdFR_Data.tomeFR = {}")
lines.append("local tm = EbonholdFR_Data.tomeFR")
for name, fr in tomes_fr.items():
    if fr:
        lines.append("tm[%s] = %s" % (lua_str(name), lua_str(fr)))

open(OUTLUA, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("Echoes:%d/%d | Skill tree:%d/%d | Affixes:%d/%d | AffixEffect:%d | Tomes:%d"
      % (n_echo, len(echoes), n_skill, len(skill), n_affix, len(affixes_fr),
         len(affix_effect_fr), len(tomes_fr)))
