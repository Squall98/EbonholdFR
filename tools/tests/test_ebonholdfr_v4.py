"""Tests hors jeu d'EbonholdFR 4.0 (LuaJIT via lupa, faux environnement WoW : faux_wow.lua).

  python test_ebonholdfr_v4.py            (avec un Python où « lupa » est installé)

Vérifie :
  * chargement « à vide » des fichiers de l'addon, dans l'ordre du .toc (avec / sans le serveur,
    avec / sans EbonholdFR_Reglages.lua) ;
  * empreinte et jetons : le Lua donne EXACTEMENT le même résultat que le générateur Python, sur
    toutes les descriptions de la capture anglaise ;
  * descriptions : GetSpellDescription traduit (texte complet puis coupe), laisse l'anglais si
    l'empreinte est inconnue, ne touche pas au texte du patch FR, mode patch ;
  * infobulles : liens de sorts, Soul Tree, affixes gravés (filtre + cache), tomes, ligne « EN : » ;
  * moteur d'interface : textes exacts, couleurs, motifs, morceaux, lignes multiples, inconnus ;
    parcours des fenêtres, accroche des FontString, cadres protégés ignorés, retour à l'anglais ;
    StaticPopup du serveur seulement ; collecte des textes non traduits ;
  * réglages : fichier du launcher, choix en jeu, changement côté launcher ;
  * mesures de coût (LuaJIT avec et sans compilation JIT).
"""
import json
import os
import re
import sys
import time
import traceback

from lupa import luajit21 as L

ICI = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(ICI)
DEPOT = os.path.dirname(TOOLS)
ADDON = os.path.join(DEPOT, "EbonholdFR")
sys.path.insert(0, TOOLS)
import generer_donnees_v4 as G  # noqa: E402

TOC = [l.strip() for l in open(os.path.join(ADDON, "EbonholdFR.toc"), encoding="utf-8")
       if l.strip() and not l.startswith("#")]
FAUX_WOW = open(os.path.join(ICI, "faux_wow.lua"), encoding="utf-8").read()

print("Lecture de la capture anglaise...")
DUMP = G.lire_sv(G.DEFAUTS["capture_en"])["EchoDumpDB"]
DUMP_FR = G.lire_sv(G.DEFAUTS["capture_fr"])["EchoDumpDB"] if os.path.isfile(G.DEFAUTS["capture_fr"]) else {}

SERVEUR = r"""
RENDU = {}
local function gsd(id, maxLength, stacks)
  if type(id) ~= "number" then error("Usage: GetSpellInfo(id)") end
  local d = RENDU[id]
  if not d then return "Click for details" end
  maxLength = maxLength or 100
  if #d > maxLength then d = d:sub(1, maxLength - 3) .. "..." end
  return d
end
utils = {
  GetSpellDescription = gsd,
  GetStackedSpellDescription = function(inst, maxLength) return gsd(inst[1].spellId, maxLength) end,
  GetSpellSearchText = function(id) return ((RENDU[id] or ""):gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", "")) end,
}
ProjectEbonhold = { ObjectivesUI = {}, ObjectivesService = {} }
for _, n in ipairs({ "skillTreeCurrentRankTooltip", "skillTreeNextRankTooltip", "skillTreeInfoTooltip",
                     "UtilsSpellTooltip" }) do
  CreateFrame("GameTooltip", n, nil, "GameTooltipTemplate")
end
EbonholdExtractionFrame = CreateFrame("Frame", "EbonholdExtractionFrame", UIParent)
EbonholdExtractionFrame.__shown = false
"""

RESULTATS = []


def test(nom):
    def deco(fn):
        RESULTATS.append((nom, fn))
        return fn
    return deco


def env(serveur=True, reglages=None, sans_fichier_reglages=False, interface_data=None, sv=None, locale="enUS"):
    """Nouveau Lua avec l'addon chargé ; reglages = texte Lua remplaçant EbonholdFR_Reglages."""
    lua = L.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(FAUX_WOW)
    lua.execute('FAUX.locale = "%s"' % locale)
    if serveur:
        lua.execute(SERVEUR)
        rendu = lua.eval("RENDU")
        for k, v in (DUMP.get("perks") or {}).items():
            if v.get("rendered"):
                rendu[int(k)] = v["rendered"]
    if sv:
        lua.execute(sv)
    for f in TOC:
        if f == "EbonholdFR_Reglages.lua":
            if sans_fichier_reglages:
                continue
            if reglages is not None:
                lua.execute(reglages)
                continue
        if f == "EbonholdFR_Interface_Data.lua" and interface_data is not None:
            lua.execute(interface_data)
            continue
        lua.globals().FAUX.charger(os.path.join(ADDON, f))
    lua.globals().FAUX.evenement("ADDON_LOADED", "EbonholdFR")
    lua.globals().FAUX.evenement("PLAYER_LOGIN")
    for _ in range(3):
        lua.globals().FAUX.tic(0.6)
    return lua


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


