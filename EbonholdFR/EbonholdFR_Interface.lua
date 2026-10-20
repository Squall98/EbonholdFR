--[[ EbonholdFR 4.0 — traduction EN DIRECT de l'interface de ProjectEbonhold (addon du serveur).

  Données : EbonholdFR_InterfaceData (généré) = exact {anglais = français}, motifs {motif, rempl.},
            morceaux {bout de phrase anglais = français} (phrases que le serveur colle avec une valeur).

  Comment les fenêtres du serveur sont repérées et traduites :
    1. RACINES : cadres nommés de l'addon du serveur (liste connue + tout nom global qui commence
       par un préfixe du serveur : ProjectEbonhold*, Ebonhold*, skillTree*, Hardmode*...). Une
       veille légère (toutes les 0,5 s tant qu'il en manque, puis balayage de _G de temps en temps)
       attrape les fenêtres créées tard (tableau des objectifs, forge...).
    2. À l'affichage d'une racine (HookScript OnShow : ce sont des cadres NON sécurisés de l'addon),
       on parcourt ses régions et enfants (GetRegions / GetChildren). Chaque FontString rencontrée
       est traduite puis accrochée UNE fois : hooksecurefunc(fs, "SetText") (méthode de CET objet,
       pas de hook global) pour suivre ses mises à jour ; idem pour le SetText des boutons.
       Les cadres protégés (IsProtected) sont ignorés, ainsi que les champs de saisie et les modèles.
    3. Infobulles : après chaque Show de GameTooltip dont le propriétaire appartient à une fenêtre du
       serveur (et des infobulles créées par le serveur), les lignes connues sont traduites.
    4. Fenêtres de confirmation du serveur (StaticPopupDialogs du serveur) : méthode Show des cadres
       StaticPopup1..4, seulement si la boîte affichée est une boîte du serveur.
  Texte inconnu -> il reste en anglais. Coût : cache des traductions, tables faibles pour les objets
  déjà accrochés, parcours incrémental (on ne relit que les cadres dont le nombre d'enfants change).

  Collecte (/efr collecte) : note les textes anglais NON traduits rencontrés à ces mêmes points
  d'accroche dans la SavedVariable EbonholdFR_Collecte = { actif, n, textes = { [texte] = { n, ou } } }.
]]

local E = EbonholdFR
if not E then return end
local ON = E.ON

local DATA = EbonholdFR_InterfaceData or {}
local EXACT = DATA.exact or {}
local MORCEAUX = DATA.morceaux or {}
local MOTIFS = DATA.motifs or {}

local find, sub, gsub, match, gmatch, len = string.find, string.sub, string.gsub, string.match, string.gmatch, string.len
local concat, type, pairs, ipairs, pcall, tostring = table.concat, type, pairs, ipairs, pcall, tostring

local I = {}
E.Interface = I

------------------------------------------------------------------------
-- 1) MOTEUR DE TRADUCTION (fonctions pures)
------------------------------------------------------------------------
-- index des motifs par leurs 3 premiers caractères littéraux ; ceux qui commencent par une
-- valeur (« %d slots ») sont essayés à chaque fois
local motifsPar, motifsLibres = {}, {}
for _, m in ipairs(MOTIFS) do
  local pre = m[3] or ""
  if len(pre) >= 3 then
    local l = motifsPar[pre]
    if not l then l = {}; motifsPar[pre] = l end
    l[#l + 1] = m
  else
    motifsLibres[#motifsLibres + 1] = m
  end
end

-- index des morceaux par leurs 3 premiers octets, du plus long au plus court
local morceauxPar = {}
for en, fr in pairs(MORCEAUX) do
  local k = sub(en, 1, 3)
  local l = morceauxPar[k]
  if not l then l = {}; morceauxPar[k] = l end
  l[#l + 1] = { en, fr }
end
for _, l in pairs(morceauxPar) do table.sort(l, function(a, b) return len(a[1]) > len(b[1]) end) end

local LETTRE = "[%a\128-\255]"

-- lettres hors codes de couleur et textures (« |TInterface\...|t » n'est pas du texte)
local function nbLettres(s)
  s = gsub(s, "|c%x%x%x%x%x%x%x%x", "")
  s = gsub(s, "|r", "")
  s = gsub(s, "|T.-|t", "")
  local _, n = gsub(s, LETTRE, "")
  return n
end

local function essayerMotifs(s)
  local l = motifsPar[sub(s, 1, 3)]
  if l then
    for i = 1, #l do
      local r, n = gsub(s, l[i][1], l[i][2], 1)
      if n > 0 then return r end
    end
  end
  for i = 1, #motifsLibres do
    local r, n = gsub(s, motifsLibres[i][1], motifsLibres[i][2], 1)
    if n > 0 then return r end
  end
end

local function morceauA(s, pos)
  local l = morceauxPar[sub(s, pos, pos + 2)]
  if not l then return nil end
  for i = 1, #l do
    local en = l[i][1]
    if sub(s, pos, pos + len(en) - 1) == en then return en, l[i][2] end
  end
end

-- reconstitue une phrase faite de morceaux connus + valeurs (nombres, couleurs, noms) ;
-- refusé si moins de 60 % des lettres sont couvertes par des morceaux connus
local function assembler(s)
  local total = nbLettres(s)
  if total == 0 then return nil end
  local pos, n, out, connus, traduit, mots = 1, len(s), {}, 0, 0, 0
  while pos <= n do
    local en, fr = morceauA(s, pos)
    if en then
      out[#out + 1] = fr
      pos = pos + len(en)
      connus = connus + 1
      traduit = traduit + nbLettres(en)
    else
      local reste = connus > 0 and sub(s, pos)
      local e = reste and EXACT[reste]
      if e then
        out[#out + 1] = e
        traduit = traduit + nbLettres(reste)
        connus = connus + 1
        break
      end
      local tok = match(s, "^|c%x%x%x%x%x%x%x%x", pos) or match(s, "^|r", pos) or match(s, "^|T.-|t", pos)
        or match(s, "^[^%a\128-\255| ]+", pos) or match(s, "^ ", pos) or match(s, "^[%a\128-\255]+", pos)
        or sub(s, pos, pos)
      if find(tok, "^" .. LETTRE) then
        mots = mots + 1
        if mots > 6 then return nil end
      end
      out[#out + 1] = tok
      pos = pos + len(tok)
    end
  end
  if connus == 0 or traduit * 10 < total * 6 then return nil end
  return concat(out)
end

local cache, nCache = {}, 0
local traduire

local function traduireCoeur(s, prof)
  if s == "" then return nil end
  local e = EXACT[s]
  if e then return e end
  if prof > 4 then return nil end
  -- une seule couleur qui englobe tout : « |cffFFFFFFClear Instance IDs|r »
  local c, inter = match(s, "^(|c%x%x%x%x%x%x%x%x)(.*)|r$")
  if inter and not find(inter, "|[cr]") then
    local a, m, b = match(inter, "^(%s*)(.-)(%s*)$")
    local t = traduireCoeur(m, prof + 1)
    if t then return c .. a .. t .. b .. "|r" end
  end
  -- phrases à valeurs (motifs tirés des string.format du serveur ; peuvent tenir sur plusieurs lignes)
  local r = essayerMotifs(s)
  if r then return r end
  -- plusieurs lignes : chacune pour elle-même
  if find(s, "\n", 1, true) then
    local out, une = {}, false
    for l in gmatch(s .. "\n", "(.-)\n") do
      local t = l ~= "" and traduire(l) or nil
      if t then une = true end
      out[#out + 1] = t or l
    end
    if une then return concat(out, "\n") end
    return nil
  end
  -- une description de sort (gérée par EbonholdFR.lua) n'est pas un texte d'interface
  if len(s) > 40 and E.empreinte and EbonholdFR_Data and EbonholdFR_Data.fp
    and EbonholdFR_Data.fp[E.empreinte(s)] then
    return nil
  end
  return assembler(s)
end

-- texte -> français, ou nil si inconnu (le texte reste alors tel quel)
function traduire(texte)
  if type(texte) ~= "string" or texte == "" then return nil end
  local c = cache[texte]
  if c ~= nil then return c or nil end
  if not find(texte, "%a") then return nil end           -- nombres, compteurs : rien à faire
  local r
  if not find(texte, "|H", 1, true) then                 -- jamais dans un lien
    local a, m, b = match(texte, "^(%s*)(.-)(%s*)$")
    local t = traduireCoeur(m, 0)
    if t then r = a .. t .. b end
    if r == texte then r = nil end
  end
  if nCache >= 5000 then cache, nCache = {}, 0 end
  cache[texte] = r or false
  nCache = nCache + 1
  return r
end
I.traduire = traduire

------------------------------------------------------------------------
-- 2) COLLECTE DES TEXTES NON TRADUITS (désactivée par défaut)
------------------------------------------------------------------------
local COLLECTE = false     -- seul test fait quand la collecte est coupée
local MAX_COLLECTE = 3000
local nomsSorts             -- noms anglais des echoes / nœuds (volontairement non traduits)

local function nomDe(obj)
  local f = obj
  for _ = 1, 8 do
    if type(f) ~= "table" then return nil end
    local nm = f.GetName and f:GetName()
    if nm then return nm end
    f = f.GetParent and f:GetParent()
  end
end

local function joueur(t)
  for _, u in ipairs({ "player", "target", "party1", "party2", "party3", "party4", "pet" }) do
    if UnitName and UnitName(u) == t then return true end
  end
  return false
end

local function noter(texte, obj)
  local C = EbonholdFR_Collecte
  if type(C) ~= "table" or type(texte) ~= "string" then return end
  if not find(texte, "%a") or find(texte, "|H", 1, true) or find(texte, "\195", 1, true) then return end
  local t = match(texte, "^%s*(.-)%s*$")
  if t == "" or not find(t, "%a%a") then return end
  if not nomsSorts then
    nomsSorts = {}
    for _, en in pairs((EbonholdFR_Data and EbonholdFR_Data.nom) or {}) do nomsSorts[en] = true end
  end
  if nomsSorts[t] or joueur(t) then return end
  if E.empreinte and EbonholdFR_Data and EbonholdFR_Data.fp and EbonholdFR_Data.fp[E.empreinte(t)] then return end
  if len(t) > 500 then t = sub(t, 1, 500) end
  local textes = C.textes
  local e = textes[t]
  if e then
    e.n = (e.n or 0) + 1
  elseif (C.n or 0) < MAX_COLLECTE then
    textes[t] = { n = 1, ou = nomDe(obj) }
    C.n = (C.n or 0) + 1
  end
end
I.noter = noter

-- API pour les autres fichiers : traduction + collecte
function E.TraduireInterface(texte, obj)
  local r = traduire(texte)
  if not r and COLLECTE then noter(texte, obj) end
  return r
end
local traduireEtNoter = E.TraduireInterface

local function chargerCollecte()
  if type(EbonholdFR_Collecte) ~= "table" then EbonholdFR_Collecte = {} end
  local C = EbonholdFR_Collecte
  if type(C.textes) ~= "table" then C.textes = {} end
  local n = 0
  for _ in pairs(C.textes) do n = n + 1 end
  C.n = n
  C.actif = C.actif == true
  COLLECTE = C.actif
end
I.chargerCollecte = chargerCollecte

E.Commandes = E.Commandes or {}
E.Commandes.collecte = function(arg)
  chargerCollecte()
  local C = EbonholdFR_Collecte
  if arg == "vider" then
    C.textes, C.n = {}, 0
    E.msg("Collecte vid\195\169e (0 texte).")
    return
  end
  C.actif = not C.actif
  COLLECTE = C.actif
  E.msg("Collecte des textes non traduits : " .. (C.actif and "|cff2cfe32activ\195\169e|r" or "|cffff6666d\195\169sactiv\195\169e|r")
    .. " (" .. C.n .. " texte" .. (C.n > 1 and "s" or "") .. " not\195\169" .. (C.n > 1 and "s" or "")
    .. "). Enregistr\195\169 \195\160 la d\195\169connexion ou au /reload.")
end

------------------------------------------------------------------------
-- 3) ACCROCHE DES OBJETS (FontString, boutons)
------------------------------------------------------------------------
local faible = { __mode = "k" }
local accroche = setmetatable({}, faible)   -- objet -> true (hook posé)
local origine = setmetatable({}, faible)    -- objet -> texte anglais remplacé (pour revenir à l'anglais)
local occupe = setmetatable({}, faible)     -- garde anti-récursion
local serveur = setmetatable({}, faible)    -- cadres reconnus comme appartenant au serveur
I.accroche, I.origine, I.serveur = accroche, origine, serveur
local stats = { fs = 0, boutons = 0, cadres = 0, parcours = 0, racines = 0 }
I.stats = stats

-- méthode SetText d'origine (celle de la métatable, commune à tous les objets d'un type)
local brut = {}
local function setBrut(obj, texte)
  local ot = obj:GetObjectType()
  local f = brut[ot]
  if not f then
    local mt = getmetatable(obj)
    local idx = mt and mt.__index
    f = type(idx) == "table" and idx.SetText
    if type(f) ~= "function" then f = false end
    brut[ot] = f
  end
  occupe[obj] = true
  if f then f(obj, texte) else obj:SetText(texte) end
  occupe[obj] = nil
end

local function appliquer(obj, texte)
  if occupe[obj] or not ON.interface then return end
  if texte == nil then texte = obj:GetText() end
  if type(texte) ~= "string" then return end
  local fr = traduire(texte)
  if fr then
    origine[obj] = texte
    setBrut(obj, fr)
  elseif COLLECTE then
    noter(texte, obj)
  end
end
I.appliquer = appliquer

local function surSetText(obj, texte) appliquer(obj, texte) end
local function surSetFormattedText(obj) appliquer(obj, nil) end

local function accrocherFS(fs)
  if accroche[fs] then return end
  accroche[fs] = true
  stats.fs = stats.fs + 1
  hooksecurefunc(fs, "SetText", surSetText)
  hooksecurefunc(fs, "SetFormattedText", surSetFormattedText)
  appliquer(fs, nil)
end
I.accrocherFS = accrocherFS

local function accrocherBouton(b)
  if accroche[b] then return end
  accroche[b] = true
  -- bouton dont SetText est une fonction Lua de l'addon (boutons « maison ») : son FontString
  -- est accroché à part, on ne touche pas au bouton lui-même
  if rawget(b, "SetText") ~= nil or not b.GetFontString or not b:GetFontString() then return end
  stats.boutons = stats.boutons + 1
  hooksecurefunc(b, "SetText", surSetText)
  appliquer(b, nil)
end

------------------------------------------------------------------------
-- 4) PARCOURS DES FENÊTRES DU SERVEUR
------------------------------------------------------------------------
local IGNORES = { GameTooltip = true, Model = true, PlayerModel = true, DressUpModel = true, TabardModel = true,
  Cooldown = true, ScrollingMessageFrame = true, SimpleHTML = true, Minimap = true, MessageFrame = true,
  ColorSelect = true, MovieFrame = true }
local vu = setmetatable({}, faible)        -- cadre -> GetTime() du dernier passage
local nbReg = setmetatable({}, faible)     -- cadre -> nombre de régions au dernier passage
local enfants = setmetatable({}, faible)   -- cadre -> liste de ses enfants au dernier passage
local ecoute = setmetatable({}, faible)    -- cadre -> HookScript OnShow posé
local parcourir

local function surShow(self)
  if ON.interface then pcall(parcourir, self, 0) end
end

-- visibles = true (veille) : on ne descend que dans les enfants affichés ; les autres seront
-- parcourus par leur propre OnShow (posé lors du premier passage complet)
function parcourir(f, prof, visibles)
  if prof > 40 or vu[f] == GetTime() then return end
  vu[f] = GetTime()
  if f.IsProtected and f:IsProtected() then return end    -- jamais de cadre sécurisé
  local ot = f.GetObjectType and f:GetObjectType()
  if not ot or IGNORES[ot] then return end
  if not serveur[f] then serveur[f] = true; stats.cadres = stats.cadres + 1 end
  stats.parcours = stats.parcours + 1
  local nr = f.GetNumRegions and f:GetNumRegions() or 0
  if nr > 0 and nr ~= nbReg[f] then
    nbReg[f] = nr
    local regs = { f:GetRegions() }
    for i = 1, #regs do
      local r = regs[i]
      if r and r.GetObjectType and r:GetObjectType() == "FontString" then accrocherFS(r) end
    end
  end
  if ot == "Button" or ot == "CheckButton" then accrocherBouton(f) end
  local nc = f.GetNumChildren and f:GetNumChildren() or 0
  if nc > 0 then
    local k = enfants[f]
    if not k or k.n ~= nc then
      k = { f:GetChildren() }
      k.n = nc
      enfants[f] = k
    end
    for i = 1, nc do
      local c = k[i]
      if c and (not visibles or (c.IsShown and c:IsShown())) then parcourir(c, prof + 1, visibles) end
    end
  end
  if not ecoute[f] and (nc > 0 or nr > 0) and f.HookScript then
    ecoute[f] = true
    f:HookScript("OnShow", surShow)
  end
end
I.parcourir = parcourir

-- appartient à une fenêtre du serveur ? (propriétaire d'une infobulle)
local PREFIXES = { "ProjectEbonhold", "Ebonhold", "skillTree", "SkillTree", "Perk", "Objective", "Hardmode",
  "ModernShop", "ExtBank", "VoidStorage", "EchoJournal", "ItemPurchase", "ItemRecovery", "CustomKnowledgeBase",
  "WorldChannel", "InterfaceOptionsProjectEbonhold", "CollectionsJournal", "Wardrobe", "MountJournal",
  "PetJournal", "ShieldTracker", "SpecDropdown", "ezCollections" }
local EXCLUS = { "EbonholdFR", "UtilsSpellTooltip", "EchoDump" }

local function nomServeur(nm)
  if type(nm) ~= "string" then return false end
  for i = 1, #EXCLUS do if sub(nm, 1, len(EXCLUS[i])) == EXCLUS[i] then return false end end
  for i = 1, #PREFIXES do if sub(nm, 1, len(PREFIXES[i])) == PREFIXES[i] then return true end end
  return false
end
I.nomServeur = nomServeur

function E.EstCadreServeur(f)
  for _ = 1, 12 do
    if type(f) ~= "table" then return false end
    if serveur[f] then return true end
    local nm = f.GetName and f:GetName()
    if nm and nomServeur(nm) then serveur[f] = true; return true end
    f = f.GetParent and f:GetParent()
  end
  return false
end

-- traduction des lignes d'une infobulle (appelée par EbonholdFR.lua après Show)
function E.InterfaceTooltip(tt)
  local nom = tt:GetName()
  if not nom then return false end
  local change = false
  local owner = tt.GetOwner and tt:GetOwner() or tt
  for i = 1, tt:NumLines() or 0 do
    for _, cote in ipairs({ "TextLeft", "TextRight" }) do
      local fs = _G[nom .. cote .. i]
      local t = fs and fs:GetText()
      if t then
        local fr = traduireEtNoter(t, owner)
        if fr then fs:SetText(fr); change = true end
      end
    end
  end
  return change
end

------------------------------------------------------------------------
-- 5) RACINES : où sont les fenêtres du serveur ?
------------------------------------------------------------------------
local RACINES = {
  "ProjectEbonholdPerkFrame", "PerkChooseButton", "PerkHideButton", "PerkFamilyHintFrame",
  "ProjectEbonholdPlayerRunFrame", "ProjectEbonholdEmpowermentFrame", "ProjectEbonholdIntensityButton",
  "ProjectEbonholdEchoJournal", "CollectionsJournal", "skillTreeFrame", "EbonholdPrestigeFrame",
  "EbonholdPrestigeConfirmFrame", "ObjectivesMainFrame", "ObjectiveTrackerFrame", "EbonholdExtractionFrame",
  "HardmodeFrame", "HardmodeConfirmPopup", "HardmodeBlockFrame", "HardmodeLockOverlay",
  "EbonholdHardcoreUnlockAlert", "ProjectEbonholdDeathFrame", "ProjectEbonholdConfirmPopup",
  "ProjectEbonholdItemSelectionFrame", "ProjectEbonholdDeathRecapFrame", "ProjectEbonholdLevelUpFrame",
  "ProjectEbonholdOrbSpendDialog", "EbonholdOrbAlert", "CustomKnowledgeBaseFrame", "ItemRecoveryFrame",
  "ItemPurchasePopup", "ModernShopFrame", "ModernShopPreviewFrame", "ModernShopToastFrame", "ExtBankFrame",
  "VoidStorageFrame", "VoidStorageButton", "WorldChannelPopupFrame", "ProjectEbonholdScrapButton",
  "ProjectEbonholdScrapConfigPanel", "SkillTreeMicroButtonAlert", "EchoJournalMicroButtonAlert",
  "CollectionsMicroButtonAlert", "ProjectEbonholdPTRBanner", "EbonholdUnlearnBanner", "SpecDropdownFrame",
  "EbonholdPrestigeAlert", "ProjectEbonholdLoadoutListMenu", "InterfaceOptionsProjectEbonholdPanel",
}
local trouvees = {}    -- racine -> true
local enAttente = {}   -- noms pas encore créés
for _, n in ipairs(RACINES) do enAttente[n] = true end

local NON_INFOBULLE = { "Scan", "Scratch", "Query", "Dump" }

local function prendreRacine(nm, f)
  if trouvees[f] or type(f) ~= "table" or type(rawget(f, 0)) ~= "userdata" then return end
  local ok, ot = pcall(f.GetObjectType, f)
  if not ok or not ot then return end
  if ot == "GameTooltip" then
    for _, x in ipairs(NON_INFOBULLE) do if find(nm, x, 1, true) then trouvees[f] = true; return end end
    trouvees[f] = true
    E.AccrocherInfobulle(f, true)
    return
  end
  if ot == "FontString" then
    trouvees[f] = true
    accrocherFS(f)
    return
  end
  if ot == "Texture" or IGNORES[ot] or not f.HookScript then return end
  if f.IsProtected and f:IsProtected() then return end
  trouvees[f] = true
  stats.racines = stats.racines + 1
  f:HookScript("OnShow", surShow)
  ecoute[f] = true
  if ON.interface and f:IsVisible() then pcall(parcourir, f, 0) end
end

local function verifierAttente()
  local reste = false
  for nm in pairs(enAttente) do
    local f = _G[nm]
    if f then enAttente[nm] = nil; prendreRacine(nm, f) else reste = true end
  end
  return reste
end

-- balayage de _G : fenêtres nommées avec un préfixe du serveur (résiste aux mises à jour)
local function balayer()
  for nm, f in pairs(_G) do
    if type(f) == "table" and type(nm) == "string" and not trouvees[f] and nomServeur(nm) then
      prendreRacine(nm, f)
    end
  end
end
I.balayer = balayer

-- veille : racines manquantes (0,5 s), fenêtres visibles (1 s, parcours incrémental),
-- balayage de _G (2 s, 15 s, 60 s après la connexion puis toutes les 5 min)
local veille = CreateFrame("Frame")
local tA, tV, tB, nB = 0, 0, 0, 0
local PAUSES = { 2, 13, 45 }
veille:SetScript("OnUpdate", function(self, dt)
  tA, tV, tB = tA + dt, tV + dt, tB + dt
  if tA >= 0.5 then
    tA = 0
    verifierAttente()
  end
  if tV >= 1 then
    tV = 0
    if ON.interface then
      for f in pairs(trouvees) do
        if ecoute[f] and f:IsVisible() then pcall(parcourir, f, 0, true) end
      end
    end
  end
  if tB >= (PAUSES[nB + 1] or 300) then
    tB = 0
    nB = nB + 1
    pcall(balayer)
  end
end)

------------------------------------------------------------------------
-- 6) BOÎTES DE CONFIRMATION DU SERVEUR (StaticPopup)
------------------------------------------------------------------------
local DIALOGUES = { UNLOCK_PERK_CONFIRM = true, CONFIRM_GM_TICKET = true }
local PREF_DIALOGUES = { "PROJECTEBONHOLD_", "EBONHOLD_", "SKILLTREE_", "EXTBANK_" }
local function dialogueServeur(which)
  if type(which) ~= "string" then return false end
  if DIALOGUES[which] then return true end
  for i = 1, #PREF_DIALOGUES do if sub(which, 1, len(PREF_DIALOGUES[i])) == PREF_DIALOGUES[i] then return true end end
  return false
end
I.dialogueServeur = dialogueServeur

local function apresPopup(self)
  if not ON.interface or not dialogueServeur(self.which) then return end
  local nom = self:GetName()
  local change = false
  local fs = nom and _G[nom .. "Text"]
  local t = fs and fs:GetText()
  local fr = t and traduireEtNoter(t, self)
  if fr then fs:SetText(fr); change = true end
  for i = 1, 3 do
    local b = nom and _G[nom .. "Button" .. i]
    local bt = b and b:IsShown() and b:GetText()
    local bfr = bt and traduireEtNoter(bt, self)
    if bfr then b:SetText(bfr); change = true end
  end
  if change and StaticPopup_Resize then pcall(StaticPopup_Resize, self, self.which) end
end

local popups = {}
local function accrocherPopups()
  for i = 1, 4 do
    local p = _G["StaticPopup" .. i]
    if p and not popups[p] then
      popups[p] = true
      hooksecurefunc(p, "Show", function(self) pcall(apresPopup, self) end)
    end
  end
end

------------------------------------------------------------------------
-- 7) RÉGLAGES : couper / remettre la traduction de l'interface à chaud
------------------------------------------------------------------------
local etaitActif = ON.interface
local precedent = E.SurChangementReglages
function E.SurChangementReglages()
  if precedent then precedent() end
  if ON.interface == etaitActif then return end
  etaitActif = ON.interface
  if not ON.interface then
    -- retour à l'anglais d'origine
    for obj, en in pairs(origine) do pcall(setBrut, obj, en) end
    for k in pairs(origine) do origine[k] = nil end
  else
    for obj in pairs(accroche) do pcall(appliquer, obj, nil) end
    for f in pairs(trouvees) do
      if ecoute[f] and f.IsVisible and f:IsVisible() then pcall(parcourir, f, 0) end
    end
  end
end

local precedentSV = E.SurChargementVariables
function E.SurChargementVariables()
  if precedentSV then precedentSV() end
  chargerCollecte()
end

------------------------------------------------------------------------
-- 8) DÉMARRAGE + commande /efr stats
------------------------------------------------------------------------
local demarrage = CreateFrame("Frame")
demarrage:RegisterEvent("PLAYER_LOGIN")
demarrage:SetScript("OnEvent", function()
  chargerCollecte()
  accrocherPopups()
  verifierAttente()
end)

E.Commandes = E.Commandes or {}
E.Commandes.stats = function()
  local nC = 0
  for _ in pairs(cache) do nC = nC + 1 end
  local manquantes = {}
  for nm in pairs(enAttente) do manquantes[#manquantes + 1] = nm end
  E.msg(("Interface : %d textes connus, %d motifs, %d morceaux | racines %d, cadres %d, FontString %d, boutons %d | cache %d")
    :format((function() local n = 0 for _ in pairs(EXACT) do n = n + 1 end return n end)(), #MOTIFS,
      (function() local n = 0 for _ in pairs(MORCEAUX) do n = n + 1 end return n end)(),
      stats.racines, stats.cadres, stats.fs, stats.boutons, nC))
  if #manquantes > 0 then E.msg("Fen\195\170tres pas encore cr\195\169\195\169es : " .. concat(manquantes, ", ")) end
  if E.Commandes.collecte and EbonholdFR_Collecte then
    E.msg("Collecte : " .. (COLLECTE and "active" or "coup\195\169e") .. ", " .. (EbonholdFR_Collecte.n or 0) .. " textes not\195\169s.")
  end
end
