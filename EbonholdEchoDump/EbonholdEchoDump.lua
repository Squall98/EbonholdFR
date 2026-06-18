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
          or low:find("echo")) and type(v) == "table" then
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

  msg(string.format("Terminé : |cff55d38a%d|r echoes + |cff55d38a%d|r noeuds skill tree.", found, stFound))
  msg("Tape maintenant |cffffd200/reload|r puis envoie le fichier SavedVariables/EchoDumpDB.lua")
end

SLASH_ECHODUMP1 = "/echodump"
SlashCmdList["ECHODUMP"] = function()
  msg("Scan en cours (echoes + skill tree + structure serveur)...")
  DoDump(true)
end

local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_LOGIN")
f:SetScript("OnEvent", function()
  msg("Chargé. Tape |cffffd200/echodump|r pour exporter les echoes (puis /reload).")
end)
