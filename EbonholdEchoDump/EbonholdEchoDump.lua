--[[ Ebonhold Echo Dump  (read-only — ne modifie rien en jeu)
  But : exporter tous les echoes (nom + description + metadata) dans SavedVariables,
  pour la traduction et les guides.
  Usage en jeu :
     1) /echodump        -> scanne tous les echoes
     2) /reload          -> écrit le fichier sur le disque
     3) Envoie le fichier :
        <WoW>\WTF\Account\<COMPTE>\SavedVariables\EbonholdEchoDump.lua
  Bonus : /echodump affixes  (tente de dumper aussi les tables custom du serveur)
]]

EchoDumpDB = EchoDumpDB or {}

-- Tooltip caché pour lire les descriptions des sorts
local scanner = CreateFrame("GameTooltip", "EchoDumpScanner", UIParent, "GameTooltipTemplate")
scanner:SetOwner(UIParent, "ANCHOR_NONE")

-- Accumulateur des objets tomes (persiste entre les /echodump d'une même session)
local TOME_ITEMS = {}

local function ReadTooltipLines(spellId)
  scanner:ClearLines()
  -- SetHyperlink lit la description telle que définie côté serveur
  local ok = pcall(function() scanner:SetHyperlink("spell:" .. spellId) end)
  if not ok then return nil end
  local lines = {}
  local n = scanner:NumLines() or 0
  for i = 1, n do
    local fs = _G["EchoDumpScannerTextLeft" .. i]
    if fs then
      local txt = fs:GetText()
      if txt and txt ~= "" then lines[#lines + 1] = txt end
    end
  end
  return lines
end

-- Lit les lignes d'un tooltip d'OBJET à partir de son lien (item:...)
local function ReadItemTooltipLines(link)
  scanner:ClearLines()
  local ok = pcall(function() scanner:SetHyperlink(link) end)
  if not ok then return nil end
  local lines = {}
  local n = scanner:NumLines() or 0
  for i = 1, n do
    local fs = _G["EchoDumpScannerTextLeft" .. i]
    if fs then
      local txt = fs:GetText()
      if txt and txt ~= "" then lines[#lines + 1] = txt end
    end
  end
  return lines
end

-- Scanne les OBJETS tomes (tooltip complet avec blurb). Réutilisable (dump + ticker).
-- Priming GetItemInfo : force le serveur à envoyer les données des items non possédés ;
-- elles arrivent ~quelques sec plus tard -> ré-appeler accumule dans TOME_ITEMS.
local function ScanTomeItems()
  local function scanTomeItem(link)
    if not link then return end
    local lines = ReadItemTooltipLines(link)
    if not lines or #lines == 0 then return end
    local title = lines[1] or ""
    local echoName = string.match(title, "^Tome of Echo: (.+)$")
    if not echoName then return end
    if TOME_ITEMS[echoName] then return end
    -- ignore les tooltips incomplets (pas encore la ligne "Use:")
    local hasUse = false
    for i = 2, #lines do
      if string.find(lines[i], "when offered new Echoes", 1, true) then hasUse = true break end
    end
    if not hasUse then return end
    local itemId = tonumber(string.match(link, "item:(%d+)"))
    TOME_ITEMS[echoName] = { itemId = itemId, title = title, tooltip = lines }
  end
  -- 0) priming
  for _, e in ipairs(Tome_Ids or {}) do
    if e.id then pcall(GetItemInfo, e.id) end
  end
  -- 1) item:id direct (item id d'un tome == id de son sort grant = Tome_Ids)
  for _, e in ipairs(Tome_Ids or {}) do
    if e.id then scanTomeItem("item:" .. e.id) end
  end
  -- 2) sacs
  for bag = 0, 4 do
    local slots = GetContainerNumSlots and GetContainerNumSlots(bag) or 0
    for slot = 1, slots do
      scanTomeItem(GetContainerItemLink and GetContainerItemLink(bag, slot))
    end
  end
  -- 3) banque de guilde (onglets en cache)
  local numTabs = GetNumGuildBankTabs and GetNumGuildBankTabs() or 0
  for tab = 1, numTabs do
    for slot = 1, 98 do
      scanTomeItem(GetGuildBankItemLink and GetGuildBankItemLink(tab, slot))
    end
  end
  local tiFound = 0
  for _ in pairs(TOME_ITEMS) do tiFound = tiFound + 1 end
  EchoDumpDB.tomeItems = TOME_ITEMS
  EchoDumpDB.tomeItemCount = tiFound
  return tiFound
end

-- Copie sûre d'une table vers SavedVariables (string/number/boolean/table seulement)
local function SafeCopy(t, depth)
  if depth > 5 or type(t) ~= "table" then return nil end
  local out = {}
  for k, v in pairs(t) do
    local tk = type(k)
    if tk == "string" or tk == "number" then
      local tv = type(v)
      if tv == "string" or tv == "number" or tv == "boolean" then
        out[k] = v
      elseif tv == "table" then
        out[k] = SafeCopy(v, depth + 1)
      end
    end
  end
  return out
