# -*- coding: utf-8 -*-
# Construit fr_translations.json en ne traduisant QUE des structures sûres
# (haute confiance). Le reste est laissé non traduit (anglais en jeu).
import json, re

DATA = r"../data"
echoes = json.load(open(DATA + r"\echoes-dump.json", encoding='utf-8'))
skill = json.load(open(DATA + r"\skilltree-dump.json", encoding='utf-8'))

# Charge des traductions manuelles existantes pour ne pas les écraser
try:
    existing = json.load(open(DATA + r"\fr_translations.json", encoding='utf-8'))
except Exception:
    existing = {}
NAMES = dict(existing.get("names", {}))
DESCS = dict(existing.get("descs", {}))
MANUAL_NAMES = set(NAMES)  # à préserver
MANUAL_DESCS = set(DESCS)

STAT = {"Agility": "l'agilité", "Strength": "la force", "Intellect": "l'intelligence",
        "Stamina": "l'endurance", "Spirit": "l'esprit"}
# noms d'echoes/nœuds (base, sans rang) — traductions soignées
NAME_BASE = {
 "Agility Boost": "Gain d'agilité", "Strength Training": "Entraînement de force",
 "Mind Expansion": "Expansion de l'esprit", "Iron Constitution": "Constitution de fer",
 "Mana Regeneration": "Régénération de mana", "Brutal Might": "Puissance brutale",
 "Adaptive Power": "Puissance adaptative", "Accelerated Decay": "Décomposition accélérée",
 "Ambidexterity": "Ambidextrie", "Armor Mastery": "Maîtrise des armures",
 "Weapon Mastery": "Maîtrise des armes", "Bola Shot": "Tir de bola",
 "Spiritual Fortitude": "Courage spirituel", "Mystic Potency": "Puissance mystique",
 "Reinforced Shielding": "Bouclier renforcé", "Cavalry Instincts": "Instincts de cavalerie",
 "Mana Feed": "Apport de mana", "Warm-Blooded": "Sang chaud",
 "Bolstered Vitality": "Vitalité renforcée", "Resilience": "Résilience",
 "Adaptive Resilience": "Résilience adaptative", "Lifebond": "Lien vital",
 "Arcane Equilibrium": "Équilibre des arcanes", "Essence of Sundering": "Essence de fracassement",
 "Essence of the Deep": "Essence des profondeurs", "Cheat Death": "Tromper la mort",
 "Cold Weather Flying": "Vol par temps froid",
}


