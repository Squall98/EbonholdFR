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

# ---------------------------------------------------------------------------
# ECHOES À CONTENU DYNAMIQUE PAR CLASSE
# Chaque variante de classe est un spellId distinct (texte propre). Le serveur
# n'affiche QUE la variante canonique (Guerrier) dans la carte d'offre, pour
# toutes les classes. On indexe donc les variantes FR par classe pour que
# l'addon affiche la bonne au runtime (UnitClass("player")).
# ---------------------------------------------------------------------------
DYN_ECHOES = {"Temporal Pressure", "Corrosive Breath", "Unstable Infusion",
              "Ember Spark", "Stonefist Barrage", "Arcane Bombardment"}

# sorts-signatures par classe (présents dans le texte EN des variantes)
CLASS_SIG = {
    "WARRIOR": ["Mortal Strike", "Bloodthirst", "Shield Slam", "Thunder Clap",
                "Whirlwind", "Revenge", "Shockwave", "applies Rend",
                "cast a melee ability"],
    "PALADIN": ["Crusader Strike", "Hammer of the Righteous", "Holy Shock",
                "Consecration", "Divine Storm", "Shield of Righteousness",
                "Avenger's Shield", "cast Judgement"],
    "HUNTER": ["Auto Shot", "Arcane Shot", "Aimed Shot", "Explosive Shot",
               "Chimera Shot", "Raptor Strike", "Multi-Shot", "Serpent Sting"],
    "ROGUE": ["Mutilate", "Sinister Strike", "Hemorrhage", "Fan of Knives",
              "Blade Flurry", "Ghostly Strike", "Garrote", "finishing move",
              "combo point"],
    "PRIEST": ["Smite", "Flash Heal", "Greater Heal", "Mind Blast", "Holy Nova",
               "Mind Sear", "Shadow Word", "Renew", "Holy Fire", "Vampiric Touch"],
    "DEATHKNIGHT": ["Death Strike", "Heart Strike", "Obliterate", "Scourge Strike",
                    "Blood Boil", "Howling Blast", "Icy Touch", "Death and Decay",
                    "Runic Power", "spend a Rune", "Blood Plague", "Frost Fever"],
    "SHAMAN": ["Lightning Bolt", "Chain Lightning", "Healing Wave", "Chain Heal",
               "Thunderstorm", "Stormstrike", "Earth Shock", "Flame Shock",
               "Frost Shock"],
    "MAGE": ["Arcane Blast", "Fireball", "Frostbolt", "Frostfire Bolt",
             "Cone of Cold", "Arcane Explosion", "Frost Nova", "Dragon's Breath",
             "critical strikes have a chance to launch a missile"],
    "WARLOCK": ["Warlock", "Immolate", "Corruption", "Curse of Agony",
                "Shadowflame", "Shadowfury", "Drain Life"],
    "DRUID": ["Starfire", "Nourish", "Mangle", "Wrath", "Regrowth", "Shred",
              "Maul", "Typhoon", "Swipe", "Swiftmend", "Hurricane", "Moonfire",
              "Rake", "Lacerate"],
}

# Ember Spark n'a pas de noms de sorts (que des ressources) -> classe -> ressource
RESOURCE_OF_CLASS = {
    "WARRIOR": "rage", "DEATHKNIGHT": "runic", "ROGUE": "energy",
    "MAGE": "mana", "WARLOCK": "mana", "PRIEST": "mana", "PALADIN": "mana",
    "HUNTER": "mana", "SHAMAN": "mana", "DRUID": "mana",
}


def classify_class(en):
    """retourne le token de classe (MAGE, WARRIOR, ...) le mieux matché, ou None."""
    best, score = None, 0
    for cls, sigs in CLASS_SIG.items():
        c = sum(1 for s in sigs if s in en)
        if c > score:
            best, score = cls, c
    return best


def ember_resource(en):
    low = en.lower()
    if "runic power" in low:
        return "runic"
    if "energy you spend" in low:
        return "energy"
    if "rage you spend" in low:
        return "rage"
    if "mana you spend" in low or "per level) you spend" in low:
        return "mana"
    return None  # variante générique "Rage, Energy, or Mana"


# accumulateur : nom d'echo -> liste (en, fr)
dyn_variants = {n: [] for n in DYN_ECHOES}


def lua_str(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", "\\n")
    return '"' + s + '"'


lines = ["-- EbonholdFR_Data.lua — GÉNÉRÉ (source: data/fr_translations.json)",
         "EbonholdFR_Data = { byId = {} }", "local b = EbonholdFR_Data.byId", ""]

n_echo = n_skill = 0
for sid, e in echoes.items():
    fr = DESCS.get(norm(e.get('desc')))
    if fr:
        name = e.get('name')
        if name in DYN_ECHOES:
            lines.append("b[%s] = { desc=%s, dyn=%s }" % (sid, lua_str(fr), lua_str(name)))
            dyn_variants[name].append((e.get('desc') or "", fr))
        else:
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

# table dynFR : echo dynamique -> { CLASSE = texte FR de la variante }
lines.append("")
lines.append("EbonholdFR_Data.dynFR = {}")
lines.append("local dn = EbonholdFR_Data.dynFR")
dyn_report = {}
for name, variants in dyn_variants.items():
    by_class = {}
    if name == "Ember Spark":
        # indexe les FR par ressource, puis mappe chaque classe vers sa ressource
        by_res = {}
        for en, fr in variants:
            r = ember_resource(en)
            if r and r not in by_res:
                by_res[r] = fr
        for cls, res in RESOURCE_OF_CLASS.items():
            if res in by_res:
                by_class[cls] = by_res[res]
    else:
        for en, fr in variants:
            cls = classify_class(en)
            if cls and cls not in by_class:
                by_class[cls] = fr
    if by_class:
        inner = ", ".join("%s=%s" % (cls, lua_str(fr)) for cls, fr in sorted(by_class.items()))
        lines.append("dn[%s] = { %s }" % (lua_str(name), inner))
    dyn_report[name] = sorted(by_class.keys())

open(OUTLUA, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("Echoes:%d/%d | Skill tree:%d/%d | Affixes:%d/%d | AffixEffect:%d | Tomes:%d"
      % (n_echo, len(echoes), n_skill, len(skill), n_affix, len(affixes_fr),
         len(affix_effect_fr), len(tomes_fr)))
print("--- dynFR (couverture par classe) ---")
for name in sorted(dyn_report):
    cl = dyn_report[name]
    print("  %-20s %2d classes : %s" % (name, len(cl), ", ".join(cl)))