end

local function msg(s) DEFAULT_CHAT_FRAME:AddMessage("|cff9966ff[EchoDump]|r " .. s) end

local function DoDump(alsoServer)
  local ids = EchoDump_Ids or {}
  EchoDumpDB = {
    generatedAt = date("%Y-%m-%d %H:%M:%S"),
    client = GetBuildInfo and select(1, GetBuildInfo()) or "3.3.5",
    count = 0,
    perks = {},
  }

  local found, missing = 0, 0
  for _, e in ipairs(ids) do
    local id = e.id
    local name, _, icon = GetSpellInfo(id)
    local lines = ReadTooltipLines(id)
    -- description = lignes du tooltip après le nom (concaténées)
    local desc = nil
    if lines and #lines > 0 then
      local startIdx = 1
      if name and lines[1] == name then startIdx = 2 end
      local parts = {}
      for i = startIdx, #lines do parts[#parts + 1] = lines[i] end
      desc = table.concat(parts, "\n")
      if name == nil then name = lines[1] end
    end
    EchoDumpDB.perks[id] = {
      name = name,
      desc = desc,
      icon = icon,
      quality = e.quality,
      classMask = e.classMask,
      groupId = e.groupId,
      minLevel = e.minLevel,
      tooltip = lines,
    }
    if name or desc then found = found + 1 else missing = missing + 1 end
  end
  EchoDumpDB.count = found

  -- SKILL TREE : scanner les sorts des noeuds (mêmes méthodes que les echoes)
  EchoDumpDB.skilltree = {}
  local stFound = 0
  for _, e in ipairs(SkillTree_Ids or {}) do
    local id = e.id
    if not EchoDumpDB.skilltree[id] then
      local name, _, icon = GetSpellInfo(id)
      local lines = ReadTooltipLines(id)
      local desc = nil
      if lines and #lines > 0 then
        local startIdx = 1
        if name and lines[1] == name then startIdx = 2 end
        local parts = {}
        for i = startIdx, #lines do parts[#parts + 1] = lines[i] end
        desc = table.concat(parts, "\n")
        if name == nil then name = lines[1] end
      end
      EchoDumpDB.skilltree[id] = {
        name = name, desc = desc, icon = icon,
        cost = e.cost, nodeId = e.nodeId, rank = e.rank, tooltip = lines,
      }
      if name or desc then stFound = stFound + 1 end
    end
  end
  EchoDumpDB.skilltreeCount = stFound

  -- AFFIXES : ProjectEbonhold.ExtractionService.learnedAffixes (peuplé après ouverture
  -- de l'Enclume Enchantée à Dalaran ; contient TOUS les affixes, learned ou non)
  EchoDumpDB.affixes = {}
  local afFound = 0
  -- ExtractionService est une GLOBALE top-level (pas un champ de ProjectEbonhold)
  local ES = _G.ExtractionService
  -- tente de demander la liste au serveur si possible (pour les fois suivantes)
  if ES and type(ES.RequestLearnedAffixes) == "function" then
    pcall(ES.RequestLearnedAffixes)
  end
  if ES and type(ES.learnedAffixes) == "table" then
    for _, af in ipairs(ES.learnedAffixes) do
      local id = af and af.id
      if id and not EchoDumpDB.affixes[id] then
        local name, _, icon = GetSpellInfo(id)
        local lines = ReadTooltipLines(id)
        local desc = nil
        if lines and #lines > 0 then
          local startIdx = 1
          if name and lines[1] == name then startIdx = 2 end
          local parts = {}
          for i = startIdx, #lines do parts[#parts + 1] = lines[i] end
          desc = table.concat(parts, "\n")
          if name == nil then name = lines[1] or af.name end
        end
        EchoDumpDB.affixes[id] = {
          name = name or af.name, desc = desc, icon = icon,
          weaponOnly = af.weaponOnly, difficulty = af.difficulty, tooltip = lines,
        }
        if name or desc then afFound = afFound + 1 end
      end
    end
  end
  EchoDumpDB.affixCount = afFound

  -- TOMES : tooltip des sorts "grant" (requiredSpell) = le texte "Use: Grants..." de l'objet
  EchoDumpDB.tomes = {}
  local tomeFound = 0
  for _, e in ipairs(Tome_Ids or {}) do
    local id = e.id
    if id and not EchoDumpDB.tomes[id] then
      local name, _, icon = GetSpellInfo(id)
      local lines = ReadTooltipLines(id)
      local desc = nil
      if lines and #lines > 0 then
        local startIdx = 1
        if name and lines[1] == name then startIdx = 2 end
        local parts = {}
        for i = startIdx, #lines do parts[#parts + 1] = lines[i] end
        desc = table.concat(parts, "\n")
        if name == nil then name = lines[1] end
      end
      EchoDumpDB.tomes[id] = { name = name, desc = desc, icon = icon, ref = e.ref, tooltip = lines }
      if name or desc then tomeFound = tomeFound + 1 end
    end
  end
  EchoDumpDB.tomeCount = tomeFound

  -- TOME ITEMS : scan via ScanTomeItems() (priming + item:id + sacs + banque).
  -- Un ticker (déclenché après le dump) ré-appelle ScanTomeItems pendant ~40s
  -- pour récupérer les données d'items qui arrivent du serveur en différé.
  local tiFound = ScanTomeItems()

  -- Capture des tables custom du serveur (echoes, SKILL TREE, affixes, etc.)
  -- Au lieu de deviner les noms, on explore toute la structure de ProjectEbonhold
  -- + les globales liées, et on dump tout ce qui est sérialisable.
  EchoDumpDB.server = {}
  EchoDumpDB.discovery = {}

  local function tcount(t)
    local n = 0; for _ in pairs(t) do n = n + 1 end; return n
  end

  if _G.ProjectEbonhold and type(_G.ProjectEbonhold) == "table" then
    local PE = _G.ProjectEbonhold
    local keys = {}
    for k, v in pairs(PE) do
      local tv = type(v)
      local info = tv
      if tv == "table" then info = "table(" .. tcount(v) .. ")" end
      keys[tostring(k)] = info
      -- dump toute table de taille raisonnable (skill tree, affixes, perks, etc.)
      if tv == "table" then
        local cnt = tcount(v)
        if cnt > 0 and cnt <= 5000 then
          EchoDumpDB.server[tostring(k)] = SafeCopy(v, 0)
        end
      end
    end
    EchoDumpDB.discovery.ProjectEbonholdKeys = keys
  end

  -- Scan des globales dont le nom évoque echoes / skill tree / affixes
  local g = {}
  for name, v in pairs(_G) do
    if type(name) == "string" then
      local low = name:lower()
      if (low:find("ebonhold") or low:find("perk") or low:find("skilltree")
          or low:find("soulash") or low:find("node") or low:find("affix")
          or low:find("extraction") or low:find("echo")) and type(v) == "table" then
        g[name] = "table(" .. tcount(v) .. ")"
        -- dump les globales pertinentes de taille raisonnable, hors UI frames
        local cnt = tcount(v)
        if cnt > 0 and cnt <= 5000 and not EchoDumpDB.server[name] then
          EchoDumpDB.server[name] = SafeCopy(v, 0)
        end
      end
    end
  end
  EchoDumpDB.discovery.globalsMatching = g
  msg("Structure serveur explorée (voir EchoDumpDB.discovery + .server).")

  msg(string.format("Terminé : |cff55d38a%d|r echoes + |cff55d38a%d|r skill tree + |cff55d38a%d|r affixes + |cff55d38a%d|r tomes (|cff55d38a%d|r objets tomes).", found, stFound, afFound, tomeFound, tiFound))
  if afFound == 0 then
    msg("|cffffd200Astuce affixes :|r ouvre l'Enclume Enchantée (Dalaran) puis refais /echodump pour les capturer.")
  end
  msg("Tape maintenant |cffffd200/reload|r puis envoie le fichier SavedVariables/EchoDumpDB.lua")
end

-- Ticker : ré-appelle ScanTomeItems toutes les 3s pendant ~45s, le temps que le
-- serveur renvoie les données des items tomes non possédés (suite au priming).
local tomeTicker = CreateFrame("Frame")
local function StartTomeTicker()
  tomeTicker._t = 0
  tomeTicker._iter = 0
  tomeTicker._last = EchoDumpDB.tomeItemCount or 0
  tomeTicker:SetScript("OnUpdate", function(self, elapsed)
    self._t = self._t + elapsed
    if self._t < 3 then return end
    self._t = 0
    self._iter = self._iter + 1
    local n = ScanTomeItems()
    if n ~= self._last then
      msg(string.format("Tomes en cache : |cff55d38a%d|r / 128 (continue...)", n))
      self._last = n
    end
    if n >= 128 or self._iter >= 15 then
      self:SetScript("OnUpdate", nil)
      msg(string.format("Scan tomes terminé : |cff55d38a%d|r / 128 objets. Tape |cffffd200/reload|r.", n))
    end
  end)
end

SLASH_ECHODUMP1 = "/echodump"
SlashCmdList["ECHODUMP"] = function()
  msg("Scan en cours (echoes + skill tree + structure serveur)...")
  DoDump(true)
  StartTomeTicker()
  msg("|cffffd200Priming des tomes en cours (~45s)...|r reste connecté, attends la fin puis /reload.")
end

local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_LOGIN")
f:SetScript("OnEvent", function()
  msg("Chargé. Tape |cffffd200/echodump|r pour exporter les echoes (puis /reload).")
end)