# ============================================================================ chargement
@test("chargement à vide : addon complet, serveur présent")
def t_charge():
    lua = env()
    check(lua.eval("type(EbonholdFR.TraduireDescription)") == "function", "API absente")
    check(lua.eval("utils._ebonholdFR4") is True, "utils non accroché")
    check(lua.eval("EbonholdFR.version") == "4.0", "version lue dans le .toc")
    check(lua.eval("SlashCmdList.EBONHOLDFR ~= nil"), "commande /efr")


@test("chargement à vide : sans l'addon du serveur (utils absent) ni fichier de réglages")
def t_charge_vide():
    lua = env(serveur=False, sans_fichier_reglages=True)
    for _ in range(25):
        lua.globals().FAUX.tic(1.0)
    check(lua.eval("EbonholdFR.ON.interface") is True, "défauts")
    check(lua.eval("EbonholdFR.ON.echoes_desc") is True, "défauts")
    lua.eval("SlashCmdList.EBONHOLDFR('')")
    lua.eval("SlashCmdList.EBONHOLDFR('stats')")
    lua.eval("SlashCmdList.EBONHOLDFR('test 200662')")
    lua.eval("SlashCmdList.EBONHOLDFR('inconnue')")


@test("chargement à vide : client frFR (globales de compatibilité)")
def t_charge_fr():
    lua = env(locale="frFR")
    check(lua.eval("ARMOR_COLON").replace(" ", " ") == "Armure :", "libellé FR")
    check(lua.eval("type(ToggleSpellBook)") == "function", "ToggleSpellBook recréé")


# ============================================================================ empreintes
@test("empreinte et jetons : Lua == Python sur toute la capture")
def t_empreintes():
    lua = env()
    fp_lua = lua.eval("EbonholdFR.empreinte")
    jet_lua = lua.eval("function(s) local t = EbonholdFR.jetons(EbonholdFR.normaliser(s)); return table.concat(t, '\\1') end")
    n = 0
    for cat in ("perks", "skilltree", "affixes", "tomes"):
        for k, v in (DUMP.get(cat) or {}).items():
            textes = [v.get("rendered"), v.get("desc")] + [x for x in (v.get("tooltip") or [])[1:] if isinstance(x, str)]
            for t in textes:
                if not t:
                    continue
                n += 1
                check(fp_lua(t) == G.empreinte(t), "empreinte %s %s : %r != %r" % (cat, k, fp_lua(t), G.empreinte(t)))
                check(jet_lua(t) == "\1".join(x for _, _, x in G.jetons(G.normaliser(t))), "jetons %s %s" % (cat, k))
    for t in ["@ sans fin 12", "1.5.3 et 12. fin", "|cff2cfe3212.5|r dégâts @sp0.1+ap0.05@ x", "  a\r\n\r\n b  "]:
        check(fp_lua(t) == G.empreinte(t), "cas limite %r" % t)
    print("      %d textes comparés" % n)


