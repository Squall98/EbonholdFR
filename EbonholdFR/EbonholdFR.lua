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
local affixEffectFR = D.affixEffectFR or {}
local affixDescFR = D.affixDescFR or {}
local tomeFR = D.tomeFR or {}
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
  if not e then return end
  -- nœuds de skill tree : e.sdesc ; echoes (liens chat / shift-click) : e.desc (template, tokens littéraux)
  local frDesc = e.sdesc or e.desc
  if not frDesc then return end
  local nm = tt:GetName()
  if not nm then return end
  local l2 = _G[nm .. "TextLeft2"]
  if l2 then l2:SetText(frDesc) end
  -- vide les lignes de description restantes (3..N) : à ce stade ce sont
  -- uniquement des suites de description (le coût est ajouté APRÈS le hook)
  local n = tt:NumLines() or 0
  for i = 3, n do
    local li = _G[nm .. "TextLeft" .. i]
    if li and li:GetText() and li:GetText() ~= "" then li:SetText(" ") end
  end
  tt:Show()
end

------------------------------------------------------------------------
-- 3) OBJETS : affixes gravés (ligne violette) + Tomes of Echo
--    via OnTooltipSetItem (couvre survol sac/équipé ET liens chat).
------------------------------------------------------------------------
local STACK_EN = ". Stacks with other ranks."
local STACK_FR = ". Se cumule avec les autres rangs."

local function stripColor(s)
  if not s then return s end
  s = string.gsub(s, "|c%x%x%x%x%x%x%x%x", "")
  s = string.gsub(s, "|r", "")
  return s
end

local function frAffixEffect(plain)
  -- gère le suffixe " Stacks with other ranks." puis cherche l'effet
  local body, suffix = plain, ""
  if string.sub(plain, -string.len(STACK_EN)) == STACK_EN then
    body = string.sub(plain, 1, string.len(plain) - string.len(STACK_EN))
    suffix = STACK_FR
  end
  local fr = affixEffectFR[body]
  if not fr then
    local noDot = string.gsub(body, "%.$", "")
    fr = affixEffectFR[noDot]
  end
  if fr then return fr .. suffix end
  return nil
end

local function translateItemTooltip(tt)
  local nm = tt:GetName()
  if not nm then return end
  local l1 = _G[nm .. "TextLeft1"]
  local title = l1 and l1:GetText()
  local tomeName = title and string.match(title, "^Tome of Echo: (.+)$")
  local n = tt:NumLines() or 0
  local changed = false
  for i = 2, n do
    local fs = _G[nm .. "TextLeft" .. i]
    local raw = fs and fs:GetText()
    if raw and raw ~= "" then
      local plain = stripColor(raw)
      -- a) ligne d'affixe gravé
      local frEff = frAffixEffect(plain)
      if frEff then
        fs:SetText(frEff); changed = true
      elseif tomeName then
        -- b) lignes de Tome of Echo
        if string.find(plain, "when offered new Echoes", 1, true) then
          local full = tomeFR[tomeName]
          if full then
            -- ligne FR complète (enrobage + blurb traduit), nom de l'echo en anglais
            fs:SetText(full); changed = true
          else
            -- repli : on traduit juste l'enrobage par regex (blurb laissé en anglais)
            local t = string.gsub(raw, "Use: ", "Utiliser : ")
            t = string.gsub(t,
              "Grants this character the ability to discover (.-) when offered new Echoes%.",
              "Permet \195\160 ce personnage de d\195\169couvrir %1 parmi les Echoes propos\195\169s.")
            if t ~= raw then fs:SetText(t); changed = true end
          end
        elseif plain == "Binds when used" then
          fs:SetText("Li\195\169 quand utilis\195\169"); changed = true
        end
      end
    end
  end
  if changed then tt:Show() end
end

local hookedItem = {}
local function hookItemTooltip(frameName)
  if hookedItem[frameName] then return true end
  local f = _G[frameName]
  if not f or type(f.HookScript) ~= "function" then return false end
  f:HookScript("OnTooltipSetItem", translateItemTooltip)
  hookedItem[frameName] = true
  return true
end

------------------------------------------------------------------------
-- 4) SORTS (grimoire / spellbook) : affixes affichés via OnTooltipSetSpell.
--    On essaie l'id direct (byId) puis le match texte (affixDescFR).
------------------------------------------------------------------------
local function translateSpellTooltip(tt)
  local nm = tt:GetName()
  if not nm then return end
  -- essai 1 : id du sort
  local _, _, id = tt:GetSpell()
  local e = id and byId[id]
  if e and (e.sdesc or e.desc) then
    local l2 = _G[nm .. "TextLeft2"]
    if l2 then l2:SetText(e.sdesc or e.desc) end
    local n = tt:NumLines() or 0
    for i = 3, n do
      local li = _G[nm .. "TextLeft" .. i]
      if li and li:GetText() and li:GetText() ~= "" then li:SetText(" ") end
    end
    tt:Show()
    return
  end
  -- essai 2 : match de la description complète (affixes)
  local n = tt:NumLines() or 0
  local changed = false
  for i = 2, n do
    local fs = _G[nm .. "TextLeft" .. i]
    local raw = fs and fs:GetText()
    if raw and raw ~= "" then
      local fr = affixDescFR[stripColor(raw)]
      if fr then fs:SetText(fr); changed = true end
    end
  end
  if changed then tt:Show() end
end

local hookedSpell = {}
local function hookSpellTooltip(frameName)
  if hookedSpell[frameName] then return true end
  local f = _G[frameName]
  if not f or type(f.HookScript) ~= "function" then return false end
  f:HookScript("OnTooltipSetSpell", translateSpellTooltip)
  hookedSpell[frameName] = true
  return true
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
  -- tooltips d'objets (affixes gravés + tomes)
  hookItemTooltip("GameTooltip")
  hookItemTooltip("ItemRefTooltip")
  hookItemTooltip("ShoppingTooltip1")
  hookItemTooltip("ShoppingTooltip2")
  -- tooltips de sorts (grimoire : affixes via OnTooltipSetSpell)
  hookSpellTooltip("GameTooltip")
  hookSpellTooltip("ItemRefTooltip")
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
