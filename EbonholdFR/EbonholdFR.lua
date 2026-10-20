--[[ EbonholdFR 4.0 — cœur : réglages, descriptions (echoes, Soul Tree, affixes, tomes), infobulles.

  Principe des descriptions (même calcul que tools/generer_donnees_v4.py) :
    texte anglais affiché -> sans couleurs, blancs regroupés -> « jetons » (nombres 12 / 2.5 et
    formules @...@) -> EMPREINTE = texte où chaque jeton devient « # ».
    EbonholdFR_Data.fp[empreinte] -> gabarit français ; ses marqueurs {k} reprennent le k-ième jeton
    du texte anglais AFFICHÉ ({@k} = formule calculée, affichée en vert comme l'original).
  On ne traduit QUE si l'empreinte est connue : texte modifié par le serveur, texte déjà en
  français (patch FR) ou inconnu -> on ne touche à rien.

  Points d'accroche (aucun hook global de SetText, aucun script posé sur un bouton sécurisé) :
    * utils.GetSpellDescription / GetStackedSpellDescription / GetSpellSearchText (table Lua de
      l'addon du serveur, remplacement de champ) ;
    * GameTooltip, ItemRefTooltip, ShoppingTooltip1/2 et les infobulles du serveur :
      hooksecurefunc(..., "SetHyperlink" / "Show") et HookScript OnTooltipSetItem / OnTooltipSetSpell.
]]

local ADDON = "EbonholdFR"
EbonholdFR = EbonholdFR or {}
local E = EbonholdFR

local D = EbonholdFR_Data or {}
local GABARITS = D.t or {}
local EMPREINTES = D.fp or {}
local PAR_ID = D.id or {}
local NOM_EN = D.nom or {}
local TOME_ITEM = D.tomeItem or {}

local find, sub, gsub, match, len = string.find, string.sub, string.gsub, string.match, string.len
local concat, floor, tonumber, type, pairs, pcall = table.concat, math.floor, tonumber, type, pairs, pcall

local function msg(s)
  if DEFAULT_CHAT_FRAME then DEFAULT_CHAT_FRAME:AddMessage("|cff9966ff[EbonholdFR]|r " .. tostring(s)) end
end
E.msg = msg

E.version = (GetAddOnMetadata and GetAddOnMetadata(ADDON, "Version")) or "?"

------------------------------------------------------------------------
-- 1) RÉGLAGES
--    EbonholdFR_Reglages (fichier écrit par le launcher, chargé en premier ; absent = défauts)
--    + choix faits en jeu (EbonholdFRDB.choix). Si le launcher change ses réglages, ses
--    nouvelles valeurs reprennent la main (les choix en jeu sont alors oubliés).
------------------------------------------------------------------------
local DEFAUTS = { interface = true, echoes_desc = true, soultree_desc = true, affixes_desc = true,
                  tomes = true, nom_anglais = true, patch = false }
E.CLES = { "interface", "echoes_desc", "soultree_desc", "affixes_desc", "tomes", "nom_anglais" }
local CLE_CAT = { [1] = "echoes_desc", [2] = "soultree_desc", [3] = "affixes_desc", [4] = "tomes" }
E.CLE_CAT = CLE_CAT

local ON = {}          -- réglages effectifs (recalculés par E.Rafraichir)
E.ON = ON
local DB               -- EbonholdFRDB (disponible à ADDON_LOADED)

local function bool(v, def)
  if v == nil then return def end
  if v == "fr" or v == "on" or v == "oui" or v == 1 or v == "1" or v == "true" then return true end
  if v == "en" or v == "off" or v == "non" or v == 0 or v == "0" or v == "false" then return false end
  return v and true or false
end
E.bool = bool

local function reglagesLauncher()
  return type(EbonholdFR_Reglages) == "table" and EbonholdFR_Reglages or nil
end

-- le patch FR (descriptions françaises dans le jeu) est-il installé ?
function E.Patch()
  local R = reglagesLauncher()
  return R and bool(R.patch, false) or false
end

local function signature(R)
  if not R then return "aucun" end
  local t = {}
  for _, k in ipairs(E.CLES) do t[#t + 1] = k .. "=" .. tostring(R[k]) end
  t[#t + 1] = "patch=" .. tostring(R.patch)
  return concat(t, ";")
end

-- valeur « brute » d'un réglage (sans l'interrupteur général ni le patch)
function E.ValeurReglage(cle)
  if DB and DB.choix and DB.choix[cle] ~= nil then return DB.choix[cle] end
  local R = reglagesLauncher()
  if R and R[cle] ~= nil then return bool(R[cle], DEFAUTS[cle]) end
  return DEFAUTS[cle]
end

function E.Rafraichir()
  local actif = not DB or DB.enabled ~= false
  local patch = E.Patch()
  for _, k in ipairs(E.CLES) do
    local v = actif and E.ValeurReglage(k) or false
    -- patch FR installé : les descriptions sont déjà en français dans le jeu -> on n'y touche pas
    if patch and (k == "echoes_desc" or k == "soultree_desc" or k == "affixes_desc" or k == "tomes") then v = false end
    ON[k] = v and true or false
  end
  ON.desc = ON.echoes_desc or ON.soultree_desc or ON.affixes_desc or ON.tomes
  if E.SurChangementReglages then E.SurChangementReglages() end
end
E.Rafraichir()

function E.SetChoix(cle, valeur)
  E.EnsureDB()
  DB.choix[cle] = valeur and true or false
  E.Rafraichir()
end

function E.RevenirLauncher()
  E.EnsureDB()
  DB.choix = {}
  DB.enabled = true
  E.Rafraichir()
end

-- crée/complète EbonholdFRDB (idempotent ; aussi appelée par le fichier d'interface)
function E.EnsureDB()
  if type(EbonholdFRDB) ~= "table" then EbonholdFRDB = {} end
  local db = EbonholdFRDB
  if db.v ~= 4 then
    -- migration v3 -> v4 : les réglages par catégorie viennent maintenant du launcher
    db.cat = nil
    db.choix = {}
    db.v = 4
  end
  if type(db.choix) ~= "table" then db.choix = {} end
  if db.enabled == nil then db.enabled = true end
  db.minimap = db.minimap or {}
  if db.minimap.hide == nil then db.minimap.hide = false end
  if db.minimap.angle == nil then db.minimap.angle = 200 end
  local sig = signature(reglagesLauncher())
  if db.sigReglages ~= sig then
    -- le launcher a changé les réglages depuis la dernière session : ils reprennent la main
    db.sigReglages = sig
    db.choix = {}
    db.enabled = true
  end
  DB = db
  return db
end

------------------------------------------------------------------------
-- 2) EMPREINTE, JETONS, GABARITS (fonctions pures, testées hors jeu)
------------------------------------------------------------------------
local function normaliser(s)
  s = gsub(s, "|c%x%x%x%x%x%x%x%x", "")
  s = gsub(s, "|r", "")
  s = gsub(s, "%s+", " ")
  return (match(s, "^ *(.-) *$"))
end

-- -> liste des jetons, empreinte
local function jetons(plain)
  local toks, parts, pos = {}, {}, 1
  while true do
    local s = find(plain, "[@%d]", pos)
    if not s then break end
    local e
    if sub(plain, s, s) == "@" then
      e = find(plain, "@", s + 1, true)
      if not e then
        -- « @ » sans fermeture : simple caractère
        parts[#parts + 1] = sub(plain, pos, s)
        pos = s + 1
      end
    else
      local m = match(plain, "^%d+%.%d+", s) or match(plain, "^%d+", s)
      e = s + len(m) - 1
    end
    if e then
      parts[#parts + 1] = sub(plain, pos, s - 1)
      parts[#parts + 1] = "#"
      toks[#toks + 1] = sub(plain, s, e)
      pos = e + 1
    end
  end
  parts[#parts + 1] = sub(plain, pos)
  return toks, concat(parts)
end

local VERT = "|cff2cfe32"
local function remplir(g, toks)
  local ok = true
  local r = gsub(g, "{(@?)(%d+)}", function(f, k)
    local v = toks[tonumber(k)]
    if not v then ok = false; return "" end
    if f == "@" and sub(v, 1, 1) ~= "@" then return VERT .. v .. "|r" end
    return v
  end)
  if ok then return r end
end

local function empreinte(texte)
  local _, fp = jetons(normaliser(texte))
  return fp
end

E.normaliser, E.jetons, E.remplir, E.empreinte = normaliser, jetons, remplir, empreinte

-- cache : texte anglais -> traduction (ou false). Vidé au-delà de 3000 entrées.
local cacheDesc, nCacheDesc = {}, 0

-- Texte anglais affiché -> texte français, catégorie (1 echoes, 2 Soul Tree, 3 affixes, 4 tomes)
-- ou nil si le texte n'est pas reconnu (ou si la catégorie est désactivée).
function E.TraduireDescription(texte, idSort)
  if type(texte) ~= "string" or texte == "" then return nil end
  local special = idSort and PAR_ID[idSort]
  local c = (not special) and cacheDesc[texte]
  local fr, cat
  if c ~= nil and c ~= false then
    fr, cat = c[1], c[2]
  elseif c == nil then
    local toks, fp = jetons(normaliser(texte))
    local v = EMPREINTES[fp]
    if v then
      local idx = floor(v / 10)
      cat = v % 10
      if special and special[1] == fp then idx = special[2] end
      local g = GABARITS[idx]
      fr = g and remplir(g, toks)
    end
    if not special then
      if nCacheDesc > 3000 then cacheDesc, nCacheDesc = {}, 0 end
      cacheDesc[texte] = fr and { fr, cat } or false
      nCacheDesc = nCacheDesc + 1
    end
  end
  if fr and ON[CLE_CAT[cat] or ""] then return fr, cat end
  return nil
end

-- coupe le français à ~maxLength x 1,3 (le français est plus long) sur un espace, sans
-- laisser de code couleur ouvert ni de caractère UTF-8 entamé
local function couper(s, maxLength)
  maxLength = tonumber(maxLength) or 100
  local lim = floor(maxLength * 1.3 + 0.5)
  if len(s) <= lim then return s end
  local cut = sub(s, 1, lim - 3)
  local sp = find(cut, " [^ ]*$")
  if sp and sp > lim * 0.6 then cut = sub(cut, 1, sp - 1) end
  cut = gsub(cut, "[\192-\255][\128-\191]*$", "")
  cut = gsub(cut, "|c%x*$", "")
  cut = gsub(cut, "|$", "")
  local _, nc = gsub(cut, "|c%x%x%x%x%x%x%x%x", "")
  local _, nr = gsub(cut, "|r", "")
  if nc > nr then cut = cut .. "|r" end
  return cut .. "..."
end
E.couper = couper

-- retour à la ligne manuel (infobulles du Soul Tree, qui ne coupent pas les lignes elles-mêmes)
local function couperLignes(s, largeur)
  local out = {}
  for para in string.gmatch(s .. "\n", "(.-)\n") do
    if len(para) <= largeur then
      out[#out + 1] = para
    else
      local ligne = ""
      for mot in string.gmatch(para, "%S+") do
        if ligne == "" then ligne = mot
        elseif len(ligne) + 1 + len(mot) > largeur then out[#out + 1] = ligne; ligne = mot
        else ligne = ligne .. " " .. mot end
      end
      out[#out + 1] = ligne
    end
  end
  return concat(out, "\n")
end
E.couperLignes = couperLignes

------------------------------------------------------------------------
-- 3) ACCROCHES SUR utils (addon du serveur)
------------------------------------------------------------------------
local orig = {}

local function installerUtils()
  if type(utils) ~= "table" or type(utils.GetSpellDescription) ~= "function" then return false end
  if utils._ebonholdFR4 then return true end
  utils._ebonholdFR4 = true

  -- 3a) description d'un echo (cartes de choix, journal, panneau de la run, tomes...)
  orig.GSD = utils.GetSpellDescription
  utils.GetSpellDescription = function(spellId, maxLength, stacks)
    if not ON.echoes_desc or type(spellId) ~= "number" then
      return orig.GSD(spellId, maxLength, stacks)
    end
    -- on demande le texte COMPLET (sinon l'anglais est coupé avant ses derniers nombres)
    local ok, complet = pcall(orig.GSD, spellId, 100000, stacks)
    if ok and type(complet) == "string" then
      local fr = E.TraduireDescription(complet, spellId)
      if fr then return couper(gsub(fr, "%s+", " "), maxLength) end
    end
    return orig.GSD(spellId, maxLength, stacks)
  end

  -- 3b) description cumulée (echoes équipés en plusieurs exemplaires)
  if type(utils.GetStackedSpellDescription) == "function" then
    orig.GSSD = utils.GetStackedSpellDescription
    utils.GetStackedSpellDescription = function(spellInstances, maxLength)
      local sid = type(spellInstances) == "table" and spellInstances[1] and spellInstances[1].spellId
      if ON.echoes_desc and type(sid) == "number" then
        local ok, complet = pcall(orig.GSSD, spellInstances, 100000)
        if ok and type(complet) == "string" then
          local fr = E.TraduireDescription(complet, sid)
          if fr then return couper(gsub(fr, "%s+", " "), maxLength) end
        end
      end
      return orig.GSSD(spellInstances, maxLength)
    end
  end

  -- 3c) recherche du journal des echoes : l'anglais ET le français sont cherchables
  if type(utils.GetSpellSearchText) == "function" then
    orig.GSST = utils.GetSpellSearchText
    utils.GetSpellSearchText = function(spellId)
      local en = orig.GSST(spellId)
      if ON.echoes_desc and type(en) == "string" and en ~= "" then
        local fr = E.TraduireDescription(en, spellId)
        if fr then return en .. " " .. normaliser(fr) end
      end
      return en
    end
  end
  return true
end
E.installerUtils = installerUtils
installerUtils()   -- ProjectEbonhold est une dépendance : utils existe déjà en principe

------------------------------------------------------------------------
-- 4) INFOBULLES
------------------------------------------------------------------------
local lignesCache = setmetatable({}, { __mode = "k" })   -- infobulle -> { [i] = FontString gauche }
local function ligne(tt, i, droite)
  local nom = tt:GetName()
  if not nom then return nil end
  if droite then return _G[nom .. "TextRight" .. i] end
  local c = lignesCache[tt]
  if not c then c = {}; lignesCache[tt] = c end
  local fs = c[i]
  if not fs then fs = _G[nom .. "TextLeft" .. i]; c[i] = fs end
  return fs
end
E.ligne = ligne

-- traduit les lignes de description (2..n) reconnues par leur empreinte
local function traduireLignes(tt, idSort, largeur)
  if not ON.desc then return false end
  local n = tt:NumLines() or 0
  local change = false
  for i = 2, n do
    local fs = ligne(tt, i)
    local txt = fs and fs:GetText()
    if txt and len(txt) > 12 then
      local fr = E.TraduireDescription(txt, idSort)
      if fr then
        if largeur then fr = couperLignes(fr, largeur) end
        fs:SetText(fr)
        change = true
      end
    end
  end
  return change
end
E.traduireLignes = traduireLignes

-- Option « Afficher aussi le nom anglais » : nom affiché (patch FR) -> nom anglais
local nomsAffiches
local function tableNoms()
  if nomsAffiches then return nomsAffiches end
  nomsAffiches = {}
  if not GetSpellInfo then return nomsAffiches end
  for id, en in pairs(NOM_EN) do
    local cur = GetSpellInfo(id)
    if cur and cur ~= en then
      local deja = nomsAffiches[cur]
      if deja == nil then nomsAffiches[cur] = en
      elseif deja ~= en then nomsAffiches[cur] = false end   -- ambigu : on s'abstient
    end
  end
  return nomsAffiches
end
E.tableNoms = tableNoms

local PREFIXE_EN = "EN : "
local function aDejaLigneEN(tt)
  for i = 2, tt:NumLines() or 0 do
    local fs = ligne(tt, i)
    local t = fs and fs:GetText()
    if t and sub(t, 1, len(PREFIXE_EN)) == PREFIXE_EN then return true end
  end
  return false
end

-- la ligne « EN : » est ajoutée à l'image suivante, une fois que l'addon du serveur a fini
-- d'ajouter ses propres lignes (rang, coût...) : elle arrive ainsi en bas de l'infobulle
local attente = {}
local pilote = CreateFrame("Frame")
pilote:Hide()
pilote:SetScript("OnUpdate", function(self)
  self:Hide()
  local liste = attente
  attente = {}            -- (Show ci-dessous peut replanifier : nouvelle table)
  for tt, en in pairs(liste) do
    if tt:IsShown() and ON.nom_anglais and not aDejaLigneEN(tt) then
      local l1 = ligne(tt, 1)
      local t = l1 and l1:GetText()
      if t and tableNoms()[t] == en then
        tt:AddLine(PREFIXE_EN .. en, 0.5, 0.5, 0.5)
        tt:Show()
      end
    end
  end
end)

local function planifierNomAnglais(tt)
  if not ON.nom_anglais then return end
  local l1 = ligne(tt, 1)
  local t = l1 and l1:GetText()
  if not t then return end
  local en = tableNoms()[t]
  if en then
    attente[tt] = en
    pilote:Show()
  end
end
E.planifierNomAnglais = planifierNomAnglais

-- 4a) liens de sorts / echoes : spell:ID, echo:ID
local function apresSetHyperlink(tt, lien)
  if type(lien) ~= "string" then return end
  local id = tonumber(match(lien, "^spell:(%d+)") or match(lien, "^echo:(%d+)") or "")
  if not id then return end
  local largeur = E.LARGEUR_TT and E.LARGEUR_TT[tt]
  if traduireLignes(tt, id, largeur) then tt:Show() end
  planifierNomAnglais(tt)
end

-- 4b) grimoire : OnTooltipSetSpell
local function surSort(tt)
  local _, _, id = tt:GetSpell()
  if traduireLignes(tt, id) then tt:Show() end
  planifierNomAnglais(tt)
end

-- 4c) objets : ligne violette des affixes gravés, tomes of Echo
local VIOLET = "|cffb048f8"
local cacheObjet, nCacheObjet = {}, 0

local function traduireLigneAffixe(txt)
  local avant, inter, apres = match(txt, "^(.-)" .. VIOLET .. "(.-)|r(.*)$")
  local ouvre, ferme = VIOLET, "|r"
  if not inter then
    avant, ouvre, inter, ferme, apres = match(txt, "^(.-)(@[Aa]ffixe?@)(.-)(@[Aa]ffixe?@)(.*)$")
  end
  if not inter then return nil end
  local fr, cat = E.TraduireDescription(inter)
  if fr and cat == 3 then return avant .. ouvre .. fr .. ferme .. apres end
end

local function traduireObjet(tt)
  if not (ON.affixes_desc or ON.tomes or ON.nom_anglais or ON.interface) then return end
  local n = tt:NumLines() or 0
  if n < 2 then return end
  local _, lien = tt:GetItem()
  local itemId = lien and tonumber(match(lien, "item:(%d+)"))
  local titreEN = itemId and TOME_ITEM[itemId]
  local change = false
  for i = 2, n do
    local fs = ligne(tt, i)
    local txt = fs and fs:GetText()
    if txt then
      local fr
      if find(txt, VIOLET, 1, true) or find(txt, "ffixe?@") then
        -- ne travailler QUE sur les lignes marquées (filtre), résultat mis en cache
        if ON.affixes_desc then
          fr = cacheObjet[txt]
          if fr == nil then
            fr = traduireLigneAffixe(txt) or false
            if nCacheObjet > 2000 then cacheObjet, nCacheObjet = {}, 0 end
            cacheObjet[txt] = fr
            nCacheObjet = nCacheObjet + 1
          end
        end
      elseif titreEN then
        -- tome of Echo : ligne « Use: ... » et lignes ajoutées par le serveur
        if ON.tomes and sub(txt, 1, 5) == "Use: " then
          fr = E.TraduireDescription(txt)
        elseif ON.interface and E.TraduireInterface then
          fr = E.TraduireInterface(txt, tt)
        end
        if ON.interface and E.TraduireInterface then
          local fd = ligne(tt, i, true)
          local td = fd and fd:IsShown() and fd:GetText()
          local frd = td and E.TraduireInterface(td, tt)
          if frd then fd:SetText(frd); change = true end
        end
      end
      if fr then fs:SetText(fr); change = true end
    end
  end
  if titreEN and ON.nom_anglais then
    local l1 = ligne(tt, 1)
    local t = l1 and l1:GetText()
    if t and normaliser(t) ~= titreEN and not aDejaLigneEN(tt) then
      tt:AddLine(PREFIXE_EN .. titreEN, 0.5, 0.5, 0.5)
      change = true
    end
  end
  if change then tt:Show() end
end
E.traduireObjet = traduireObjet

-- 4d) après chaque Show : interface du serveur, descriptions des infobulles du serveur, nom anglais
E.TT_SERVEUR = {}      -- infobulles créées par l'addon du serveur -> true
E.LARGEUR_TT = {}      -- infobulles sans retour à la ligne automatique -> largeur (caractères)
local enShow = false
local function traiterShow(tt)
  local change = false
  local srv = E.TT_SERVEUR[tt]
  if srv then change = traduireLignes(tt, nil, E.LARGEUR_TT[tt]) or change end
  if ON.interface and E.InterfaceTooltip and (srv or (E.EstCadreServeur and E.EstCadreServeur(tt:GetOwner()))) then
    change = E.InterfaceTooltip(tt) or change
  end
  if change then tt:Show() end
  planifierNomAnglais(tt)
end
local function apresShow(tt)
  if enShow then return end
  enShow = true
  local ok, err = pcall(traiterShow, tt)
  enShow = false
  if not ok and E.debug then msg("erreur infobulle : " .. tostring(err)) end
end

local accrocheTT = {}
function E.AccrocherInfobulle(nom, serveur, largeur)
  local tt = type(nom) == "string" and _G[nom] or nom
  if type(tt) ~= "table" or type(tt.HookScript) ~= "function" or accrocheTT[tt] then return accrocheTT[tt] or false end
  accrocheTT[tt] = true
  if serveur then E.TT_SERVEUR[tt] = true end
  if largeur then E.LARGEUR_TT[tt] = largeur end
  hooksecurefunc(tt, "Show", apresShow)
  if type(tt.SetHyperlink) == "function" then
    hooksecurefunc(tt, "SetHyperlink", function(self, lien)
      local ok = pcall(apresSetHyperlink, self, lien)
    end)
  end
  if not serveur then
    tt:HookScript("OnTooltipSetItem", function(self) pcall(traduireObjet, self) end)
    tt:HookScript("OnTooltipSetSpell", function(self) pcall(surSort, self) end)
  end
  return true
end

-- infobulles créées par le serveur (largeur = retour à la ligne manuel)
local TT_DU_SERVEUR = {
  skillTreeCurrentRankTooltip = 52, skillTreeNextRankTooltip = 52, skillTreeInfoTooltip = 52,
  ProjectEbonholdCheckpointTooltip = false, EbonholdPrestigeCacheTip = false,
}

local function accrocherInfobulles()
  local tout = true
  for _, nom in ipairs({ "GameTooltip", "ItemRefTooltip", "ShoppingTooltip1", "ShoppingTooltip2" }) do
    if not E.AccrocherInfobulle(nom, false) then tout = false end
  end
  for nom, largeur in pairs(TT_DU_SERVEUR) do
    if not E.AccrocherInfobulle(nom, true, largeur or nil) then tout = false end
  end
  return tout
end

------------------------------------------------------------------------
-- 5) INITIALISATION
------------------------------------------------------------------------
local init = CreateFrame("Frame")
init:RegisterEvent("ADDON_LOADED")
init:RegisterEvent("PLAYER_LOGIN")
init:SetScript("OnEvent", function(self, event, arg1)
  if event == "ADDON_LOADED" and arg1 == ADDON then
    E.EnsureDB()
    E.Rafraichir()
    if E.SurChargementVariables then E.SurChargementVariables() end
  elseif event == "PLAYER_LOGIN" then
    E.EnsureDB()
    E.Rafraichir()
    -- certaines infobulles du serveur peuvent apparaître plus tard : on réessaie quelques secondes
    local essais, t = 0, 0
    self:SetScript("OnUpdate", function(f, dt)
      t = t + dt
      if t < 1 then return end
      t = 0
      essais = essais + 1
      local ok = installerUtils() and accrocherInfobulles()
      if essais == 3 and ON.nom_anglais then tableNoms() end   -- noms affichés -> anglais (1 fois)
      if (ok and essais >= 3) or essais > 20 then
        f:SetScript("OnUpdate", nil)
        if E.debug then msg("accroches : " .. tostring(ok)) end
      end
    end)
    installerUtils()
    accrocherInfobulles()
  end
end)

------------------------------------------------------------------------
-- 6) COMMANDES : /efr [sous-commande]  (+ anciens alias /frtest, /frmenu, /frbouton)
------------------------------------------------------------------------
E.Commandes = E.Commandes or {}

