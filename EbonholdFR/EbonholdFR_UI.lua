--[[ EbonholdFR_UI — bouton minimap + panneau d'options (V3).
  Fonction phare : basculer la traduction FR <-> EN (texte original) à la volée,
  globalement ou par catégorie (Echoes / Skill Tree / Affixes / Tomes).
  Les réglages sont lus en direct par les hooks de EbonholdFR.lua (trOn).
]]

local function msg(s) DEFAULT_CHAT_FRAME:AddMessage("|cff9966ff[EbonholdFR]|r " .. s) end

local DB           -- réglages sauvegardés (EbonholdFRDB)
local button       -- bouton minimap
local panel        -- panneau d'options
local RADIUS = 80  -- rayon de placement autour de la minimap

------------------------------------------------------------------------
-- Bouton minimap (déplaçable autour du cercle, position sauvegardée)
------------------------------------------------------------------------
local function updateButtonPos()
  local a = math.rad(DB.minimap.angle or 200)
  button:SetPoint("CENTER", Minimap, "CENTER", RADIUS * math.cos(a), RADIUS * math.sin(a))
end

-- l'icône se grise quand la traduction est désactivée (mode anglais)
local function updateButtonState()
  if button and button.icon then button.icon:SetDesaturated(not DB.enabled) end
end

local function dragOnUpdate(self)
  local mx, my = Minimap:GetCenter()
  local scale = Minimap:GetEffectiveScale()
  local px, py = GetCursorPosition()
  px, py = px / scale, py / scale
  DB.minimap.angle = math.deg(math.atan2(py - my, px - mx))
  updateButtonPos()
end

local function buttonTooltip(self)
  GameTooltip:SetOwner(self, "ANCHOR_LEFT")
  GameTooltip:AddLine("Ebonhold |cff66ccffFR|r")
  if DB.enabled then
    GameTooltip:AddLine("\195\137tat : |cff2cfe32Fran\195\167ais actif|r", 1, 1, 1)
  else
    GameTooltip:AddLine("\195\137tat : |cffff6666Anglais (original)|r", 1, 1, 1)
  end
  GameTooltip:AddLine("Clic gauche : ouvrir les options", 0.7, 0.7, 0.7)
  GameTooltip:AddLine("Clic droit : basculer FR / EN", 0.7, 0.7, 0.7)
  GameTooltip:Show()
end

local function createButton()
  button = CreateFrame("Button", "EbonholdFRMinimapButton", Minimap)
  button:SetFrameStrata("MEDIUM")
  button:SetWidth(31); button:SetHeight(31)
  button:SetFrameLevel(8)
  button:RegisterForClicks("LeftButtonUp", "RightButtonUp")
  button:RegisterForDrag("LeftButton")

  local overlay = button:CreateTexture(nil, "OVERLAY")
  overlay:SetWidth(53); overlay:SetHeight(53)
  overlay:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
  overlay:SetPoint("TOPLEFT")

  local icon = button:CreateTexture(nil, "BACKGROUND")
  icon:SetWidth(20); icon:SetHeight(20)
  icon:SetTexture("Interface\\Icons\\INV_Misc_Book_07")
  icon:SetPoint("TOPLEFT", 7, -6)
  button.icon = icon

  button:SetScript("OnClick", function(self, btn)
    if btn == "RightButton" then
      DB.enabled = not DB.enabled
      updateButtonState()
      if EbonholdFR_RefreshPanel then EbonholdFR_RefreshPanel() end
      buttonTooltip(self)
      msg(DB.enabled and "Traduction |cff2cfe32fran\195\167aise|r activ\195\169e."
                      or "Traduction d\195\169sactiv\195\169e : textes en |cffff6666anglais|r.")
    else
      if panel and panel:IsShown() then panel:Hide() else EbonholdFR_OpenPanel() end
    end
  end)
  button:SetScript("OnDragStart", function(self) self:SetScript("OnUpdate", dragOnUpdate) end)
  button:SetScript("OnDragStop", function(self) self:SetScript("OnUpdate", nil) end)
  button:SetScript("OnEnter", buttonTooltip)
  button:SetScript("OnLeave", function() GameTooltip:Hide() end)

  updateButtonPos()
  updateButtonState()
  if DB.minimap.hide then button:Hide() end
end

------------------------------------------------------------------------
-- Panneau d'options
------------------------------------------------------------------------
local CATS = {
  { key = "echoes",    label = "Echoes (descriptions)" },
  { key = "skilltree", label = "Skill Tree (arbre de talents)" },
  { key = "affixes",   label = "Affixes (objets, grimoire)" },
  { key = "tomes",     label = "Tomes of Echo" },
}

local masterCheck, catChecks = nil, {}