# phrases de stat (EN -> FR) pour les patterns rigides "Increases/Reduces <phrase> by <val>"
PHRASE = {
 "Agility": "l'agilité", "Strength": "la force", "Intellect": "l'intelligence",
 "Stamina": "l'endurance", "Spirit": "l'esprit",
 "armor": "l'armure", "Armor": "l'armure",
 "all damage": "tous les dégâts", "all damage done": "tous les dégâts infligés",
 "attack power": "la puissance d'attaque", "spell power": "la puissance des sorts",
 "armor penetration rating": "le score de pénétration d'armure",
 "block value": "la valeur de blocage",
 "critical strike rating": "le score de coup critique",
 "critical strike chance": "la chance de coup critique",
 "haste rating": "le score de hâte", "hit rating": "le score de toucher",
 "expertise rating": "le score d'expertise", "dodge rating": "le score d'esquive",
 "parry rating": "le score de parade", "defense rating": "le score de défense",
 "resilience rating": "le score de résilience",
 "movement speed": "la vitesse de déplacement",
 "attack speed": "la vitesse d'attaque",
 "Healing done": "les soins prodigués", "healing done": "les soins prodigués",
 "your maximum health": "votre vie maximale", "maximum health": "la vie maximale",
 "your maximum mana": "votre mana maximal", "maximum mana": "le mana maximal",
 "your damage": "vos dégâts", "your damage done": "vos dégâts infligés",
 "damage done": "les dégâts infligés", "your healing": "vos soins",
 "Arcane Resistance": "la résistance aux Arcanes", "Fire Resistance": "la résistance au Feu",
 "Frost Resistance": "la résistance au Givre", "Shadow Resistance": "la résistance à l'Ombre",
 "Nature Resistance": "la résistance à la Nature", "all resistances": "toutes les résistances",
 "your armor": "votre armure", "your block value": "votre valeur de blocage",
 "your attack power": "votre puissance d'attaque", "your Attack Power": "votre puissance d'attaque",
 "your spell power": "votre puissance des sorts", "your Spell Power": "votre puissance des sorts",
 "your Intellect": "votre intelligence", "your Agility": "votre agilité",
 "your Strength": "votre force", "your Stamina": "votre endurance", "your Spirit": "votre esprit",
 "your Expertise": "votre expertise", "your Armor": "votre armure",
 "your critical strike chance": "votre chance de coup critique",
 "your critical strike rating": "votre score de coup critique",
 "your chance to hit": "votre chance de toucher", "Haste": "la hâte",
 "melee damage": "les dégâts de mêlée", "ranged damage": "les dégâts à distance",
 "your mana regeneration": "votre régénération de mana",
 "critical strike damage and critical healing": "les dégâts critiques et les soins critiques",
 "your maximum Energy": "votre énergie maximale", "your maximum Rage": "votre rage maximale",
 "the duration of beneficial effects you cast on yourself": "la durée des effets bénéfiques que vous lancez sur vous-même",
 "the amount of cloth you find on humanoids": "la quantité de tissu trouvée sur les humanoïdes",
 "the amount of materials gained from Skinning": "la quantité de matériaux obtenue par le dépeçage",
 "the amount of materials gained from Mining": "la quantité de matériaux obtenue par le minage",
 "the amount of materials gained from Herbalism": "la quantité de matériaux obtenue par l'herboristerie",
}
PHRASE_KEYS = sorted(PHRASE, key=lambda s: -len(s))


def stat_name(text):
    val = r"(@[^@]+@%?|\d+%?)"
    for ph in PHRASE_KEYS:
        m = re.match(r"^Increases %s by %s ?(\.?)$" % (re.escape(ph), val), text)
        if m:
            return "Augmente %s de %s%s" % (PHRASE[ph], m.group(1), m.group(2))
        m = re.match(r"^Reduces %s by %s ?(\.?)$" % (re.escape(ph), val), text)
        if m:
            return "Réduit %s de %s%s" % (PHRASE[ph], m.group(1), m.group(2))
        m = re.match(r"^Reduces %s taken by %s ?(\.?)$" % (re.escape(ph), val), text)
        if m:
            return "Réduit %s subis de %s%s" % (PHRASE[ph], m.group(1), m.group(2))
    return extra(text)


CREATURE = {"Beasts": "les bêtes", "Demons": "les démons", "Dragonkin": "les draconiens",
            "Elementals": "les élémentaires", "Undead": "les morts-vivants",
            "Humanoids": "les humanoïdes", "Giants": "les géants",
            "Mechanicals": "les mécaniques", "Aberrations": "les aberrations"}
SCHOOL = {"Arcane": "des arcanes", "Fire": "de feu", "Frost": "de givre",
          "Shadow": "d'ombre", "Nature": "de nature", "Holy": "sacrés",
          "Bleed": "de saignement", "Physical": "physiques"}


