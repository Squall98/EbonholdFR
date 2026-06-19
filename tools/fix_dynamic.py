# -*- coding: utf-8 -*-
# Corrige les echoes "multi-variantes de classe" dont toutes les variantes
# recevaient la MÊME traduction FR (celle d'une seule classe).
# On traduit CHAQUE variante en gardant les noms de sorts/dots/ressources en anglais.
import json, re

DATA = r"../data"
e = json.load(open(DATA + r"\echoes-dump.json", encoding="utf-8"))
tr = json.load(open(DATA + r"\fr_translations.json", encoding="utf-8"))
descs = tr["descs"]

def norm(s):
    s = (s or "").replace("\\r", " ").replace("\\n", " ").replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", s).strip()

# --- effets communs (réutilisés) ---
EMBER = ("une petite braise jaillit de vous, infligeant @x@ dégâts de Feu à un ennemi "
         "aléatoire dans un rayon de 20 mètres. Cet effet inflige au moins 15 dégâts et "
         "ne peut pas se produire plus d'une fois toutes les 1.50 sec.")
STONE = ("projetez un rocher sur la cible, infligeant @x@ dégâts Physiques à tous les "
         "ennemis dans un rayon de 8 mètres de l'impact. Cet effet inflige au moins 15 dégâts.")
STONE_INF = ("projeter un rocher sur la cible, infligeant @x@ dégâts Physiques à tous les "
             "ennemis dans un rayon de 8 mètres de l'impact. Cet effet inflige au moins 15 dégâts.")
ARC_END = "infligeant @x@ dégâts des Arcanes aux ennemis touchés. Cet effet inflige au moins 30 dégâts."

# (name, sous-chaîne unique d'identification dans l'EN brut, FR de la variante)
FIXES = [
 # ---------- EMBER SPARK ----------
 ("Ember Spark", "60 Rage, 80 Energy", "Pour chaque tranche de 60 points de rage, 80 d'énergie ou 40 de mana dépensée, " + EMBER),
 ("Ember Spark", "60 Rage you spend", "Pour chaque tranche de 60 points de rage dépensée, " + EMBER),
 ("Ember Spark", "40 Runic Power", "Pour chaque tranche de 40 points de puissance runique dépensée, " + EMBER),
 ("Ember Spark", "80 Energy you spend", "Pour chaque tranche de 80 points d'énergie dépensée, " + EMBER),
 ("Ember Spark", "per level) Mana you spend", "Pour chaque tranche de (40 + 12 par niveau) de mana dépensée, " + EMBER),
 ("Ember Spark", "per level) you spend", "Pour chaque tranche de (40 + 12 par niveau) dépensée, " + EMBER),
 # ---------- STONEFIST BARRAGE ----------
 ("Stonefist Barrage", "Auto Shot critical strikes", "Vos coups critiques d'Auto Shot ont une chance de " + STONE_INF),
 ("Stonefist Barrage", "Lightning Bolt, Chain Lightning", "Quand vous lancez Lightning Bolt, Chain Lightning, Healing Wave ou Chain Heal, vous " + STONE),
 ("Stonefist Barrage", "Starfire, Nourish, or Mangle", "Quand vous lancez Starfire, Nourish ou Mangle, vous " + STONE),
 ("Stonefist Barrage", "Mutilate, Sinister Strike", "Quand vous lancez Mutilate, Sinister Strike ou Hemorrhage, vous avez une chance de " + STONE_INF),
 ("Stonefist Barrage", "Arcane Blast, Fireball", "Quand vous lancez Arcane Blast, Fireball, Frostbolt ou Frostfire Bolt, vous " + STONE),
 ("Stonefist Barrage", "Smite, Flash Heal", "Quand vous lancez Smite, Flash Heal, Greater Heal ou Mind Blast, vous " + STONE),
 ("Stonefist Barrage", "Mortal Strike, Bloodthirst", "Quand vous lancez Mortal Strike, Bloodthirst ou Shield Slam, vous " + STONE),
 ("Stonefist Barrage", "cast Judgement, you hurl", "Quand vous lancez Judgement, vous " + STONE),
 ("Stonefist Barrage", "Death Strike, Heart Strike", "Quand vous lancez Death Strike, Heart Strike, Obliterate ou Scourge Strike, vous " + STONE),
 ("Stonefist Barrage", "Warlock periodic damage", "Vos dégâts périodiques de Warlock ont une chance de vous faire " + STONE_INF),
 # ---------- ARCANE BOMBARDMENT ----------
 ("Arcane Bombardment", "cast a melee ability", "Quand vous utilisez une capacité de mêlée, vous avez 20% de chances de lancer 3 missiles à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "Crusader Strike, Hammer of the Righteous", "Quand vous lancez Crusader Strike, Hammer of the Righteous, Judgement ou Holy Shock, vous lancez 2 missiles à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "spend a Rune", "Chaque fois que vous dépensez une Rune, vous lancez un missile à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "Arcane Shot, Aimed Shot", "Quand vous lancez Arcane Shot, Aimed Shot, Explosive Shot ou Chimera Shot, vous lancez 3 missiles à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "Flame Shock, Earth Shock, or Frost Shock, you launch 2 missiles at a random location", "Quand vous lancez Flame Shock, Earth Shock ou Frost Shock, vous lancez 2 missiles à un endroit aléatoire, " + ARC_END),
 ("Arcane Bombardment", "Flame Shock, Earth Shock, or Frost Shock, you launch 2 missiles at a random nearby", "Quand vous lancez Flame Shock, Earth Shock ou Frost Shock, vous lancez 2 missiles à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "Wrath, Starfire, Regrowth", "Quand vous lancez Wrath, Starfire, Regrowth, Shred ou Maul, vous avez une chance de lancer 3 missiles à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "use a finishing move", "Quand vous utilisez une attaque de finition, vous avez 20% de chances par point de combo de lancer 3 missiles à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "Your critical strikes have a chance to launch a missile", "Vos coups critiques ont une chance de lancer un missile à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "Shadow Word: Pain and periodic healing from Renew", "Vos dégâts périodiques de Shadow Word: Pain et vos soins périodiques de Renew ont une chance de lancer un missile à un endroit aléatoire proche, " + ARC_END),
 ("Arcane Bombardment", "Immolate, Corruption, and Curse of Agony", "Les dégâts périodiques d'Immolate, Corruption et Curse of Agony ont une chance de lancer un missile à un endroit aléatoire proche, " + ARC_END),
]