-- met à jour l'état visuel des cases selon DB
function EbonholdFR_RefreshPanel()
  if not panel then return end
  masterCheck:SetChecked(DB.enabled)
  for _, c in ipairs(catChecks) do
    c:SetChecked(DB.cat[c.key])
    if DB.enabled then c:Enable(); c.text:SetTextColor(1, 1, 1)
    else c:Disable(); c.text:SetTextColor(0.5, 0.5, 0.5) end
  end
end

local function makeCheck(parent, label, x, y)
  local cb = CreateFrame("CheckButton", nil, parent, "UICheckButtonTemplate")
  cb:SetWidth(26); cb:SetHeight(26)
  cb:SetPoint("TOPLEFT", x, y)
  cb.text = cb:CreateFontString(nil, "ARTWORK", "GameFontNormal")
  cb.text:SetPoint("LEFT", cb, "RIGHT", 2, 0)
  cb.text:SetText(label)
  return cb
end

local function createPanel()
  panel = CreateFrame("Frame", "EbonholdFROptionsPanel", UIParent)
  panel:SetWidth(330); panel:SetHeight(310)
  panel:SetPoint("CENTER")
  panel:SetFrameStrata("DIALOG")
  panel:SetBackdrop({
    bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
    edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
    tile = true, tileSize = 32, edgeSize = 32,
    insets = { left = 11, right = 12, top = 12, bottom = 11 },
  })
  panel:EnableMouse(true)
  panel:SetMovable(true)
  panel:RegisterForDrag("LeftButton")
  panel:SetScript("OnDragStart", panel.StartMoving)
  panel:SetScript("OnDragStop", panel.StopMovingOrSizing)
  panel:Hide()

  local title = panel:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
  title:SetPoint("TOP", 0, -18)
  title:SetText("Ebonhold |cff66ccffFR|r  —  Options")

  local close = CreateFrame("Button", nil, panel, "UIPanelCloseButton")
  close:SetPoint("TOPRIGHT", -6, -6)

  -- interrupteur maître
  masterCheck = makeCheck(panel, "|cffffd100Traduction fran\195\167aise|r", 20, -52)
  masterCheck.text:SetFontObject("GameFontHighlight")
  masterCheck:SetScript("OnClick", function(self)
    DB.enabled = self:GetChecked() and true or false
    EbonholdFR_RefreshPanel()
    if button then button.icon:SetDesaturated(not DB.enabled) end
  end)
  local sub = panel:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
  sub:SetPoint("TOPLEFT", 44, -76)
  sub:SetText("D\195\169coch\195\169 = textes d'origine en anglais.")

  -- cases par catégorie
  local y = -104
  for _, info in ipairs(CATS) do
    local cb = makeCheck(panel, info.label, 40, y)
    cb.key = info.key
    cb:SetScript("OnClick", function(self)
      DB.cat[self.key] = self:GetChecked() and true or false
    end)
    catChecks[#catChecks + 1] = cb
    y = y - 28
  end

  -- bouton recharger l'interface
  local reload = CreateFrame("Button", nil, panel, "UIPanelButtonTemplate")
  reload:SetWidth(200); reload:SetHeight(24)
  reload:SetPoint("TOP", 0, y - 8)
  reload:SetText("Recharger l'interface (/reload)")
  reload:SetScript("OnClick", function() ReloadUI() end)
  local rhint = panel:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
  rhint:SetPoint("TOP", reload, "BOTTOM", 0, -3)
  rhint:SetText("Pour appliquer aux fen\195\170tres d\195\169j\195\160 ouvertes.")

  -- pied : version + teaser + crédit
  local foot = panel:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
  foot:SetPoint("BOTTOM", 0, 16)
  foot:SetText("v3.0  •  une autre Echo sommeille encore...  •  par Squall98")

  EbonholdFR_RefreshPanel()
  if button then button.icon:SetDesaturated(not DB.enabled) end
end

function EbonholdFR_OpenPanel()
  if not panel then createPanel() end
  EbonholdFR_RefreshPanel()
  panel:Show()
end

------------------------------------------------------------------------
-- Initialisation
------------------------------------------------------------------------
local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_LOGIN")
f:SetScript("OnEvent", function()
  DB = EbonholdFR.EnsureDB()
  createButton()
end)

-- /frmenu : ouvre/ferme le panneau ; /frbouton : affiche/masque le bouton minimap
SLASH_FRMENU1 = "/frmenu"
SlashCmdList["FRMENU"] = function()
  if panel and panel:IsShown() then panel:Hide() else EbonholdFR_OpenPanel() end
end

SLASH_FRBOUTON1 = "/frbouton"
SlashCmdList["FRBOUTON"] = function()
  DB.minimap.hide = not DB.minimap.hide
  if DB.minimap.hide then button:Hide(); msg("Bouton minimap masqu\195\169 (/frbouton pour le r\195\169afficher).")
  else button:Show(); msg("Bouton minimap affich\195\169.") end
end