def extra(text):
    val = r"(@[^@]+@%?|\d+%?)"
    m = re.match(r"^Increases your spell power by %s when fighting (\w+)( enemies)?\.$" % val, text)
    if m and m.group(2) in CREATURE:
        return "Augmente votre puissance des sorts de %s face %s." % (m.group(1), CREATURE[m.group(2)])
    m = re.match(r"^Increases your attack power by %s when fighting (\w+)( enemies)?\.$" % val, text)
    if m and m.group(2) in CREATURE:
        return "Augmente votre puissance d'attaque de %s face %s." % (m.group(1), CREATURE[m.group(2)])
    m = re.match(r"^Increases mount speed by an additional %s%%\.$" % r"(@[^@]+@|\d+)", text)
    if m:
        return "Augmente la vitesse de monture de %s%% supplémentaires." % m.group(1)
    m = re.match(r"^Your (\w+) over time effects can now critically strike\.$", text)
    if m and m.group(1) in SCHOOL:
        return "Vos effets %s sur la durée peuvent désormais infliger des coups critiques." % SCHOOL[m.group(1)]
    m = re.match(r"^Reduces the cooldown of your (.+) abilities by %s\.?$" % val, text)
    if m:
        return "Réduit de %s le temps de recharge de vos capacités suivantes : %s." % (m.group(2), m.group(1))
    m = re.match(r"^Reduces the mana cost of your spells by %s\.?$" % val, text)
    if m:
        return "Réduit le coût en mana de vos sorts de %s." % m.group(1)
    m = re.match(r"^Generates %s (Rage|Energy|Runic Power|Mana) every (\d+) sec\.?$" % val, text)
    if m:
        res = {"Rage": "de rage", "Energy": "d'énergie", "Runic Power": "de puissance runique", "Mana": "de mana"}
        return "Génère %s %s toutes les %s sec." % (m.group(1), res[m.group(2)], m.group(3))
    # ---- templates d'echoes multi-rangs (même phrase, token différent) ----
    sch = r"(Arcane|Fire|Frost|Shadow|Nature|Holy|Physical)"
    schf = {"Arcane": "des Arcanes", "Fire": "de Feu", "Frost": "de Givre", "Shadow": "d'Ombre",
            "Nature": "de Nature", "Holy": "sacrés", "Physical": "physiques"}
    m = re.match(r"^Every 5 sec while in combat, you launch 3 missiles at random locations, dealing %s %s damage to enemies hit\. This effect deals at least (\d+) damage\.$" % (val, sch), text)
    if m:
        return "Toutes les 5 sec en combat, vous lancez 3 projectiles à des endroits aléatoires, infligeant %s dégâts %s aux ennemis touchés. Cet effet inflige au moins %s dégâts." % (m.group(1), schf[m.group(2)], m.group(3))
    m = re.match(r"^Your melee attacks have a %s chance to strike an additional time\.$" % val, text)
    if m:
        return "Vos attaques de mêlée ont %s de chances de frapper une fois de plus." % m.group(1)
    m = re.match(r"^Your Auto Shot has a %s chance to fire an additional shot\.$" % val, text)
    if m:
        return "Votre Tir automatique a %s de chances de tirer un projectile supplémentaire." % m.group(1)
    m = re.match(r"^After standing still for 2 sec, your armor is increased by %s for 5 sec after you move\.$" % val, text)
    if m:
        return "Après être resté immobile 2 sec, votre armure est augmentée de %s pendant 5 sec après vous être déplacé." % m.group(1)
    m = re.match(r"^Your (\w+) effects can now critically strike\.$", text)
    if m:
        ef = {"Bleed": "de saignement", "Poison": "de poison", "Disease": "de maladie"}
        if m.group(1) in ef:
            return "Vos effets %s peuvent désormais infliger des coups critiques." % ef[m.group(1)]
    # X Brand (marque cumulable par école)
    m = re.match(r"^Your direct (\w+) damage spells and abilities apply a stacking mark to the target for 8 sec, increasing the \w+ damage you deal to that target by (@[^@]+@) per stack\. Stacks up to 5 times\.$", text)
    if m and m.group(1) in schf:
        return ("Vos sorts et capacités de dégâts directs %s appliquent une marque cumulable à la cible pendant 8 sec, "
                "augmentant les dégâts %s que vous lui infligez de %s par cumul. Se cumule jusqu'à 5 fois."
                % (schf[m.group(1)], schf[m.group(1)], m.group(2)))
    # Reduces the duration of <X> effects on you by N%
    DUR = {"stun": "d'étourdissement", "root": "d'immobilisation", "disarm": "de désarmement",
           "fear": "de peur", "silence": "de silence", "snare": "d'entrave",
           "movement slowing": "de ralentissement", "interrupt": "d'interruption"}
    m = re.match(r"^Reduces the duration of ([a-z ]+) effects on you by (@[^@]+@%?|\d+%?)\.$", text)
    if m and m.group(1) in DUR:
        return "Réduit la durée des effets %s sur vous de %s." % (DUR[m.group(1)], m.group(2))
    # Restores N mana/health every N sec
    m = re.match(r"^Restores (@[^@]+@|\d+) (mana|health) every (\d+) sec\.?$", text)
    if m:
        what = "de mana" if m.group(2) == "mana" else "de vie"
        return "Restaure %s %s toutes les %s sec." % (m.group(1), what, m.group(3))
    # Increases threat / Reduces threat
    m = re.match(r"^Increases threat generated by (@[^@]+@%?|\d+%?)\.$", text)
    if m:
        return "Augmente la menace générée de %s." % m.group(1)
    m = re.match(r"^Reduces threat generated by (@[^@]+@%?|\d+%?)\.$", text)
    if m:
        return "Réduit la menace générée de %s." % m.group(1)
    # Increases healing received by N
    m = re.match(r"^Increases healing received by (@[^@]+@%?|\d+%?)\.$", text)
    if m:
        return "Augmente les soins reçus de %s." % m.group(1)
    # Increases your movement speed by an additional N%
    m = re.match(r"^Increases your movement speed by an additional (@[^@]+@%?|\d+%?)\.$", text)
    if m:
        return "Augmente votre vitesse de déplacement de %s supplémentaires." % m.group(1)
    # Increases your Energy regeneration by N
    m = re.match(r"^Increases your Energy regeneration by (@[^@]+@%?|\d+%?)$", text)
    if m:
        return "Augmente votre régénération d'énergie de %s" % m.group(1)
    # X Hazard : "While 4 or more enemies are within range, the damage of your <list> is increased by N%."
    m = re.match(r"^While 4 or more enemies are within range, the damage of your (.+?) is increased by (\d+)%\.$", text)
    if m:
        return "Tant qu'au moins 4 ennemis sont à portée, les dégâts de vos %s sont augmentés de %s%%." % (m.group(1), m.group(2))
    # X Surge : instant-cast
    m = re.match(r"^Casting a spell or ability has a chance to make your next eligible spell instant-cast\.\s*Eligible spells\s*:\s*(.+?)\.?$", text)
    if m:
        return "Lancer un sort ou une capacité a une chance de rendre votre prochain sort éligible instantané. Sorts éligibles : %s." % m.group(1)
    # Pet bonds
    m = re.match(r"^Increases your pets' Spell power by (@[^@]+@), based on your Spell power\.$", text)
    if m:
        return "Augmente la puissance des sorts de vos familiers de %s, selon votre puissance des sorts." % m.group(1)
    m = re.match(r"^Increases your pets' Attack power by (@[^@]+@), based on your Attack power\.$", text)
    if m:
        return "Augmente la puissance d'attaque de vos familiers de %s, selon votre puissance d'attaque." % m.group(1)
    # Ralentissements
    m = re.match(r"^Your melee attacks slow enemies by (\d+)% for (\d+) sec\.$", text)
    if m:
        return "Vos attaques de mêlée ralentissent les ennemis de %s%% pendant %s sec." % (m.group(1), m.group(2))
    m = re.match(r"^Your direct damage spells slow enemies by (\d+)% for (\d+) sec\.$", text)
    if m:
        return "Vos sorts de dégâts direct ralentissent les ennemis de %s%% pendant %s sec." % (m.group(1), m.group(2))
    return None


