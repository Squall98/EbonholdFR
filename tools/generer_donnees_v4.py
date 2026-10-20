"""EbonholdFR 4.0 — générateur des fichiers de données de l'addon.

Produit, dans le dossier de l'addon :
  * EbonholdFR_Data.lua            descriptions FR (echoes, Soul Tree, affixes, tomes) indexées par
                                   EMPREINTE du texte anglais attendu + noms anglais (option « EN : »)
  * EbonholdFR_Interface_Data.lua  traduction de l'interface du serveur (textes exacts, motifs,
                                   morceaux de phrases)

Entrées (voir les constantes ci-dessous ou les options --xxx) :
  * capture anglaise du jeu (SavedVariables EchoDumpDB, /echodump) : textes rendus en jeu ;
  * capture française (facultative) : sert seulement à VÉRIFIER les gabarits produits ;
  * traductions du launcher : vendor/patch_fr.json (sinon custom_translations.json) : {names, descs,
    noms_dans_desc}, clé = texte anglais EXACT du Spell.dbc ; les noms Ebonhold cités dans une
    description française sont remis en anglais (noms_dans_desc), comme le jeu les affiche ;
  * Spell.dbc du serveur (texte anglais brut, avec ses codes $s1, $d, ${...}, @formule@) ;
  * SpellItemEnchantment.dbc du serveur (facultatif) : texte exact des affixes gravés sur les objets ;
  * anciennes données v3 (facultatives) : repli pour les affixes / tomes non couverts ;
  * ui-fr.json (facultatif) : traduction de l'interface ; à défaut, un petit échantillon intégré.

Principe des descriptions (identique en Python et en Lua, voir EbonholdFR.lua) :
  texte affiché -> sans couleurs, espaces regroupés -> « jetons » = nombres (12, 2.5) et formules
  @...@ -> EMPREINTE = texte où chaque jeton devient « # ».  Le gabarit français contient des
  marqueurs {k} (k-ième jeton du texte anglais affiché) ou {@k} (formule : nombre vert).
  En jeu, on ne traduit que si l'empreinte du texte anglais affiché est connue ; sinon on laisse.

Usage :
  python -I generer_donnees_v4.py                 (chemins par défaut ci-dessous)
  python -I generer_donnees_v4.py --help
Aucune dépendance hors bibliothèque standard.
"""
import argparse
import json
import os
import re
import struct
import sys
from collections import Counter, defaultdict

# --------------------------------------------------------------------------- chemins par défaut
ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(ICI)
EBONHOLD = os.path.normpath(os.path.join(DEPOT, "..", ".."))          # D:\Projets-WoW\Ebonhold
CHANTIER = os.path.join(EBONHOLD, "chantier-maj-2026-10")
SERVEUR = os.path.join(CHANTIER, "serveur-2026-10-20")
DEFAUTS = {
    "capture_en": os.path.join(EBONHOLD, "database", "dumps", "EbonholdEchoDump-enUS-2026-10-20.lua"),
    "capture_fr": os.path.join(EBONHOLD, "database", "dumps", "EbonholdEchoDump-frFR-2026-10-20.lua"),
    "traductions": next((p for p in (os.path.join(EBONHOLD, "launcher", "vendor", "patch_fr.json"),
                                     os.path.join(EBONHOLD, "launcher", "vendor", "custom_translations.json"))
                         if os.path.isfile(p)), os.path.join(EBONHOLD, "launcher", "vendor", "patch_fr.json")),
    "spell_dbc": os.path.join(SERVEUR, "patch-5.MPQ", "DBFilesClient", "Spell.dbc"),
    "enchant_dbc": os.path.join(SERVEUR, "patch-6.MPQ", "DBFilesClient", "SpellItemEnchantment.dbc"),
    "ancien": os.path.join(DEPOT, "data"),
    "ui_fr": os.path.join(CHANTIER, "trad", "ui-fr.json"),
    "sortie": os.path.join(DEPOT, "EbonholdFR"),
}
VERSION_DONNEES = "2026-10-20"

# catégories (codées dans le fichier Lua : valeur = index_gabarit * 10 + catégorie)
CAT_ECHO, CAT_SOUL, CAT_AFFIX, CAT_TOME = 1, 2, 3, 4
NOM_CAT = {CAT_ECHO: "echoes", CAT_SOUL: "soultree", CAT_AFFIX: "affixes", CAT_TOME: "tomes"}