# --- familles RÈGLE : on traduit la structure, on garde la liste de sorts EN ---
# Temporal Pressure : "Your cooldowns are now reduced by your Haste. Affected spells : <LISTE>"
def fr_temporal(d):
    d = norm(d)
    m = re.match(r"Your cooldowns are now reduced by your Haste\. Affected spells\s*:\s*(.+)", d)
    if not m:
        return None
    return "Vos temps de recharge sont désormais réduits par votre Hâte. Sorts affectés : " + m.group(1)

# Corrosive Breath : "Every 5 sec, your next <LISTE> unleashes Acid Breath, dealing ..."
def fr_corrosive(d):
    d = norm(d)
    m = re.match(r"Every 5 sec, your next (?:your next )?(.+?) unleashes Acid Breath,.*", d)
    if not m:
        return None
    spells = m.group(1).replace(", or ", " ou ").replace(" or ", " ou ")
    return ("Toutes les 5 sec, votre prochain " + spells + " déchaîne un Souffle acide, infligeant "
            "@x@ dégâts de Nature aux ennemis devant vous et @y@ dégâts de Nature supplémentaires "
            "par seconde pendant 5 sec. Cet effet inflige au moins 15 dégâts et 3 supplémentaires par seconde.")

# Unstable Infusion : "Damaging an enemy applies <DOTS>. Does not affect targets already affected."
def fr_unstable(d):
    d = norm(d)
    m = re.match(r"Damaging an enemy applies (.+?)\. Does not affect targets already affected\.?", d)
    if not m:
        return None
    dots = m.group(1).replace(", or ", " ou ").replace(" or ", " ou ").replace(
        ", based on your current form", ", selon votre forme actuelle")
    return "Blesser un ennemi applique " + dots + ". N'affecte pas les cibles déjà affectées."

# ----- application -----
def set_for(name, raw, fr):
    # supprime toute entrée existante de même norm, puis pose la nouvelle
    target = norm(raw)
    for k in [k for k in descs if norm(k) == target]:
        del descs[k]
    descs[raw] = fr

count = 0
unmatched = []
for sid, it in e.items():
    nm = it.get("name")
    raw = it.get("desc")
    if not nm or not raw:
        continue
    fr = None
    if nm == "Temporal Pressure":
        fr = fr_temporal(raw)
    elif nm == "Corrosive Breath":
        fr = fr_corrosive(raw)
    elif nm == "Unstable Infusion":
        fr = fr_unstable(raw)
    else:
        for fname, sub, ffr in FIXES:
            if nm == fname and sub in norm(raw):
                fr = ffr
                break
    if fr:
        set_for(nm, raw, fr)
        count += 1
    elif nm in ("Temporal Pressure", "Corrosive Breath", "Unstable Infusion",
                "Ember Spark", "Stonefist Barrage", "Arcane Bombardment"):
        unmatched.append((nm, norm(raw)[:80]))

json.dump(tr, open(DATA + r"\fr_translations.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("variantes corrigées:", count)
if unmatched:
    print("NON MATCHÉES:", len(unmatched))
    for u in unmatched[:20]:
        print("  -", u)
