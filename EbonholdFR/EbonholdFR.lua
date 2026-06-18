--[[ EbonholdFR — traduction française des DESCRIPTIONS de Project Ebonhold.
  Les NOMS restent en anglais (volontaire). Seules les descriptions passent en FR.
    * Echoes      : descriptions via utils.GetSpellDescription (tokens @..@)
                    -> hook : on réinjecte le template FR avec les nombres calculés.
    * Skill Tree  : tooltips custom (skillTreeCurrentRankTooltip / NextRank) via
                    SetHyperlink('spell:id') -> hook : on remplace la description
                    (lignes 2+) par la version FR statique (e.sdesc).
  Données : EbonholdFR_Data.lua  (byId[spellId] = { desc=... } ou { sdesc=... }).
  Commande : /frtest <spellId>
]]

local D = EbonholdFR_Data or {}
local byId = D.byId or {}
local function msg(s) DEFAULT_CHAT_FRAME:AddMessage("|cff9966ff[EbonholdFR]|r " .. s) end

------------------------------------------------------------------------
-- 1) ECHOES : descriptions tokenisées (utils.GetSpellDescription global)
------------------------------------------------------------------------
-- remplit le template FR avec les nombres verts (|cff2cfe32..|r) calculés par l'original
local function reinject(fr, enText, maxLength)
  if string.find(fr, "@") then
    local nums = {}
    for v in string.gmatch(enText, "|cff2cfe32(.-)|r") do nums[#nums + 1] = v end
    local i = 0
    fr = string.gsub(fr, "@(.-)@", function()
      i = i + 1
      return "|cff2cfe32" .. (nums[i] or "") .. "|r"
    end)
  end
  if maxLength and string.len(fr) > maxLength then
    fr = string.sub(fr, 1, maxLength - 3) .. "..."
  end
  return fr
end

local function installDescHook()
  if type(utils) ~= "table" or type(utils.GetSpellDescription) ~= "function" then
    return false
  end
  if utils._ebonholdFRHooked then return true end
  utils._ebonholdFRHooked = true
  -- 1a) description simple (browser)
  local orig = utils.GetSpellDescription
  utils.GetSpellDescription = function(spellId, maxLength, stacks)
    local e = byId[spellId]
    if e and e.desc then
      return reinject(e.desc, orig(spellId, maxLength, stacks), maxLength)
    end
    return orig(spellId, maxLength, stacks)
  end
  -- 1b) description cumulée (panneau d'echoes équipés en jeu)
  if type(utils.GetStackedSpellDescription) == "function" then
    local origStk = utils.GetStackedSpellDescription
    utils.GetStackedSpellDescription = function(spellInstances, maxLength)
      local sid = spellInstances and spellInstances[1] and spellInstances[1].spellId
      local e = sid and byId[sid]
      if e and e.desc then
        return reinject(e.desc, origStk(spellInstances, maxLength), maxLength)
      end
      return origStk(spellInstances, maxLength)
    end
  end
  return true
end

------------------------------------------------------------------------
-- 2) SKILL TREE : remplace la description (lignes 2+) par e.sdesc
--    (le hook se déclenche juste après SetHyperlink, avant l'ajout du coût)
------------------------------------------------------------------------
local function fixSkillTooltip(tt, link)
  if not tt or not link then return end
  local id = tonumber(string.match(tostring(link), "spell:(%d+)"))
  if not id then return end
  local e = byId[id]
  if not e or not e.sdesc then return end
  local nm = tt:GetName()
  if not nm then return end
  local l2 = _G[nm .. "TextLeft2"]
  if l2 then l2:SetText(e.sdesc) end
  -- vide les lignes de description restantes (3..N) : à ce stade ce sont
  -- uniquement des suites de description (le coût est ajouté APRÈS le hook)
  local n = tt:NumLines() or 0
  for i = 3, n do
    local li = _G[nm .. "TextLeft" .. i]
    if li and li:GetText() and li:GetText() ~= "" then li:SetText(" ") end
  end
  tt:Show()
end

local hookedFrames = {}
local function hookTooltipFrame(frameName)
  if hookedFrames[frameName] then return true end
  local f = _G[frameName]
  if not f or type(f.SetHyperlink) ~= "function" then return false end
  hooksecurefunc(f, "SetHyperlink", function(self, link) fixSkillTooltip(self, link) end)
  hookedFrames[frameName] = true
  return true
end

------------------------------------------------------------------------
-- Initialisation
------------------------------------------------------------------------
local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_LOGIN")
f:SetScript("OnEvent", function()
  -- tooltips toujours présents
  hookTooltipFrame("GameTooltip")
  hookTooltipFrame("ItemRefTooltip")
  -- les tooltips du skill tree n'existent qu'après chargement du module :
  -- on réessaie pendant quelques secondes + après ouverture de l'arbre.
  local tries = 0
  local ticker = CreateFrame("Frame")
  ticker:SetScript("OnUpdate", function(self, elapsed)
    self._t = (self._t or 0) + elapsed
    if self._t < 1 then return end
    self._t = 0
    tries = tries + 1
    installDescHook()
    hookTooltipFrame("skillTreeCurrentRankTooltip")
    hookTooltipFrame("skillTreeNextRankTooltip")
    local doneSkill = hookedFrames["skillTreeCurrentRankTooltip"] and hookedFrames["skillTreeNextRankTooltip"]
    if (utils and utils._ebonholdFRHooked and doneSkill) or tries > 30 then
      self:SetScript("OnUpdate", nil)
      local n = 0; for _ in pairs(byId) do n = n + 1 end
      msg("Traduction active (" .. n .. " descriptions). Echoes:" ..
        tostring(utils and utils._ebonholdFRHooked or false) ..
        " SkillTree:" .. tostring(doneSkill or false))
    end
  end)
end)

SLASH_FRTEST1 = "/frtest"
SlashCmdList["FRTEST"] = function(arg)
  local id = tonumber(arg)
  if id and byId[id] then
    msg("spell " .. id .. " -> " .. tostring(byId[id].desc or byId[id].sdesc))
  else
    local n = 0; for _ in pairs(byId) do n = n + 1 end
    msg("Entrées : " .. n .. ". /frtest <spellId>")
  end
end