# --------------------------------------------------------------------------- lecture SavedVariables
class LuaSV:
    """Lecteur minimal du format SavedVariables de WoW (tables, chaînes, nombres, booléens,
    commentaires « -- [1] »). Renvoie des dict / list Python ; les chaînes restent en UTF-8."""
    TOK = re.compile(rb'\s+|--[^\n]*|"((?:[^"\\]|\\.)*)"|\[|\]|\{|\}|=|,|;|-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?|[A-Za-z_][A-Za-z0-9_]*', re.S)

    def __init__(self, raw):
        self.toks = []
        pos = 0
        n = len(raw)
        while pos < n:
            m = self.TOK.match(raw, pos)
            if not m:
                raise ValueError("SavedVariables illisible vers l'octet %d : %r" % (pos, raw[pos:pos + 40]))
            t = m.group(0)
            pos = m.end()
            if t[:1].isspace() or t.startswith(b"--"):
                continue
            if t.startswith(b'"'):
                self.toks.append(("s", self.unescape(m.group(1))))
            elif t[:1].isdigit() or t[:1] == b"-":
                self.toks.append(("n", float(t) if (b"." in t or b"e" in t.lower()) else int(t)))
            elif t[:1].isalpha() or t[:1] == b"_":
                self.toks.append(("w", t.decode()))
            else:
                self.toks.append(("p", t.decode()))
        self.i = 0

    @staticmethod
    def unescape(b):
        out = bytearray()
        i = 0
        while i < len(b):
            c = b[i]
            if c == 0x5C and i + 1 < len(b):
                d = b[i + 1]
                simple = {0x6E: 10, 0x74: 9, 0x72: 13, 0x22: 0x22, 0x27: 0x27, 0x5C: 0x5C, 0x61: 7, 0x62: 8,
                          0x66: 12, 0x76: 11, 0x0A: 10}
                if d in simple:
                    out.append(simple[d]); i += 2; continue
                if 0x30 <= d <= 0x39:
                    j = i + 1
                    while j < len(b) and j < i + 4 and 0x30 <= b[j] <= 0x39:
                        j += 1
                    out.append(int(b[i + 1:j]) & 0xFF); i = j; continue
                out.append(d); i += 2; continue
            out.append(c); i += 1
        return out.decode("utf-8", "replace")

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else (None, None)

    def take(self, kind=None, val=None):
        t = self.toks[self.i]
        if (kind and t[0] != kind) or (val is not None and t[1] != val):
            raise ValueError("attendu %s %s, trouvé %r" % (kind, val, t))
        self.i += 1
        return t[1]

    def value(self):
        k, v = self.peek()
        if k == "s" or k == "n":
            self.i += 1
            return v
        if k == "w":
            self.i += 1
            return {"true": True, "false": False, "nil": None}.get(v, v)
        if k == "p" and v == "{":
            return self.table()
        raise ValueError("valeur inattendue %r" % ((k, v),))

    def table(self):
        self.take("p", "{")
        d, arr = {}, []
        while True:
            k, v = self.peek()
            if k == "p" and v == "}":
                self.i += 1
                break
            if k == "p" and v == "[":
                self.i += 1
                key = self.value()
                self.take("p", "]")
                self.take("p", "=")
                d[key] = self.value()
            elif k == "w" and self.toks[self.i + 1] == ("p", "="):
                self.i += 2
                d[v] = self.value()
            else:
                arr.append(self.value())
            k, v = self.peek()
            if k == "p" and v in (",", ";"):
                self.i += 1
        if arr and not d:
            return arr
        for n, x in enumerate(arr, 1):
            d[n] = x
        return d

    def globals(self):
        g = {}
        while self.i < len(self.toks):
            name = self.take("w")
            self.take("p", "=")
            g[name] = self.value()
        return g


def lire_sv(path):
    return LuaSV(open(path, "rb").read()).globals()


# --------------------------------------------------------------------------- lecture DBC (WDBC)
def lire_dbc(path, colonnes):
    raw = open(path, "rb").read()
    magic, nrec, nchamps, taille, _ = struct.unpack("<4s4I", raw[:20])
    if magic != b"WDBC":
        raise ValueError("%s : pas un fichier WDBC" % path)
    base = 20 + nrec * taille
    out = {}
    for i in range(nrec):
        r = raw[20 + i * taille:20 + (i + 1) * taille]
        vals = struct.unpack_from("<%dI" % nchamps, r, 0)
        row = []
        for c, typ in colonnes:
            if typ == "s":
                o = base + vals[c]
                row.append(raw[o:raw.index(b"\0", o)].decode("utf-8", "replace"))
            else:
                row.append(vals[c])
        out[vals[0]] = row
    return out


# --------------------------------------------------------------------------- empreinte (miroir du Lua)
RE_COULEUR = re.compile(r"\|c[0-9a-fA-F]{8}|\|r")
RE_BLANCS = re.compile(r"[ \t\n\r\f\v]+")
RE_JETON = re.compile(r"@[^@]*@|[0-9]+(?:\.[0-9]+)?")


def normaliser(s):
    """Texte affiché -> sans couleurs, blancs regroupés, sans blancs aux bords (comme en jeu)."""
    s = RE_COULEUR.sub("", s or "")
    return RE_BLANCS.sub(" ", s).strip(" ")


def jetons(plain):
    return [(m.start(), m.end(), m.group(0)) for m in RE_JETON.finditer(plain)]


def empreinte(texte):
    return RE_JETON.sub("#", normaliser(texte))


# --------------------------------------------------------------------------- codes du Spell.dbc
RE_CODE = re.compile(r"""
    \$\{(?:[^{}]|\{[^{}]*\})*\}(?:\.\d+)?             # ${ expression } (+ .N décimales)
  | \$[/*]-?\d+(?:\.\d+)?;\$?\d*[a-zA-Z]\d?           # $/10;s1  $*2;200656s1
  | \$[lLgG][^:;$]*:[^;$]*;                           # $lsingulier:pluriel;  $gil:elle;
  | \$@spell(?:desc|tooltip|name)\d+                  # $@spelldesc12345
  | \$\d*[a-zA-Z]\d?                                  # $s1 $200656d $h $a1 $u ...
  | @[^@]*@                                           # formules du serveur (calculées par l'addon)
""", re.X)


def decouper(texte):
    """[(type, texte)] avec type 'l' (littéral) ou 'c' (code)."""
    out, pos = [], 0
    for m in RE_CODE.finditer(texte):
        if m.start() > pos:
            out.append(("l", texte[pos:m.start()]))
        out.append(("c", m.group(0)))
        pos = m.end()
    if pos < len(texte):
        out.append(("l", texte[pos:]))
    return out


def aligner(brut, rendu):
    """Aligne le texte brut du DBC (codes) sur le texte rendu (normalisé) ; renvoie
    [(code, debut, fin)] (positions dans le rendu) ou None."""
    parts = decouper(normaliser(brut))
    rx, codes = [], []
    for typ, t in parts:
        if typ == "l":
            rx.append(re.escape(t))
        else:
            rx.append("(.*?)")
            codes.append(t)
    m = re.fullmatch("".join(rx), rendu, re.S)
    if not m:
        return None
    return [(codes[i], m.start(i + 1), m.end(i + 1)) for i in range(len(codes))]


# unités de durée rendues par le client anglais -> français
UNITES = [(re.compile(r"\b(sec|secs|seconds?)\b"), "sec"), (re.compile(r"\b(min|mins|minutes?)\b"), "min"),
          (re.compile(r"\b(hrs?|hours?)\b"), "h"), (re.compile(r"\b(days?)\b"), "jours")]