# ============================================================================ descriptions
def attendu(lua, texte):
    """Traduction attendue, calculée en Python à partir des tables Lua générées."""
    d = lua.globals().EbonholdFR_Data
    fp = G.empreinte(texte)
    v = d.fp[fp]
    if v is None:
        return None
    g = d.t[int(v) // 10]
    return G.remplir(g, [t for _, _, t in G.jetons(G.normaliser(texte))])


@test("GetSpellDescription : toutes les echoes traduites, identiques au calcul Python")
def t_gsd():
    lua = env()
    gsd = lua.eval("utils.GetSpellDescription")
    ok = 0
    for k, v in DUMP["perks"].items():
        r = v.get("rendered")
        if not r or r == "Click for details":
            continue
        fr = gsd(int(k), 4000, 1)
        exp = attendu(lua, r)
        check(exp is not None, "pas de gabarit pour %s" % k)
        exp = re.sub(r"[ \t\n\r\f\v]+", " ", exp)
        check(fr == exp, "%s : %r != %r" % (k, fr[:120], exp[:120]))
        check("{" not in fr and "|cff2cfe32|r" not in fr, "marqueur ou nombre vide %s" % k)
        ok += 1
    print("      %d descriptions d'echoes" % ok)


@test("GetSpellDescription(id, 120) : texte complet demandé puis français coupé proprement")
def t_troncature():
    lua = env()
    gsd = lua.eval("utils.GetSpellDescription")
    longs = 0
    for k, v in DUMP["perks"].items():
        r = v.get("rendered") or ""
        if len(r) < 200:
            continue
        fr = gsd(int(k), 120)
        check(fr.endswith("..."), "coupé : %s" % k)
        check(len(fr) <= 159, "longueur %d" % len(fr))
        check(fr.count("|c") <= fr.count("|r"), "couleur ouverte %s : %r" % (k, fr))
        check("|cff2cfe32|r" not in fr, "nombre vide %s" % k)
        fr.encode("utf-8")
        longs += 1
    check(longs > 50, "assez de cas")
    print("      %d descriptions longues coupées" % longs)


@test("descriptions : anglais inconnu / texte du patch FR / mode patch -> laissés tels quels")
def t_passthrough():
    lua = env()
    rendu = lua.eval("RENDU")
    gsd = lua.eval("utils.GetSpellDescription")
    pid, v = next((k, v) for k, v in DUMP["perks"].items() if len(v.get("rendered") or "") > 60)
    pid = int(pid)
    modif = v["rendered"].replace(" ", " totally new ", 1)
    rendu[pid] = modif
    check(gsd(pid, 4000) == modif, "texte modifié par le serveur -> anglais")
    n = anglais = 0
    fps = lua.globals().EbonholdFR_Data.fp
    for k, fv in (DUMP_FR.get("perks") or {}).items():
        if fv.get("rendered"):
            if fps[G.empreinte(fv["rendered"])] is not None:
                anglais += 1          # le patch n'a pas traduit ce texte : il est encore en anglais
                continue
            rendu[int(k)] = fv["rendered"]
            check(gsd(int(k), 4000) == fv["rendered"], "texte du patch FR modifié : %s" % k)
            n += 1
    print("      %d textes du patch FR laissés intacts (%d restés en anglais dans le patch : traduits)" % (n, anglais))
    # appel « utils.GetSpellDescription(utils, id) » du serveur (sous pcall) : même erreur qu'avant
    check(lua.eval("(pcall(utils.GetSpellDescription, utils, 500, 1))") is False, "erreur d'origine conservée")
    lua2 = env(reglages="EbonholdFR_Reglages = { version = 1, patch = true }")
    r = DUMP["perks"][str(pid)]["rendered"] if str(pid) in DUMP["perks"] else v["rendered"]
    check(lua2.eval("utils.GetSpellDescription")(pid, 4000) == r, "mode patch : anglais d'origine")
    check(lua2.eval("EbonholdFR.ON.interface") is True and lua2.eval("EbonholdFR.ON.echoes_desc") is False, "patch")


@test("recherche du journal : anglais + français cherchables")
def t_recherche():
    lua = env()
    k, v = next((k, v) for k, v in DUMP["perks"].items() if v.get("rendered"))
    s = lua.eval("utils.GetSpellSearchText")(int(k))
    check(s.startswith(G.normaliser(v["rendered"])), "anglais d'abord")
    check(len(s) > len(G.normaliser(v["rendered"])) + 10, "français ajouté")


# ============================================================================ infobulles
def remplir_sorts(lua, cat):
    s = lua.globals().FAUX.SORTS
    n = 0
    for k, v in (DUMP.get(cat) or {}).items():
        tt = v.get("tooltip")
        if isinstance(tt, list) and len(tt) >= 2:
            s[int(k)] = lua.table_from([x for x in tt if isinstance(x, str)])
            n += 1
    return n


@test("infobulles : liens de sorts (echoes, Soul Tree) traduits par empreinte")
def t_liens():
    lua = env()
    remplir_sorts(lua, "perks")
    remplir_sorts(lua, "skilltree")
    tr = 0
    for cat, tt_nom in (("perks", "ItemRefTooltip"), ("skilltree", "skillTreeCurrentRankTooltip")):
        tt = lua.globals()[tt_nom]
        for k, v in list((DUMP.get(cat) or {}).items())[:300]:
            tt.SetHyperlink(tt, "spell:%s" % k)
            tt.Show(tt)
            lignes = [lua.globals()["%sTextLeft%d" % (tt_nom, i)].GetText(lua.globals()["%sTextLeft%d" % (tt_nom, i)])
                      for i in range(1, tt.NumLines(tt) + 1)]
            anglais = [x for x in v["tooltip"][1:] if isinstance(x, str) and len(x) > 12]
            for i, l in enumerate(lignes[1:], 2):
                if l and len(l) > 12:
                    check(l not in anglais or G.empreinte(l) not in lua.globals().EbonholdFR_Data.fp,
                          "ligne restée en anglais %s %s : %r" % (cat, k, l[:80]))
            tr += 1
        if cat == "skilltree":
            check(all(len(x) <= 70 for l in lignes if l for x in l.split("\n")), "retour à la ligne Soul Tree")
    print("      %d infobulles" % tr)


@test("infobulles d'objets : affixe gravé (filtre + cache), tome, ligne EN")
def t_objets():
    lua = env()
    obj = lua.globals().FAUX.OBJETS
    # une ligne d'affixe telle que l'affiche le serveur (violet) + une ligne quelconque
    ligne ="|cffb048f8Increases your total Strength by 6%. Stacks with other ranks.|r"
    obj[123] = lua.table_from(["Belt of Testing", "Durability 20 / 20", ligne])
    gt = lua.globals().GameTooltip
    gt.SetHyperlink(gt, "item:123")
    l3 = lua.globals().GameTooltipTextLeft3.GetText(lua.globals().GameTooltipTextLeft3)
    l2 = lua.globals().GameTooltipTextLeft2.GetText(lua.globals().GameTooltipTextLeft2)
    check(l2 == "Durability 20 / 20", "ligne non marquée intacte")
    check(l3.startswith("|cffb048f8Augmente") and "6" in l3 and l3.endswith("|r"), "affixe traduit : %r" % l3)
    check(lua.eval("next(EbonholdFR.ON) ~= nil"), "")
    # tome
    tid, tv = next((k, v) for k, v in DUMP["tomeItems"].items() if v.get("itemId"))
    lignes = [x for x in tv["tooltip"] if isinstance(x, str)]
    obj[int(tv["itemId"])] = lua.table_from(["Tome d'écho : %s" % tid] + lignes[1:])
    gt.SetHyperlink(gt, "item:%d" % int(tv["itemId"]))
    textes = [lua.globals()["GameTooltipTextLeft%d" % i].GetText(lua.globals()["GameTooltipTextLeft%d" % i])
              for i in range(1, gt.NumLines(gt) + 1)]
    check(any(t and t.startswith("Utiliser") for t in textes), "ligne Use: traduite : %r" % textes)
    check(textes[-1] == "EN : " + tv["title"], "ligne EN du tome : %r" % textes[-1])


@test("ligne « EN : » (noms traduits par le patch) ajoutée une fois, en bas, à l'image suivante")
def t_nom_anglais():
    lua = env(reglages="EbonholdFR_Reglages = { version = 1, patch = true, nom_anglais = true }")
    noms = lua.globals().FAUX.NOMS
    k, v = next((k, v) for k, v in DUMP["skilltree"].items())
    noms[int(k)] = "Nom Français"
    lua.execute("EbonholdFR_Data.nom[%d] = %s" % (int(k), json.dumps(v["name"])))
    lua.globals().FAUX.SORTS[int(k)] = lua.table_from(["Nom Français", "Description française du patch."])
    tt = lua.globals().skillTreeCurrentRankTooltip
    tt.SetHyperlink(tt, "spell:%s" % k)
    tt.AddLine(tt, "Rank: 1/3")
    tt.Show(tt)
    tt.Show(tt)
    lua.globals().FAUX.tic(0.02)
    n = tt.NumLines(tt)
    der = lua.globals()["skillTreeCurrentRankTooltipTextLeft%d" % n]
    check(der.GetText(der) == "EN : " + v["name"], "ligne EN en bas : %r" % der.GetText(der))
    l2 = lua.globals().skillTreeCurrentRankTooltipTextLeft2
    check(l2.GetText(l2) == "Description française du patch.", "texte du patch intact")
    tt.Show(tt)
    lua.globals().FAUX.tic(0.02)
    check(tt.NumLines(tt) == n, "pas de doublon")


# ============================================================================ moteur d'interface
DONNEES_UI = r"""
EbonholdFR_InterfaceData = { exact = {
  ["Apply Changes"] = "Appliquer les changements",
  ["Left-click to learn"] = "Clic gauche pour apprendre",
  ["Choose an Affix"] = "Choisir un affixe",
  ["Current Objective"] = "Objectif actuel",
  ["decays over time."] = "diminue avec le temps.",
}, motifs = {
  { "^(%-?%d+) slots$", "%1 emplacements", "" },
  { "^%+(%-?[%d%.]+)%% Soul Ashes$", "+%1%% de Cendres d'\195\162me", "+" },
  { "^Rank: (%-?%d+)/(%-?%d+)$", "Rang : %1/%2", "Ran" },
}, morceaux = {
  ["Remaining Soul Ashes: "] = "Cendres d'\195\162me restantes : ",
  [" Soul Ash"] = " Cendre d'\195\162me",
  ["Cost of Next Resurrection: "] = "Co\195\187t de la prochaine r\195\169surrection : ",
  ["Intensity rises; it "] = "L'intensit\195\169 monte ; elle ",
  ["Level "] = "Niveau ",
} }
"""


@test("moteur d'interface : exact, couleur, motifs, morceaux, lignes, inconnus")
def t_moteur():
    lua = env(interface_data=DONNEES_UI)
    tr = lua.eval("EbonholdFR.Interface.traduire")
    cas = {
        "Apply Changes": "Appliquer les changements",
        "  Apply Changes ": "  Appliquer les changements ",
        "|cff00FF00Left-click to learn|r": "|cff00FF00Clic gauche pour apprendre|r",
        "12 slots": "12 emplacements",
        "+30% Soul Ashes": "+30% de Cendres d'âme",
        "\n|cff00FF00Rank: 1/3|r": "\n|cff00FF00Rang : 1/3|r",
        "Remaining Soul Ashes: 1,234": "Cendres d'âme restantes : 1,234",
        "Cost of Next Resurrection: 12 Soul Ash": "Coût de la prochaine résurrection : 12 Cendre d'âme",
        "Intensity rises; it decays over time.": "L'intensité monte ; elle diminue avec le temps.",
        "Choose an Affix\nCurrent Objective": "Choisir un affixe\nObjectif actuel",
        "Level 12": "Niveau 12",
    }
    for en, fr in cas.items():
        check(tr(en) == fr, "%r -> %r (attendu %r)" % (en, tr(en), fr))
    for inconnu in ["Totally unknown text", "12/30", "", "|cffffffff|Hitem:1|h[Apply Changes]|h|r",
                    "Level up to unlock the hidden chest now"]:
        check(tr(inconnu) is None, "inconnu traduit : %r -> %r" % (inconnu, tr(inconnu)))


@test("moteur d'interface : données réelles (exact + motifs compilables et appliqués)")
def t_moteur_reel():
    lua = env()
    tr = lua.eval("EbonholdFR.Interface.traduire")
    data = lua.globals().EbonholdFR_InterfaceData
    n = 0
    for k, v in data.exact.items():
        r = tr(k)
        check(r is not None, "exact non traduit : %r" % k)
        n += 1
    m = 0
    for i in range(1, len(data.motifs) + 1):
        p = data.motifs[i]
        lua.eval("function(p, r) return (string.gsub('test 12 abc', p, r)) end")(p[1], p[2])  # motif valide
        m += 1
    # chaque texte « format » de ui-fr.json, rempli comme le ferait le serveur, doit être reconnu
    a = 0
    if os.path.isfile(G.DEFAUTS["ui_fr"]):
        textes, _, _ = G.charger_ui(G.DEFAUTS["ui_fr"])
        for en0, fr0 in textes.items():
            en, fr = G.decoder_lua(en0), G.decoder_lua(fr0)
            if en == fr or "|H" in en or not [x for x in G.RE_SPEC.findall(en) if x != "%%"]:
                continue
            if not G.motif_lua_depuis_format(en.strip(" \t\n\r"), fr.strip(" \t\n\r")):
                continue
            vals = iter(["12", "3", "7", "9", "4", "5", "6", "8", "11"])
            exemple = G.RE_SPEC.sub(lambda mm: "%" if mm.group(0) == "%%" else
                                    ("2.5" if mm.group(0)[-1] in "fg" else
                                     ("Xyz" if mm.group(0)[-1] == "s" else next(vals))), en)
            r = tr(exemple)
            check(r is not None and r != exemple, "format non reconnu : %r" % exemple[:100])
            a += 1
    print("      %d textes exacts, %d motifs valides, %d textes « format » reconnus une fois remplis" % (n, m, a))


def fenetre(lua):
    """Fausse fenêtre du serveur : 3 niveaux, FontString, bouton, cadre protégé, champ de saisie."""
    lua.execute(r"""
      local f = CreateFrame("Frame", "ProjectEbonholdEchoJournal", UIParent)
      f.__shown = false
      local titre = f:CreateFontString(nil); titre:SetText("Apply Changes")
      local a = CreateFrame("Frame", nil, f)
      local b = CreateFrame("Button", nil, a); b:SetText("Choose an Affix")
      local prot = CreateFrame("Frame", nil, a); prot.__protege = true
      local fsProt = prot:CreateFontString(nil); fsProt:SetText("Apply Changes")
      local eb = CreateFrame("EditBox", nil, a)
      local inc = a:CreateFontString(nil); inc:SetText("Something new from the server")
      TEST = { f = f, titre = titre, b = b, fsProt = fsProt, inc = inc, a = a }
    """)


@test("fenêtres : repérage, parcours, accroche SetText, cadres protégés ignorés, retour à l'anglais")
def t_fenetres():
    lua = env(interface_data=DONNEES_UI)
    fenetre(lua)
    lua.globals().FAUX.tic(0.6)                         # la veille trouve la racine
    T = lua.globals().TEST
    check(T.titre.GetText(T.titre) == "Apply Changes", "pas encore affichée")
    T.f.Show(T.f)                                        # OnShow -> parcours
    check(T.titre.GetText(T.titre) == "Appliquer les changements", "titre traduit")
    check(T.b.GetText(T.b) == "Choisir un affixe", "bouton traduit")
    check(T.fsProt.GetText(T.fsProt) == "Apply Changes", "cadre protégé ignoré")
    check(T.inc.GetText(T.inc) == "Something new from the server", "inconnu intact")
    T.titre.SetText(T.titre, "Current Objective")      # mise à jour suivie par le hook
    check(T.titre.GetText(T.titre) == "Objectif actuel", "SetText suivi")
    T.b.SetText(T.b, "Apply Changes")
    check(T.b.GetText(T.b) == "Appliquer les changements", "SetText du bouton suivi")
    # nouvel enfant créé fenêtre ouverte -> attrapé par la veille
    lua.execute('local x = TEST.a:CreateFontString(nil); x:SetText("Apply Changes"); TEST.x = x')
    lua.globals().FAUX.tic(1.1)
    check(T.x.GetText(T.x) == "Appliquer les changements", "nouvel enfant traduit par la veille")
    # interface coupée -> anglais d'origine
    lua.eval("EbonholdFR.SetChoix('interface', false)")
    check(T.titre.GetText(T.titre) == "Current Objective", "retour à l'anglais : %r" % T.titre.GetText(T.titre))
    T.titre.SetText(T.titre, "Apply Changes")
    check(T.titre.GetText(T.titre) == "Apply Changes", "plus de traduction quand coupé")
    lua.eval("EbonholdFR.SetChoix('interface', true)")
    check(T.titre.GetText(T.titre) == "Appliquer les changements", "remis en français")


@test("infobulle d'un cadre du serveur traduite ; infobulle d'un autre cadre ignorée")
def t_tt_interface():
    lua = env(interface_data=DONNEES_UI)
    fenetre(lua)
    lua.globals().FAUX.tic(0.6)
    T = lua.globals().TEST
    T.f.Show(T.f)
    gt = lua.globals().GameTooltip
    gt.SetOwner(gt, T.b, "ANCHOR_RIGHT")
    gt.AddLine(gt, "Apply Changes")
    gt.AddDoubleLine(gt, "Current Objective", "12 slots")
    gt.Show(gt)
    l1, l2, r2 = (lua.globals()[n] for n in ("GameTooltipTextLeft1", "GameTooltipTextLeft2", "GameTooltipTextRight2"))
    check(l1.GetText(l1) == "Appliquer les changements" and l2.GetText(l2) == "Objectif actuel"
          and r2.GetText(r2) == "12 emplacements", "lignes traduites")
    gt.SetOwner(gt, lua.globals().UIParent, "ANCHOR_RIGHT")
    gt.AddLine(gt, "Apply Changes")
    gt.Show(gt)
    check(l1.GetText(l1) == "Apply Changes", "propriétaire hors serveur : intact")


@test("StaticPopup : boîte du serveur traduite, boîte de Blizzard intacte")
def t_popup():
    lua = env(interface_data=DONNEES_UI)
    p, t, b1 = lua.globals().StaticPopup1, lua.globals().StaticPopup1Text, lua.globals().StaticPopup1Button1
    p.which = "PROJECTEBONHOLD_LOADOUT_DELETE"
    t.SetText(t, "Apply Changes"); b1.SetText(b1, "Choose an Affix")
    p.Show(p)
    check(t.GetText(t) == "Appliquer les changements" and b1.GetText(b1) == "Choisir un affixe", "popup serveur")
    p.Hide(p)
    p.which = "DELETE_ITEM"
    t.SetText(t, "Apply Changes")
    p.Show(p)
    check(t.GetText(t) == "Apply Changes", "popup Blizzard intacte")


@test("collecte des textes non traduits (/efr collecte)")
def t_collecte():
    lua = env(interface_data=DONNEES_UI)
    fenetre(lua)
    lua.globals().FAUX.tic(0.6)
    T = lua.globals().TEST
    check(lua.eval("EbonholdFR_Collecte.actif") is False, "désactivée par défaut")
    T.f.Show(T.f)
    check(lua.eval("EbonholdFR_Collecte.n") == 0, "rien noté quand coupée")
    lua.eval("SlashCmdList.EBONHOLDFR('collecte')")
    check(lua.eval("EbonholdFR_Collecte.actif") is True, "activée")
    T.inc.SetText(T.inc, "Save to my builds")
    T.inc.SetText(T.inc, "Save to my builds")
    T.inc.SetText(T.inc, "12/30")              # nombre seul : ignoré
    T.inc.SetText(T.inc, "Squall")             # nom du joueur : ignoré
    T.inc.SetText(T.inc, "Apply Changes")      # connu : pas noté
    T.inc.SetText(T.inc, "Déjà en français")
    e = lua.eval("EbonholdFR_Collecte.textes['Save to my builds']")
    check(e is not None and e.n == 2 and e.ou == "ProjectEbonholdEchoJournal", "entrée notée : n=2, ou=cadre")
    check(lua.eval("EbonholdFR_Collecte.n") == 1, "une seule entrée : %r" % lua.eval("EbonholdFR_Collecte.n"))
    gt = lua.globals().GameTooltip
    gt.SetOwner(gt, T.b, "ANCHOR_RIGHT"); gt.AddLine(gt, "Keep Name"); gt.Show(gt)
    check(lua.eval("EbonholdFR_Collecte.textes['Keep Name'] ~= nil"), "infobulle du serveur notée")
    lua.execute("for i = 1, 3100 do EbonholdFR.Interface.noter('Texte numero ' .. i .. ' xx', nil) end")
    check(lua.eval("EbonholdFR_Collecte.n") == 3000, "plafond 3000")
    lua.eval("SlashCmdList.EBONHOLDFR('collecte vider')")
    check(lua.eval("EbonholdFR_Collecte.n") == 0, "vidée")
    lua.eval("SlashCmdList.EBONHOLDFR('collecte')")
    check(lua.eval("EbonholdFR_Collecte.actif") is False, "recoupée")
    # état conservé : SavedVariable rechargée active
    lua2 = env(interface_data=DONNEES_UI, sv="EbonholdFR_Collecte = { actif = true, n = 1, textes = { Share = { n = 4 } } }")
    check(lua2.eval("EbonholdFR_Collecte.actif") is True and lua2.eval("EbonholdFR_Collecte.n") == 1, "état gardé")


# ============================================================================ réglages
@test("réglages : fichier du launcher, chaînes fr/en, choix en jeu, changement côté launcher")
def t_reglages():
    lua = env(reglages='EbonholdFR_Reglages = { version = 1, interface = "en", echoes_desc = "fr", tomes = false }')
    check(lua.eval("EbonholdFR.ON.interface") is False and lua.eval("EbonholdFR.ON.echoes_desc") is True
          and lua.eval("EbonholdFR.ON.tomes") is False, "valeurs du launcher")
    lua.eval("EbonholdFR.SetChoix('tomes', true)")
    check(lua.eval("EbonholdFR.ON.tomes") is True and lua.eval("EbonholdFRDB.choix.tomes") is True, "choix en jeu")
    # nouvelle session, même fichier : le choix en jeu reste
    sv = "EbonholdFRDB = { v = 4, enabled = true, choix = { tomes = true }, minimap = {}, sigReglages = %s }" % \
        json.dumps(lua.eval("EbonholdFRDB.sigReglages"))
    lua2 = env(reglages='EbonholdFR_Reglages = { version = 1, interface = "en", echoes_desc = "fr", tomes = false }', sv=sv)
    check(lua2.eval("EbonholdFR.ON.tomes") is True, "choix en jeu conservé")
    # le launcher change ses réglages : ils reprennent la main
    lua3 = env(reglages='EbonholdFR_Reglages = { version = 1, interface = true, tomes = false, nom_anglais = false }', sv=sv)
    check(lua3.eval("EbonholdFR.ON.tomes") is False and lua3.eval("next(EbonholdFRDB.choix) == nil"), "launcher prioritaire")
    # ancienne base v3 migrée (position du bouton gardée)
    lua4 = env(sv="EbonholdFRDB = { enabled = false, cat = { echoes = false }, minimap = { angle = 42 } }")
    check(lua4.eval("EbonholdFRDB.minimap.angle") == 42 and lua4.eval("EbonholdFRDB.cat") is None, "migration v3")
    # interrupteur général
    lua.execute("EbonholdFRDB.enabled = false; EbonholdFR.Rafraichir()")
    check(lua.eval("EbonholdFR.ON.echoes_desc") is False and lua.eval("EbonholdFR.ON.interface") is False, "tout en anglais")


@test("forge en français : ouvre la fenêtre du serveur, nom anglais ignoré")
def t_forge():
    lua = env()
    lua.execute('GossipFrameNpcNameText:SetText("Enclume enchant\\195\\169e"); GossipFrame.__shown = true')
    lua.globals().FAUX.evenement("GOSSIP_SHOW")
    check(lua.eval("EbonholdExtractionFrame:IsShown()") is True, "forge ouverte")
    lua.globals().FAUX.evenement("GOSSIP_CLOSED")
    check(lua.eval("EbonholdExtractionFrame:IsShown()") is False, "forge refermée avec le dialogue")
    lua.execute('GossipFrameNpcNameText:SetText("Enchanted Anvil")')
    lua.globals().FAUX.evenement("GOSSIP_SHOW")
    check(lua.eval("EbonholdExtractionFrame:IsShown()") is False, "nom anglais : le serveur s'en charge")


# ============================================================================ coûts
def memoire_addon():
    """Mémoire Lua occupée par l'addon chargé (données comprises), en Ko."""
    lua = L.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(FAUX_WOW)
    lua.execute(SERVEUR)
    lua.execute("collectgarbage('collect'); collectgarbage('collect')")
    avant = lua.eval("collectgarbage('count')")
    for f in TOC:
        lua.globals().FAUX.charger(os.path.join(ADDON, f))
    lua.globals().FAUX.evenement("ADDON_LOADED", "EbonholdFR")
    lua.globals().FAUX.evenement("PLAYER_LOGIN")
    lua.execute("collectgarbage('collect'); collectgarbage('collect')")
    return lua.eval("collectgarbage('count')") - avant


@test("mesures de coût")
def t_couts():
    for jit in (True, False):
        lua = env(interface_data=None)
        if not jit:
            lua.execute("jit.off()")
        mode = "JIT" if jit else "interprété"
        gsd = lua.eval("utils.GetSpellDescription")
        ids = [int(k) for k, v in DUMP["perks"].items() if v.get("rendered")]
        lua.execute("IDS = {%s}" % ",".join(map(str, ids)))
        r = lua.eval("""function(n)
          local t0 = os.clock()
          for _ = 1, n do for _, id in ipairs(IDS) do utils.GetSpellDescription(id, 500, 1) end end
          return (os.clock() - t0) / (n * #IDS) * 1e6 end""")
        froid = r(1)
        chaud = r(5)
        rr = lua.eval("""function(n)
          local tr, ex, t0 = EbonholdFR.Interface.traduire, EbonholdFR_InterfaceData.exact, os.clock()
          local k = 0
          for _ = 1, n do for en in pairs(ex) do tr(en); k = k + 1 end end
          return (os.clock() - t0) / k * 1e6 end""")
        ui = rr(3)
        mm = lua.eval("""function()
          local tr, t0, k = EbonholdFR.Interface.traduire, os.clock(), 0
          for i = 1, 3000 do tr('Remaining Soul Ashes: ' .. i); tr('Unknown server text number ' .. i); k = k + 2 end
          return (os.clock() - t0) / k * 1e6 end""")()
        w = lua.eval("""function(n)
          local root = CreateFrame("Frame", "ProjectEbonholdTestRoot", UIParent)
          for i = 1, n do
            local c = CreateFrame("Button", nil, root)
            local fs = c:CreateFontString(nil); fs:SetText(i % 2 == 0 and "Apply Changes" or ("Valeur " .. i))
          end
          local P = EbonholdFR.Interface.parcourir
          local t0 = os.clock(); FAUX.temps = FAUX.temps + 1; P(root, 0); local premier = os.clock() - t0
          t0 = os.clock()
          for _ = 1, 50 do FAUX.temps = FAUX.temps + 1; P(root, 0) end
          local second = (os.clock() - t0) / 50
          local fs = { root.__children[2]:GetRegions() }
          t0 = os.clock(); for i = 1, 10000 do fs[2]:SetText("Apply Changes") end
          local st = (os.clock() - t0) / 10000
          return premier * 1000, second * 1000, st * 1e6 end""")
        p1, p2, st = w(1000)
        mem = memoire_addon()
        print("      [%s] GetSpellDescription : %.1f µs/appel (1er passage), %.1f µs (cache) | interface : "
              "%.2f µs/texte exact, %.1f µs/texte nouveau (motif ou inconnu) | parcours 1000 boutons : "
              "%.1f ms puis %.2f ms | SetText accroché : %.2f µs | mémoire de l'addon : %.0f Ko"
              % (mode, froid, chaud, ui, mm, p1, p2, st, mem))


# ============================================================================
def main():
    ok = ko = 0
    for nom, fn in RESULTATS:
        try:
            t0 = time.time()
            fn()
            ok += 1
            print("ok    %s (%.1f s)" % (nom, time.time() - t0))
        except Exception as e:  # noqa: BLE001
            ko += 1
            print("ECHEC %s : %s" % (nom, e))
            traceback.print_exc(limit=3)
    print("\n%d tests réussis, %d échec(s)" % (ok, ko))
    return 1 if ko else 0


if __name__ == "__main__":
    sys.exit(main())
