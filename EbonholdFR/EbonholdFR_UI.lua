--[[ EbonholdFR_UI — bouton minimap + panneau d'options (v4).
  Les réglages viennent du launcher (EbonholdFR_Reglages.lua) ; ce panneau permet de les changer
  en jeu (mémorisé dans EbonholdFRDB). Clic droit sur le bouton : tout en anglais / tout en français.
]]

local E = EbonholdFR
local function msg(s) E.msg(s) end

local DB           -- EbonholdFRDB
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
  GameTooltip:AddLine("Ebonhold |cff66ccffFR|r " .. E.version)
  if DB.enabled then
    GameTooltip:AddLine("\195\137tat : |cff2cfe32Fran\195\167ais actif|r", 1, 1, 1)
  else
    GameTooltip:AddLine("\195\137tat : |cffff6666Anglais (original)|r", 1, 1, 1)
  end
  if E.Patch() then
    GameTooltip:AddLine("Patch FR install\195\169 : descriptions d\195\169j\195\160 en fran\195\167ais", 0.6, 0.8, 1)
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
      E.Rafraichir()
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
local OPTIONS = {
  { key = "interface",     label = "Interface du serveur (fen\195\170tres, boutons)" },
  { key = "echoes_desc",   label = "Echoes (descriptions)",                    desc = true },
  { key = "soultree_desc", label = "Soul Tree (descriptions)",                 desc = true },
  { key = "affixes_desc",  label = "Affixes (objets, grimoire)",               desc = true },
  { key = "tomes",         label = "Tomes of Echo",                            desc = true },
  { key = "nom_anglais",   label = "Afficher aussi le nom anglais (EN : ...)" },
}

local masterCheck, optChecks, patchNote = nil, {}, nil

-- met à jour l'état visuel des cases selon les réglages
function EbonholdFR_RefreshPanel()
  if not panel then return end
  masterCheck:SetChecked(DB.enabled)
  local patch = E.Patch()
  for _, c in ipairs(optChecks) do
    c:SetChecked(E.ValeurReglage(c.key) and true or false)
    local grise = (not DB.enabled) or (patch and c.desc)
    if grise then c:Disable(); c.text:SetTextColor(0.5, 0.5, 0.5)
    else c:Enable(); c.text:SetTextColor(1, 1, 1) end
  end
  if patch then patchNote:Show() else patchNote:Hide() end
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
  panel:SetWidth(360); panel:SetHeight(390)
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
  tinsert(UISpecialFrames, "EbonholdFROptionsPanel")   -- Échap ferme le panneau

  local title = panel:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
  title:SetPoint("TOP", 0, -18)
  title:SetText("Ebonhold |cff66ccffFR|r  \226\128\148  Options")

  local close = CreateFrame("Button", nil, panel, "UIPanelCloseButton")
  close:SetPoint("TOPRIGHT", -6, -6)

  -- interrupteur général
  masterCheck = makeCheck(panel, "|cffffd100Traduction fran\195\167aise|r", 20, -48)
  masterCheck.text:SetFontObject("GameFontHighlight")
  masterCheck:SetScript("OnClick", function(self)
    DB.enabled = self:GetChecked() and true or false
    E.Rafraichir()
    EbonholdFR_RefreshPanel()
    updateButtonState()
  end)
  local sub = panel:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
  sub:SetPoint("TOPLEFT", 44, -72)
  sub:SetText("D\195\169coch\195\169 = textes d'origine en anglais.")

  -- une case par réglage
  local y = -96
  for _, info in ipairs(OPTIONS) do
    local cb = makeCheck(panel, info.label, 40, y)
    cb.key, cb.desc = info.key, info.desc
    cb:SetScript("OnClick", function(self)
      E.SetChoix(self.key, self:GetChecked())
      EbonholdFR_RefreshPanel()
    end)
    optChecks[#optChecks + 1] = cb
    y = y - 26
  end

  patchNote = panel:CreateFontString(nil, "ARTWORK", "GameFontNormalSmall")
  patchNote:SetPoint("TOPLEFT", 44, y - 2)
  patchNote:SetWidth(290)
  patchNote:SetJustifyH("LEFT")
  patchNote:SetText("|cff99ccffPatch FR install\195\169 : les descriptions sont d\195\169j\195\160 en fran\195\167ais dans le jeu.|r")
  y = y - 30

  -- revenir aux réglages du launcher
  local reset = CreateFrame("Button", nil, panel, "UIPanelButtonTemplate")
  reset:SetWidth(240); reset:SetHeight(22)
  reset:SetPoint("TOP", 0, y)
  reset:SetText("Reprendre les r\195\169glages du launcher")
  reset:SetScript("OnClick", function()
    E.RevenirLauncher()
    EbonholdFR_RefreshPanel()
    updateButtonState()
    msg("R\195\169glages du launcher repris.")
  end)

  -- recharger l'interface
  local reload = CreateFrame("Button", nil, panel, "UIPanelButtonTemplate")
  reload:SetWidth(240); reload:SetHeight(22)
  reload:SetPoint("TOP", reset, "BOTTOM", 0, -6)
  reload:SetText("Recharger l'interface (/reload)")
  reload:SetScript("OnClick", function() ReloadUI() end)
  local rhint = panel:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
  rhint:SetPoint("TOP", reload, "BOTTOM", 0, -3)
  rhint:SetText("Pour appliquer aux fen\195\170tres d\195\169j\195\160 ouvertes.")

  -- pied : version (lue dans le .toc) + crédit
  local foot = panel:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
  foot:SetPoint("BOTTOM", 0, 16)
  foot:SetText("v" .. E.version .. "  \226\128\162  une autre Echo sommeille encore...  \226\128\162  par Squall98")

  EbonholdFR_RefreshPanel()
  updateButtonState()
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
  DB = E.EnsureDB()
  createButton()
end)

local function basculerPanneau()
  if not DB then DB = E.EnsureDB() end
  if panel and panel:IsShown() then panel:Hide() else EbonholdFR_OpenPanel() end
end

local function basculerBouton()
  if not DB or not button then return end
  DB.minimap.hide = not DB.minimap.hide
  if DB.minimap.hide then button:Hide(); msg("Bouton minimap masqu\195\169 (/efr bouton pour le r\195\169afficher).")
  else button:Show(); msg("Bouton minimap affich\195\169.") end
end

E.Commandes = E.Commandes or {}
E.Commandes.menu = basculerPanneau
E.Commandes.options = basculerPanneau
E.Commandes.bouton = basculerBouton

-- anciens alias : /frmenu ouvre/ferme le panneau ; /frbouton affiche/masque le bouton minimap
SLASH_FRMENU1 = "/frmenu"
SlashCmdList["FRMENU"] = basculerPanneau
SLASH_FRBOUTON1 = "/frbouton"
SlashCmdList["FRBOUTON"] = basculerBouton