def gabarit_valeur(rendu, debut, fin, toks, code):
    """Valeur rendue d'un code -> morceau de gabarit (jetons -> marqueurs)."""
    out, pos = [], debut
    for k, (a, b, t) in enumerate(toks, 1):
        if b <= debut or a >= fin:
            continue
        if a < debut or b > fin:
            return None                      # jeton à cheval sur la frontière : on renonce
        out.append(rendu[pos:a])
        formule = code.startswith("@")
        out.append("{@%d}" % k if formule else "{%d}" % k)
        pos = b
    out.append(rendu[pos:fin])
    s = "".join(out)
    for rx, fr in UNITES:
        s = rx.sub(fr, s)
    return s


RE_NOMBRE_FR = re.compile(r"(?<![0-9.,])[0-9]+(?:[.,][0-9]+)?(?![0-9])")


def construire_gabarit(brut, rendu_norm, fr_brut):
    """-> (gabarit, None) ou (None, raison)."""
    al = aligner(brut, rendu_norm)
    if al is None:
        return None, "alignement"
    toks = jetons(rendu_norm)
    valeurs = {}
    dans_code = set()
    for code, a, b in al:
        v = gabarit_valeur(rendu_norm, a, b, toks, code)
        if v is None:
            return None, "jeton à cheval"
        valeurs.setdefault(code, v)
        valeurs.setdefault(code.lower(), v)
        for k, (ta, tb, _) in enumerate(toks, 1):
            if ta >= a and tb <= b:
                dans_code.add(k)
    # nombres littéraux anglais (hors codes) uniques -> marqueurs, si le français a le même nombre unique
    litteraux = Counter(t for k, (_, _, t) in enumerate(toks, 1) if k not in dans_code and not t.startswith("@"))
    index_lit = {t: k for k, (_, _, t) in enumerate(toks, 1) if k not in dans_code and litteraux[t] == 1}
    fr_parts = decouper(fr_brut)
    fr_lits = Counter()
    for typ, t in fr_parts:
        if typ == "l":
            fr_lits.update(m.group(0) for m in RE_NOMBRE_FR.finditer(t))
    out = []
    for typ, t in fr_parts:
        if typ == "c":
            v = valeurs.get(t)
            if v is None:
                v = valeurs.get(t.lower())
            if v is None:
                return None, "code FR absent de l'anglais : " + t
            out.append(v)
        else:
            if "{" in t or "}" in t:
                t = t.replace("{", "(").replace("}", ")")

            def sub_lit(m):
                n = m.group(0)
                if fr_lits[n] == 1 and n in index_lit:
                    return "{%d}" % index_lit[n]
                return n
            out.append(RE_NOMBRE_FR.sub(sub_lit, t))
    g = "".join(out).replace("\r\n", "\n").replace("\r", "\n")
    g = re.sub(r"[ \t]+\n", "\n", g).strip()
    if g.count("$") > rendu_norm.count("$"):
        return None, "code $ restant"
    return g, None


def remplir(gabarit, toks):
    """Remplit un gabarit avec une liste de jetons (miroir de fill() en Lua)."""
    ok = [True]

    def f(m):
        k = int(m.group(2))
        if k > len(toks):
            ok[0] = False
            return ""
        v = toks[k - 1]
        if m.group(1) == "@" and not v.startswith("@"):
            return "|cff2cfe32" + v + "|r"
        return v
    s = re.sub(r"\{(@?)(\d+)\}", f, gabarit)
    return s if ok[0] else None


def max_marqueur(g):
    return max([int(x) for x in re.findall(r"\{@?(\d+)\}", g)] or [0])


def marquer_nombres(fr, toks_en, debut=0):
    """Nombres d'une traduction écrite en dur -> marqueurs {k}, en suivant l'ordre des jetons
    anglais de même valeur (repli pour les anciennes traductions v3)."""
    k = [debut]

    def sub_n(mm):
        n = mm.group(0)
        for j in range(k[0], len(toks_en)):
            if toks_en[j] == n:
                k[0] = j + 1
                return "{%d}" % (j + 1)
        return n
    return re.sub(r"[0-9]+(?:\.[0-9]+)?", sub_n, fr)


# --------------------------------------------------------------------------- interface (ui-fr.json)
ECHANTILLON_UI = {
    "Apply Changes": "Appliquer les changements",
    "Revert Changes": "Annuler les changements",
    "No changes to apply": "Aucun changement \u00e0 appliquer",
    "Shift-click to link in chat": "Maj-clic pour lier dans la discussion",
    "OBJECTIVES": "OBJECTIFS",
    "Current Objective": "Objectif actuel",
    "Reroll Selection": "Relancer la s\u00e9lection",
    "Reroll Selection  ": "Relancer la s\u00e9lection  ",
    "Requires Tome to unlock": "N\u00e9cessite un Tome pour \u00eatre d\u00e9bloqu\u00e9",
    "Already learned": "D\u00e9j\u00e0 appris",
    "Use to add this echo to your collection": "Utilisez-le pour ajouter cet \u00e9cho \u00e0 votre collection",
    "Unlocks Echo:": "D\u00e9bloque l'\u00e9cho :",
    "Carry over Prestige": "Conserv\u00e9 au Prestige",
    "|cff00FF00Left-click to learn|r": "|cff00FF00Clic gauche pour apprendre|r",
    "|cffAAAAAARight-click to unlearn|r": "|cffAAAAAAClic droit pour d\u00e9sapprendre|r",
    "Enchanted Anvil": "Enclume enchant\u00e9e",
    "Affix Book": "Livre des affixes",
    "Extract": "Extraire",
    "Choose an Affix": "Choisir un affixe",
    "Soul Ashes Progression": "Progression des Cendres d'\u00e2me",
    "Stacks: %s": "Cumuls : %s",
    "Rank: %d/%d": "Rang : %d/%d",
    "Soul Ashes: ": "Cendres d'\u00e2me : ",
    "Remaining Soul Ashes: ": "Cendres d'\u00e2me restantes : ",
    "%s Soul Ashes": "%s Cendres d'\u00e2me",
    "Intensity: %s": "Intensit\u00e9 : %s",
}