def tr_name(name):
    if name in NAME_BASE:
        return NAME_BASE[name]
    m = re.match(r"^(.*) \(Rank (\d+)\)$", name)
    if m and m.group(1) in NAME_BASE:
        return "%s (Rang %s)" % (NAME_BASE[m.group(1)], m.group(2))
    m = re.match(r"^(.*) Milestone$", name)
    if m and m.group(1) in NAME_BASE:
        return "%s (Jalon)" % NAME_BASE[m.group(1)]
    return None


def norm2(s):
    s = (s or "").replace("\\r", " ").replace("\\n", " ").replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", s).strip()


def strip_replace(s):
    # retire le suffixe "Replace <X> (Rank N)." des nœuds de skill tree
    return re.sub(r"\s*Replace .+?\(Rank \d+\)\.?\s*$", "", s).strip()


SCHOOL_DMG = {"Arcane": "d'Arcanes", "Fire": "de Feu", "Frost": "de Givre", "Shadow": "d'Ombre",
              "Nature": "de Nature", "Holy": "sacrés", "Physical": "physiques"}


def tr_skill(t):
    m = re.match(r"^Allows you to equip (\d+) item\(s\) regardless of its level requirement\.$", t)
    if m:
        return "Vous permet d'équiper %s objet(s) quel que soit leur niveau requis." % m.group(1)
    m = re.match(r"^(\d+)% of the damage you take is delayed, dealing its damage over 5 seconds instead\.$", t)
    if m:
        return "%s%% des dégâts que vous subissez sont différés et infligés sur 5 sec à la place." % m.group(1)
    m = re.match(r"^When you heal an ally, a nearby enemy takes Holy damage equal to (\d+)% of the healing done\.$", t)
    if m:
        return "Quand vous soignez un allié, un ennemi proche subit des dégâts sacrés égaux à %s%% des soins prodigués." % m.group(1)
    m = re.match(r"^Your melee and ranged critical strikes grant Butcher.s Tempo, increasing your Attack Speed by 1% for 6 sec\. This effect stacks up to (\d+) times\.$", t)
    if m:
        return "Vos coups critiques de mêlée et à distance octroient Butcher's Tempo, augmentant votre vitesse d'attaque de 1%% pendant 6 sec. Se cumule jusqu'à %s fois." % m.group(1)
    m = re.match(r"^When crafting items, you have a (\d+)% chance to recover some of the reagents used\.$", t)
    if m:
        return "Lors de la fabrication, vous avez %s%% de chances de récupérer une partie des composants utilisés." % m.group(1)
    m = re.match(r"^Taking magical damage reduces damage taken from that school by (\d+)% for 8 sec\.$", t)
    if m:
        return "Subir des dégâts magiques réduit les dégâts subis de cette école de %s%% pendant 8 sec." % m.group(1)
    m = re.match(r"^Reduces (\w+) damage taken by (\d+)%\.$", t)
    if m and m.group(1) in SCHOOL_DMG:
        return "Réduit les dégâts %s subis de %s%%." % (SCHOOL_DMG[m.group(1)], m.group(2))
    m = re.match(r"^Increases experience gained by an additional (\d+)%\.$", t)
    if m:
        return "Augmente l'expérience gagnée de %s%% supplémentaires." % m.group(1)
    m = re.match(r"^While above 75% mana, you gain Surging Power, increasing your spell damage by (\d+)%\. This effect persists until your mana falls below 25%, at which point it is replaced by Restorative Flow\. Restorative Flow increases your mana regeneration by (\d+)% and persists until your mana rises above 75%, at which point it is replaced by Surging Power\.$", t)
    if m:
        return ("Au-dessus de 75%% de mana, vous gagnez Puissance déferlante, augmentant vos dégâts des sorts de %s%%. "
                "Cet effet persiste jusqu'à ce que votre mana tombe sous 25%%, où il est remplacé par Flux réparateur. "
                "Flux réparateur augmente votre régénération de mana de %s%% et persiste jusqu'à ce que votre mana repasse au-dessus de 75%%, où il est remplacé par Puissance déferlante." % (m.group(1), m.group(2)))
    # familles de nœuds (un nombre varie par rang)
    P = [
     (r"^Increases your total mana by (\d+)\.$", "Augmente votre mana totale de %s."),
     (r"^Increases your mana by (\d+)%\.$", "Augmente votre mana de %s%%."),
     (r"^You deal (\d+)% increased damage to enemies below 35% health\.$", "Vous infligez %s%% de dégâts supplémentaires aux ennemis sous 35%% de vie."),
     (r"^While moving, damage taken is reduced by (\d+)%\.$", "En mouvement, les dégâts subis sont réduits de %s%%."),
     (r"^Gathering from a node increases your movement speed by (\d+)% for 10 sec\.$", "Récolter sur un gisement augmente votre vitesse de déplacement de %s%% pendant 10 sec."),
     (r"^Overhealing shields you for (\d+)% of the overhealing done by direct healing spells, up to 20% of your maximum health\.$", "Le surplus de soins vous octroie un bouclier valant %s%% du surplus de soins de vos sorts de soin direct, jusqu'à 20%% de votre vie maximale."),
     (r"^(\d+)% of all healing you deal to allies also heals you\.$", "%s%% de tous les soins que vous prodiguez à vos alliés vous soignent également."),
     (r"^Reduces Magical damage taken by (\d+)%\.$", "Réduit les dégâts magiques subis de %s%%."),
     (r"^Reduces Ranged damage taken by (\d+)%\.$", "Réduit les dégâts à distance subis de %s%%."),
     (r"^Reduces Area-of-Effect damage taken by (\d+)%\.$", "Réduit les dégâts de zone subis de %s%%."),
     (r"^Increases damage and healing done by (\d+)%\.$", "Augmente les dégâts et soins infligés de %s%%."),
     (r"^Whenever you kill an enemy that grants experience or honor, your movement speed is increased by an additional (\d+)% for 5 sec\.$", "Chaque fois que vous tuez un ennemi octroyant de l'expérience ou de l'honneur, votre vitesse de déplacement est augmentée de %s%% supplémentaires pendant 5 sec."),
     (r"^Every 3 sec while out of combat and not mounted, your movement speed is increased by an additional (\d+)%\. Stacks up to 3 times\.$", "Toutes les 3 sec hors combat et démonté, votre vitesse de déplacement est augmentée de %s%% supplémentaires. Se cumule jusqu'à 3 fois."),
     (r"^Every 3 sec while out of combat and mounted, your mount speed is increased by an additional (\d+)%\. Stacks up to 3 times\.$", "Toutes les 3 sec hors combat et monté, votre vitesse de monture est augmentée de %s%% supplémentaires. Se cumule jusqu'à 3 fois."),
     (r"^While out of combat, you restore (\d+)% of your maximum health every 3 seconds\.$", "Hors combat, vous récupérez %s%% de votre vie maximale toutes les 3 sec."),
     (r"^While in combat, you restore (\d+)% of your maximum health every 3 seconds\.$", "En combat, vous récupérez %s%% de votre vie maximale toutes les 3 sec."),
     (r"^Your Hearthstone cools down (\d+)% faster\.$", "Votre Pierre de foyer se recharge %s%% plus vite."),
     (r"^Reduces all damage taken while stunned or mind controlled by (\d+)%\.$", "Réduit tous les dégâts subis pendant un étourdissement ou un contrôle mental de %s%%."),
     (r"^While below (\d+)% health, damage taken is reduced by 30%\.$", "Sous %s%% de vie, les dégâts subis sont réduits de 30%%."),
     (r"^Whenever you kill an enemy that grants experience or honor, you restore (\d+)% of your maximum Health\.$", "Chaque fois que vous tuez un ennemi octroyant de l'expérience ou de l'honneur, vous récupérez %s%% de votre vie maximale."),
     (r"^When you use a potion, you instantly restore an additional (\d+)% of your maximum Health\.$", "Lorsque vous utilisez une potion, vous récupérez instantanément %s%% de votre vie maximale en plus."),
     (r"^Increases your swimming speed by an additional (\d+)%\.$", "Augmente votre vitesse de nage de %s%% supplémentaires."),
     (r"^Whenever you kill an enemy that grants experience or honor, your damage is increased by (\d+)% for 10 sec\. Stacks up to 5 times\.$", "Chaque fois que vous tuez un ennemi octroyant de l'expérience ou de l'honneur, vos dégâts sont augmentés de %s%% pendant 10 sec. Se cumule jusqu'à 5 fois."),
     (r"^Increases reputation gains by (\d+)%\.$", "Augmente les gains de réputation de %s%%."),
     (r"^Reduces fall damage taken by (\d+)%$", "Réduit les dégâts de chute subis de %s%%."),
     (r"^Reduces gathering time by (\d+)%\.$", "Réduit le temps de récolte de %s%%."),
     (r"^Reduces crafting time by (\d+)%\.$", "Réduit le temps de fabrication de %s%%."),
     (r"^Increases the duration of food buffs by (\d+)%\.$", "Augmente la durée des buffs de nourriture de %s%%."),
     (r"^Increases your chance to find rare loot by (\d+)%\.$", "Augmente vos chances de trouver du butin rare de %s%%."),
     (r"^Increases experience gained from quests by an additional (\d+)%\.$", "Augmente l'expérience gagnée par les quêtes de %s%% supplémentaires."),
     (r"^Increases experience gained from gathering and killing monsters by an additional (\d+)%\.$", "Augmente l'expérience gagnée par la récolte et le meurtre de monstres de %s%% supplémentaires."),
     (r"^Allows (\d+)% of your mana regeneration to continue while casting\.$", "Permet à %s%% de votre régénération de mana de continuer pendant l'incantation."),
     (r"^Movement Speed increased by (\d+)%\.$", "Vitesse de déplacement augmentée de %s%%."),
     (r"^Increases your mount speed by an additional (\d+)%\.$", "Augmente votre vitesse de monture de %s%% supplémentaires."),
    ]
    for pat, rep in P:
        m = re.match(pat, t)
        if m:
            return rep % m.groups()
    # Into the Fray (2 nombres)
    m = re.match(r"^While you have 3 or more enemies within 8 yds of you, you generate (\d+)% increased threat and deal (\d+)% increased damage\.$", t)
    if m:
        return "Tant qu'au moins 3 ennemis sont à 8 m de vous, vous générez %s%% de menace supplémentaire et infligez %s%% de dégâts supplémentaires." % (m.group(1), m.group(2))
    # Vengeful Momentum (stacks variable)
    m = re.match(r"^Taking direct melee hits grants a stack of Momentum\. This effect cannot occur more than once every 0\.3 sec\. At (\d+) stacks, you deal 10 Physical damage and generate a massive amount of threat\. Damage scales with your Stamina\.$", t)
    if m:
        return "Subir des coups de mêlée directs octroie un cumul d'Élan. Cet effet ne peut pas se produire plus d'une fois toutes les 0,3 sec. À %s cumuls, vous infligez 10 dégâts physiques et générez une menace massive. Les dégâts dépendent de votre Endurance." % m.group(1)
    return None


auto_n = auto_d = 0
for coll in (echoes, skill):
    for sid, e in coll.items():
        nm = e.get('name')
        if nm and nm not in MANUAL_NAMES:
            fr = tr_name(nm)
            if fr:
                NAMES[nm] = fr; auto_n += 1
        ds = (e.get('desc') or '')
        if ds and ds not in MANUAL_DESCS:
            core = strip_replace(norm2(ds))
            fr = stat_name(core) or tr_skill(core)
            if fr:
                DESCS[ds] = fr; auto_d += 1

json.dump({"names": NAMES, "descs": DESCS},
          open(DATA + r"\fr_translations.json", 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print("Noms traduits:", len(NAMES), "(+%d auto)" % auto_n,
      "| Descs traduites:", len(DESCS), "(+%d auto)" % auto_d)