E.Commandes.test = function(arg)
  local id = tonumber(arg)
  if not id then msg("/efr test <id du sort>"); return end
  local en = orig.GSD and orig.GSD(id, 100000, 1)
  msg("EN : " .. tostring(en))
  local fr = en and E.TraduireDescription(en, id)
  msg("FR : " .. tostring(fr or "(empreinte inconnue : laiss\195\169 en anglais)"))
  if en then msg("empreinte : " .. empreinte(en)) end
end

E.Commandes.aide = function()
  msg("v" .. E.version .. " \226\128\148 /efr : options | /efr test <id> | /efr stats | /efr collecte [vider] | /efr fix | /efr bouton")
end

SLASH_EBONHOLDFR1 = "/efr"
SlashCmdList["EBONHOLDFR"] = function(txt)
  txt = txt or ""
  local cmd, reste = match(txt, "^%s*(%S*)%s*(.-)%s*$")
  cmd = string.lower(cmd or "")
  if cmd == "" then
    if E.Commandes.menu then E.Commandes.menu() else E.Commandes.aide() end
    return
  end
  local f = E.Commandes[cmd]
  if f then f(reste) else E.Commandes.aide() end
end

SLASH_FRTEST1 = "/frtest"
SlashCmdList["FRTEST"] = function(arg) E.Commandes.test(arg) end