# lignes d'affixes gravés sans sort d'affixe correspondant dans la capture (traduction manuelle,
# empreinte du texte anglais -> gabarit)
AFFIXES_MANUELS = {
    "Increases your damage and healing done by #%. Stacks with other ranks.":
        "Augmente vos dégâts et vos soins de {1}%. Se cumule avec les autres rangs.",
    "Increases your damage and healing done by #%.": "Augmente vos dégâts et vos soins de {1}%.",
    "Dealing damage slows your target's movement by #% and increases the time between their attacks by #%.":
        "Infliger des dégâts ralentit le déplacement de votre cible de {1}% et augmente le délai entre ses attaques de {2}%.",
    "Your melee attacks have #% chance to make you strike all nearby enemies dealing weapon damage. While using a two-handed weapon, you have a #% chance to trigger Bladestorm on your target":
        "Vos attaques de mêlée ont {1}% de chances de vous faire frapper tous les ennemis proches, infligeant les dégâts de votre arme. Avec une arme à deux mains, vous avez {2}% de chances de déclencher Bladestorm sur votre cible",
    "Reduces damage taken from Undead enemies by #%. Stacks up to the number of this affix present on your equipment.":
        "Réduit les dégâts subis de la part des morts-vivants de {1}%. Se cumule selon le nombre de cet affixe présent sur votre équipement.",
}

# descriptions calculées des nœuds infinis du Soul Tree (TalentDatabase.lua : computedDesc)
SOUL_INFINIS = {
    "Increases your Stamina by %s.": "Augmente votre Endurance de %s.",
    "Increases your attack power by %s or your spell power by %s, whichever is higher.":
        "Augmente votre puissance d'attaque de %s ou votre puissance des sorts de %s, selon la plus \u00e9lev\u00e9e.",
    "Increases your Strength, Agility, Intellect or Spirit by %s, whichever is highest.":
        "Augmente votre Force, Agilit\u00e9, Intelligence ou Esprit de %s, selon la plus \u00e9lev\u00e9e.",
}

RE_SPEC = re.compile(r"%(?:%|[-+#0]*\d*(?:\.\d+)?[sdifgxXc])")
ECHAPS_LUA = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "'": "'", "\\": "\\"}


def decoder_lua(s):
    """Les textes extraits du code source gardent les échappements Lua (\\n, \\226\\128\\162...)."""
    if "\\" not in s:
        return s
    out, i, b = [], 0, bytearray()

    def flush():
        if b:
            out.append(b.decode("utf-8", "replace")); b.clear()
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            d = s[i + 1]
            if d.isdigit():
                j = i + 1
                while j < len(s) and j < i + 4 and s[j].isdigit():
                    j += 1
                b.append(int(s[i + 1:j]) & 0xFF); i = j; continue
            flush()
            out.append(ECHAPS_LUA.get(d, d)); i += 2; continue
        flush()
        out.append(c); i += 1
    flush()
    return "".join(out)


def motif_lua_depuis_format(en, fr):
    """'+%d%% Soul Ashes' -> ('^%+(%-?%d+)%% Soul Ashes$', '+%1%% Cendres...') ou None."""
    specs_en = [m.group(0) for m in RE_SPEC.finditer(en) if m.group(0) != "%%"]
    specs_fr = [m.group(0) for m in RE_SPEC.finditer(fr) if m.group(0) != "%%"]
    if not specs_en or len(specs_en) != len(specs_fr):
        return None
    pat, pos, n = ["^"], 0, 0
    for m in RE_SPEC.finditer(en):
        pat.append(echapper_motif(en[pos:m.start()]))
        sp = m.group(0)
        if sp == "%%":
            pat.append("%%")
        elif sp[-1] in "di":
            pat.append("(%-?%d+)")
        elif sp[-1] in "fg":
            pat.append("(%-?[%d%.]+)")
        else:
            pat.append("(.-)")
        pos = m.end()
    pat.append(echapper_motif(en[pos:]) + "$")
    rep, pos, k = [], 0, 0
    for m in RE_SPEC.finditer(fr):
        rep.append(fr[pos:m.start()].replace("%", "%%"))
        if m.group(0) == "%%":
            rep.append("%%")
        else:
            k += 1
            rep.append("%%%d" % k)
        pos = m.end()
    rep.append(fr[pos:].replace("%", "%%"))
    p = "".join(pat)
    if p.count("(") > 9:
        return None
    return p, "".join(rep)


def echapper_motif(s):
    return re.sub(r"([%^$().\[\]*+\-?])", r"%\1", s)


def charger_ui(path):
    """-> (textes {en: fr}, source, infos)."""
    if path and os.path.isfile(path):
        d = json.load(open(path, encoding="utf-8"))
        textes = d.get("textes", d if isinstance(d, dict) else {})
        ign = d.get("ignores") or []
        ign = set(ign if isinstance(ign, list) else list(ign))
        av = d.get("a_verifier") or []
        t = {k: v for k, v in textes.items() if isinstance(v, str) and k not in ign}
        return t, "ui-fr.json (version %s)" % d.get("version", "?"), {"ignores": len(ign), "a_verifier": len(av)}
    return dict(ECHANTILLON_UI), "\u00e9chantillon int\u00e9gr\u00e9 (ui-fr.json absent)", {}


RE_COUL_FIN = re.compile(r"\|c[0-9a-fA-F]{8}$")
RE_COUL_DEBUT = re.compile(r"^(?:[ \t\n\r]|\|c[0-9a-fA-F]{8}|\|r)+")


def lettres(s):
    """Nombre de lettres hors codes de couleur et textures (comme nbLettres en Lua)."""
    s = re.sub(r"\|c[0-9a-fA-F]{8}|\|r|\|T.*?\|t", "", s)
    return len(re.findall(r"[A-Za-z]", s))


def prefixe_litteral(motif):
    """Début littéral d'un motif Lua ancré (« ^Soul Ashes: (.+)$ » -> « Soul Ashes: »)."""
    out, i = [], 1
    while i < len(motif):
        c = motif[i]
        if c == "%" and i + 1 < len(motif) and not motif[i + 1].isalnum():
            out.append(motif[i + 1]); i += 2; continue
        if c in "().[]*+-?$%^":
            break
        out.append(c); i += 1
    return "".join(out)


def compiler_ui(textes):
    """-> exact {en: fr}, motifs [(motif, remplacement, début littéral)], morceaux {en: fr}, rejets.
    Les « morceaux » sont les bouts de phrase que le code du serveur colle entre eux ou avec une
    valeur (« Stacks: » .. n, « Requires level » .. n .. « to use ») : ils servent à reconstituer
    une phrase en jeu."""
    exact, motifs, morceaux, rejets = {}, [], {}, []
    for en0, fr0 in textes.items():
        en, fr = decoder_lua(en0), decoder_lua(fr0)
        if not en.strip() or not fr.strip() or en == fr:
            continue
        if "|H" in en:
            rejets.append((en0, "lien")); continue
        specs = [m.group(0) for m in RE_SPEC.finditer(en) if m.group(0) != "%%"]
        if specs:
            # en jeu, les blancs des bords sont mis de côté avant la recherche
            r = motif_lua_depuis_format(en.strip(" \t\n\r"), fr.strip(" \t\n\r"))
            if r:
                motifs.append((r[0], r[1], prefixe_litteral(r[0])[:3]))
            else:
                rejets.append((en0, "format incompatible"))
            continue
        en_l = en.replace("%%", "%")
        fr_l = fr.replace("%%", "%") if "%%" in en else fr
        # bout de phrase : blancs aux bords, « : » final, ou couleur laissée ouverte pour la valeur
        # (« |cffFFD700Soul Ashes: |r|cffFFFFFF » .. n .. « |r »)
        if (en_l != en_l.strip() or en_l.endswith(":") or RE_COUL_FIN.search(en_l)
                or en_l.startswith("|r")):
            if lettres(en_l) >= 3:
                morceaux[en_l] = fr_l
                # en jeu, les blancs et la couleur du début sont mis de côté avant la recherche
                court = RE_COUL_DEBUT.sub("", en_l)
                if court != en_l and lettres(court) >= 3:
                    morceaux.setdefault(court, RE_COUL_DEBUT.sub("", fr_l))
            coeur = en_l.strip()
            if coeur and not RE_COUL_FIN.search(coeur):
                exact.setdefault(coeur, fr_l.strip())
            continue
        exact[en_l] = fr_l
    motifs.sort(key=lambda pr: -len(pr[0]))       # les plus spécifiques d'abord
    return exact, motifs, morceaux, rejets


# --------------------------------------------------------------------------- écriture Lua
def lua_str(s):
    out = ['"']
    for ch in s:
        o = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif o < 32 or o == 127:
            out.append("\\%03d" % o)
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


# --------------------------------------------------------------------------- programme principal
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for k, v in DEFAUTS.items():
        ap.add_argument("--" + k.replace("_", "-"), default=v, help="(d\u00e9faut : %s)" % v)
    ap.add_argument("--rapport", default="", help="fichier JSON de rapport d\u00e9taill\u00e9 (facultatif)")
    a = ap.parse_args()

    print("Lecture de la capture anglaise :", a.capture_en)
    en = lire_sv(a.capture_en)["EchoDumpDB"]
    fr_dump = lire_sv(a.capture_fr)["EchoDumpDB"] if a.capture_fr and os.path.isfile(a.capture_fr) else None
    tr = json.load(open(a.traductions, encoding="utf-8"))
    descs_fr = dict(tr.get("descs", {}))
    # noms Ebonhold cités dans les descriptions : le jeu (sans patch) les affiche en anglais
    n_noms = 0
    for en_desc, paires in (tr.get("noms_dans_desc") or {}).items():
        fr_desc = descs_fr.get(en_desc)
        if not fr_desc:
            continue
        for en_nom, fr_nom, avec_article in paires:
            if avec_article:
                fr_desc = fr_desc.replace(avec_article, en_nom)
            fr_desc = fr_desc.replace(fr_nom, en_nom)
        if fr_desc != descs_fr[en_desc]:
            descs_fr[en_desc] = fr_desc
            n_noms += 1
    print("Traductions :", a.traductions, "(%d descriptions, %d avec noms remis en anglais)" % (len(descs_fr), n_noms))
    print("Lecture du Spell.dbc :", a.spell_dbc)
    dbc = lire_dbc(a.spell_dbc, [(136, "s"), (170, "s")])

    gabarits, index_g = [], {}

    def idx_gabarit(g):
        if g not in index_g:
            index_g[g] = len(gabarits) + 1
            gabarits.append(g)
        return index_g[g]

    fp_table = {}            # empreinte -> (index gabarit, catégorie)
    par_id = {}              # id du sort -> index gabarit (cas particuliers)
    conflits_sans_id = []
    conflits = []
    couverture = {}
    echecs = defaultdict(Counter)
    exemples_echecs = defaultdict(list)
    noms_en = {}

    candidats = defaultdict(list)   # empreinte -> [(gabarit, catégorie, id, jetons, id_utilisable)]

    def ajouter(fp, g, cat, sid, toks, id_sort=True):
        candidats[fp].append((g, cat, sid, toks, id_sort))

    def nombres(txt):
        return sorted(re.findall(r"[0-9]+(?:\.[0-9]+)?", RE_COULEUR.sub("", txt or "")))

    def finaliser():
        """Une empreinte = un gabarit. Si plusieurs sorts au même texte anglais ont des
        traductions différentes, on garde celle qui a le plus de marqueurs (elle reprend les
        nombres affichés au lieu de les écrire en dur). Si, pour un sort, ce gabarit commun
        donnerait d'autres nombres que sa propre traduction, on garde un gabarit propre à ce
        sort (table « id », utilisée quand l'id du sort est connu)."""
        for fp, lst in candidats.items():
            freq = Counter(g for g, *_ in lst)
            gagnant = max(freq, key=lambda g: (len(set(re.findall(r"\{@?\d+\}", g))), freq[g]))
            cat = next(c for g, c, *_ in lst if g == gagnant)
            fp_table[fp] = (idx_gabarit(gagnant), cat, 0)
            for g, c, sid, toks, id_sort in lst:
                if g == gagnant:
                    continue
                conflits.append((sid, fp[:80]))
                if nombres(remplir(gagnant, toks)) != nombres(remplir(g, toks)):
                    if id_sort and sid:
                        par_id[sid] = (fp, idx_gabarit(g))
                    else:
                        conflits_sans_id.append((sid, fp[:80]))

    def traiter(cat, sid, rendus, ok_compteur):
        """rendus : liste de textes anglais tels qu'affichés (formes différentes possibles)."""
        row = dbc.get(sid)
        if not row:
            echecs[cat]["absent du Spell.dbc"] += 1
            return False
        brut = row[1]
        fr_brut = descs_fr.get(brut)
        if fr_brut is None:
            echecs[cat]["pas de traduction"] += 1
            return False
        if not brut.strip():
            echecs[cat]["description vide"] += 1
            return False
        bon = False
        vus = set()
        raisons = []
        for r in rendus:
            if not r:
                continue
            rn = normaliser(r)
            fp = empreinte(rn)
            if fp in vus or rn == "Click for details":
                continue
            vus.add(fp)
            g, raison = construire_gabarit(brut, rn, fr_brut)
            if g is None:
                raisons.append((raison, rn))
                continue
            if max_marqueur(g) > len(jetons(rn)):
                raisons.append(("marqueur hors limites", rn))
                continue
            ajouter(fp, g, cat, sid, [t for _, _, t in jetons(rn)])
            if cat == CAT_AFFIX:
                effets_affixes(sid, rn, g)
            bon = True
        if bon:
            ok_compteur[0] += 1
        elif raisons:
            raison, rn = raisons[0]
            echecs[cat][raison.split(" : ")[0]] += 1
            if len(exemples_echecs[cat]) < 12:
                exemples_echecs[cat].append({"id": sid, "raison": raison, "brut": brut[:300], "rendu": rn[:300]})
        return bon

    # effet seul d'un affixe (« Allows you to engrave ...: <effet> ») -> gabarit de l'effet,
    # pour retrouver la ligne violette gravée sur les objets (texte de SpellItemEnchantment.dbc)
    effets_index = {}

    def effets_affixes(sid, rn, g):
        i_en = rn.find(": ")
        i_fr, lfr = g.find(" : "), 3
        if i_fr < 0:
            i_fr, lfr = g.find(": "), 2
        if i_en <= 0 or i_fr <= 0:
            return
        decal = len(jetons(rn[:i_en + 2]))
        effet_fr = g[i_fr + lfr:]
        if decal:
            effet_fr = re.sub(r"\{(@?)(\d+)\}", lambda mm: "{%s%d}" % (mm.group(1), int(mm.group(2)) - decal), effet_fr)
        effet_fr = effet_fr[:1].upper() + effet_fr[1:]
        cle = empreinte(rn[i_en + 2:]).rstrip(".")
        effets_index.setdefault(cle, effet_fr)
        effets_index.setdefault(cle.lower(), effet_fr)

    # --- echoes
    for nom_cat, cat in (("perks", CAT_ECHO), ("skilltree", CAT_SOUL), ("affixes", CAT_AFFIX), ("tomes", CAT_TOME)):
        t = en.get(nom_cat) or {}
        ok = [0]
        for k, v in t.items():
            sid = int(k)
            if v.get("name"):
                noms_en[sid] = v["name"]
            # formes affichées en jeu : utils.GetSpellDescription (rendered), ligne(s) de
            # l'infobulle du sort (SetHyperlink : une ligne par FontString, la description est
            # souvent seule sur sa ligne, après « Channeled » / « 1 sec cast »)
            rendus = [v.get("rendered"), v.get("desc")]
            tt = v.get("tooltip")
            if isinstance(tt, list) and len(tt) >= 2:
                rendus.extend(x for x in tt[1:] if isinstance(x, str))
            traiter(cat, sid, rendus, ok)
        couverture[NOM_CAT[cat]] = {"total": len(t), "gabarit_fr": ok[0]}

    # --- descriptions calculées des nœuds infinis du Soul Tree
    for en_fmt, fr_fmt in SOUL_INFINIS.items():
        n = 0
        g = en_fmt
        rendu = en_fmt.replace("%s", "12")
        k = 0
        out = []
        pos = 0
        for m in re.finditer(r"%s", fr_fmt):
            k += 1
            out.append(fr_fmt[pos:m.start()] + "|cff00ff00{%d}|r" % k)
            pos = m.end()
        out.append(fr_fmt[pos:])
        ajouter(empreinte(rendu), "".join(out), CAT_SOUL, 0, [t for _, _, t in jetons(rendu)])

    # --- affixes gravés sur les objets (SpellItemEnchantment.dbc)
    affix_obj = {"total": 0, "gabarit_fr": 0, "repli_v3": 0}
    ancien_effets = {}
    ancien_tomes = {}
    if a.ancien and os.path.isdir(a.ancien):
        p = os.path.join(a.ancien, "affix_effect_fr.json")
        if os.path.isfile(p):
            ancien_effets = json.load(open(p, encoding="utf-8"))
        p = os.path.join(a.ancien, "tomes_fr.json")
        if os.path.isfile(p):
            ancien_tomes = json.load(open(p, encoding="utf-8"))
    SUFFIXES = [(". Stacks with other ranks.", ". Se cumule avec les autres rangs."),
                (" Stacks with other ranks.", " Se cumule avec les autres rangs."),
                (". Unique.", ". Unique."), (" Unique.", " Unique."), (". Unique", ". Unique"), (" Unique", " Unique"),
                (".", "."), ("", "")]
    if a.enchant_dbc and os.path.isfile(a.enchant_dbc):
        ench = lire_dbc(a.enchant_dbc, [(14, "s"), (11, "i")])
        for eid, (nom, arg) in sorted(ench.items()):
            m = re.match(r"^\s*@[Aa]ffixe?@(.*?)@[Aa]ffixe?@\s*$", nom, re.S)
            if not m:
                continue
            affix_obj["total"] += 1
            interieur = normaliser(m.group(1))       # texte tel que le client l'affiche
            ligne_fp = empreinte(interieur)
            fait = False
            # 1) effet d'un affixe connu (gabarit issu des traductions du launcher) + suffixe
            for sx_en, sx_fr in SUFFIXES:
                if sx_en and not ligne_fp.endswith(sx_en):
                    continue
                base = ligne_fp[:len(ligne_fp) - len(sx_en)] if sx_en else ligne_fp
                cle = base.rstrip(".").replace("\\'", "'")
                eff = effets_index.get(cle) or effets_index.get(cle.lower())
                if eff is None:
                    continue
                gf = (eff.rstrip(".") + sx_fr) if sx_en else eff
                if max_marqueur(gf) <= len(jetons(interieur)):
                    # « \' » du DBC : on ne sait pas si le client affiche l'antislash -> les deux
                    for variante in {ligne_fp, ligne_fp.replace("\\'", "'")}:
                        ajouter(variante, gf, CAT_AFFIX, eid, [t for _, _, t in jetons(interieur)], False)
                    fait = True
                break
            # 2) repli : anciennes traductions v3 (effet exact -> FR)
            if not fait:
                for sx_en, sx_fr in SUFFIXES:
                    if sx_en and not interieur.endswith(sx_en):
                        continue
                    corps = interieur[:-len(sx_en)] if sx_en else interieur
                    frc = ancien_effets.get(corps) or ancien_effets.get(corps.rstrip("."))
                    if frc and empreinte(frc) != empreinte(corps):
                        g = marquer_nombres(frc, [t for _, _, t in jetons(corps)]) + sx_fr
                        ajouter(ligne_fp, g, CAT_AFFIX, eid, [t for _, _, t in jetons(interieur)], False)
                        fait = True
                        affix_obj["repli_v3"] += 1
                        break
            # 3) traductions manuelles (quelques lignes sans sort d'affixe correspondant)
            if not fait:
                for variante in (ligne_fp, ligne_fp.replace("\\'", "'")):
                    g = AFFIXES_MANUELS.get(variante)
                    if g:
                        ajouter(ligne_fp, g, CAT_AFFIX, eid, [t for _, _, t in jetons(interieur)], False)
                        fait = True
                        affix_obj["manuel"] = affix_obj.get("manuel", 0) + 1
                        break
            if fait:
                affix_obj["gabarit_fr"] += 1
            elif len(exemples_echecs["affixes_objets"]) < 30:
                exemples_echecs["affixes_objets"].append({"enchant": eid, "texte": interieur[:200], "sort": arg})
    couverture["affixes_objets"] = affix_obj

    # --- objets « Tome of Echo: X » (ligne « Use: ... X: résumé »)
    tome_obj = {"total": 0, "complet": 0, "enrobage_seul": 0}
    tome_titres = {}
    anciens_items = {}
    if a.ancien and os.path.isfile(os.path.join(a.ancien, "tome_items.json")):
        anciens_items = json.load(open(os.path.join(a.ancien, "tome_items.json"), encoding="utf-8"))
    RE_USE = re.compile(r"^Use: Grants this character the ability to discover (.+?) when offered new Echoes\.(?: (.*))?$")
    for nom, v in (en.get("tomeItems") or {}).items():
        tome_obj["total"] += 1
        if v.get("itemId") and v.get("title"):
            tome_titres[int(v["itemId"])] = v["title"]
        tt = v.get("tooltip") or []
        use = next((normaliser(x) for x in tt if isinstance(x, str) and x.startswith("Use: ")), None)
        m = use and RE_USE.match(use)
        if not m:
            continue
        echo, reste = m.group(1), m.group(2) or ""
        toks_en = [t for _, _, t in jetons(use)]
        enrobage = "Utiliser : Permet \u00e0 ce personnage de d\u00e9couvrir %s parmi les Echoes propos\u00e9s." % echo
        k0 = len(jetons("Use: Grants this character the ability to discover %s when offered new Echoes." % echo))
        complet = ancien_tomes.get(echo)
        ancien_en = normaliser((anciens_items.get(echo) or {}).get("useFull") or "")
        if complet and reste and ancien_en == use:
            # ancienne traduction v3 encore valable (texte anglais identique)
            g = marquer_nombres(complet, toks_en, k0)
            tome_obj["complet"] += 1
        else:
            # enrobage traduit, résumé laissé en anglais (nombres repris de l'anglais affiché)
            g = enrobage + ((" " + marquer_nombres(reste, toks_en, k0)) if reste else "")
            tome_obj["enrobage_seul"] += 1
        ajouter(empreinte(use), g, CAT_TOME, v.get("itemId") or 0, toks_en, False)
    couverture["tomes_objets"] = tome_obj

    finaliser()

    # couverture par FORME réellement affichée en jeu
    for nom_cat, cat in (("perks", CAT_ECHO), ("skilltree", CAT_SOUL), ("affixes", CAT_AFFIX), ("tomes", CAT_TOME)):
        t = en.get(nom_cat) or {}
        n_desc = n_tt = 0
        for k, v in t.items():
            r = v.get("rendered")
            if r and empreinte(r) in fp_table:
                n_desc += 1
            tt = v.get("tooltip")
            if isinstance(tt, list) and any(isinstance(x, str) and empreinte(x) in fp_table for x in tt[1:]):
                n_tt += 1
        c = couverture[NOM_CAT[cat]]
        c["infobulle_du_sort"] = n_tt
        if nom_cat == "perks":
            c["GetSpellDescription"] = n_desc

    # --- vérification croisée avec la capture française (perks rendus par le patch FR)
    verif = {"compares": 0, "identiques": 0, "exemples_diff": []}
    if fr_dump:
        for k, v in (en.get("perks") or {}).items():
            fv = (fr_dump.get("perks") or {}).get(k)
            if not fv or not fv.get("rendered") or not v.get("rendered"):
                continue
            rn = normaliser(v["rendered"])
            e = fp_table.get(empreinte(rn))
            if not e:
                continue
            g = gabarits[e[0] - 1]
            res = remplir(g, [t for _, _, t in jetons(rn)])
            if res is None:
                continue
            verif["compares"] += 1
            ours = empreinte(RE_BLANCS.sub(" ", res))
            theirs = empreinte(fv["rendered"])
            if ours == theirs:
                verif["identiques"] += 1
            elif len(verif["exemples_diff"]) < 8:
                verif["exemples_diff"].append({"id": k, "addon": ours[:220], "patch": theirs[:220]})

    # --- interface
    ui_textes, ui_source, ui_infos = charger_ui(a.ui_fr)
    exact, motifs, morceaux, rejets = compiler_ui(ui_textes)

    # --- écriture des fichiers Lua
    os.makedirs(a.sortie, exist_ok=True)
    p_data = os.path.join(a.sortie, "EbonholdFR_Data.lua")
    with open(p_data, "w", encoding="utf-8", newline="\n") as f:
        f.write("-- EbonholdFR_Data.lua \u2014 G\u00c9N\u00c9R\u00c9 par tools/generer_donnees_v4.py (ne pas modifier \u00e0 la main)\n")
        f.write("-- Capture anglaise : %s \u2014 traductions : %s\n" % (os.path.basename(a.capture_en), os.path.basename(a.traductions)))
        f.write("-- t  = gabarits FR ({k} = k-i\u00e8me jeton du texte anglais affich\u00e9, {@k} = formule en vert)\n")
        f.write("-- fp = empreinte du texte anglais attendu -> index du gabarit * 10 + cat\u00e9gorie\n")
        f.write("--      (1 echoes, 2 Soul Tree, 3 affixes, 4 tomes)\n")
        f.write("-- id = id du sort -> { empreinte, index du gabarit }, quand le gabarit commun à l'empreinte ne lui convient pas\n")
        f.write("-- nom = id du sort -> nom anglais ; tomeItem = id de l'objet -> nom anglais\n")
        f.write("EbonholdFR_Data = { version = %s, t = {}, fp = {}, id = {}, nom = {}, tomeItem = {} }\n" % lua_str(VERSION_DONNEES))
        f.write("local t = EbonholdFR_Data.t\n")
        for i, g in enumerate(gabarits, 1):
            f.write("t[%d]=%s\n" % (i, lua_str(g)))
        f.write("local fp = EbonholdFR_Data.fp\n")
        for k in sorted(fp_table):
            i, cat, _ = fp_table[k]
            f.write("fp[%s]=%d\n" % (lua_str(k), i * 10 + cat))
        f.write("local id = EbonholdFR_Data.id\n")
        for sid in sorted(par_id):
            f.write("id[%d]={%s,%d}\n" % (sid, lua_str(par_id[sid][0]), par_id[sid][1]))
        f.write("local n = EbonholdFR_Data.nom\n")
        for sid in sorted(noms_en):
            f.write("n[%d]=%s\n" % (sid, lua_str(noms_en[sid])))
        f.write("local ti = EbonholdFR_Data.tomeItem\n")
        for iid in sorted(tome_titres):
            f.write("ti[%d]=%s\n" % (iid, lua_str(tome_titres[iid])))
    p_ui = os.path.join(a.sortie, "EbonholdFR_Interface_Data.lua")
    with open(p_ui, "w", encoding="utf-8", newline="\n") as f:
        f.write("-- EbonholdFR_Interface_Data.lua \u2014 G\u00c9N\u00c9R\u00c9 par tools/generer_donnees_v4.py (ne pas modifier \u00e0 la main)\n")
        f.write("-- Source : %s\n" % ui_source)
        f.write("-- exact = texte anglais exact -> fran\u00e7ais ; motifs = { motif Lua, remplacement, d\u00e9but } ;\n")
        f.write("-- morceaux = bouts de phrase coll\u00e9s par le code du serveur (\u00ab Stacks: \u00bb .. n)\n")
        f.write("EbonholdFR_InterfaceData = { source = %s, exact = {}, motifs = {}, morceaux = {} }\n" % lua_str(ui_source))
        f.write("local e = EbonholdFR_InterfaceData.exact\n")
        for k in sorted(exact):
            f.write("e[%s]=%s\n" % (lua_str(k), lua_str(exact[k])))
        f.write("local m = EbonholdFR_InterfaceData.motifs\n")
        for p, r, pre in motifs:
            f.write("m[#m+1]={%s,%s,%s}\n" % (lua_str(p), lua_str(r), lua_str(pre)))
        f.write("local o = EbonholdFR_InterfaceData.morceaux\n")
        for k in sorted(morceaux):
            f.write("o[%s]=%s\n" % (lua_str(k), lua_str(morceaux[k])))

    # --- rapport
    tailles = {os.path.basename(p): os.path.getsize(p) for p in (p_data, p_ui)}
    rapport = {
        "couverture": couverture,
        "gabarits": len(gabarits), "empreintes": len(fp_table), "traductions_divergentes": len(conflits),
        "gabarits_par_id": len(par_id), "divergences_sans_id": len(conflits_sans_id),
        "noms_anglais": len(noms_en), "tomes_objets_titres": len(tome_titres),
        "echecs": {NOM_CAT.get(k, k): dict(v) for k, v in echecs.items()},
        "verification_patch_fr": {k: v for k, v in verif.items() if k != "exemples_diff"},
        "interface": {"source": ui_source, "exact": len(exact), "motifs": len(motifs), "morceaux": len(morceaux),
                      "rejets": len(rejets), **ui_infos},
        "tailles_octets": tailles,
    }
    print(json.dumps(rapport, ensure_ascii=False, indent=1))
    if a.rapport:
        rapport["exemples_echecs"] = exemples_echecs
        rapport["exemples_conflits"] = conflits[:30]
        rapport["exemples_diff_patch"] = verif["exemples_diff"]
        rapport["rejets_interface"] = rejets[:60]
        json.dump(rapport, open(a.rapport, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("Rapport d\u00e9taill\u00e9 :", a.rapport)
    return 0


if __name__ == "__main__":
    sys.exit(main())
